# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from collections import namedtuple

import aiokubernetes as k8s

# All API responses will be wrapped into this tuple.
# The `name` will be 'ADDED', MODIFIED, etc, `raw` will the unprocessed but
# Json decoded response from K8s and `obj` will be the Swagger object created
# from `raw` (may be None if there was an error).
WatchResponse = namedtuple('WatchResponse', 'name raw obj')


class Watch2(object):

    def __init__(self, request):
        self.request = request
        self.connection = None
        self._stop = False

    def __aiter__(self):
        return self

    async def __anext__(self):
        # Set the response object to the user supplied function (eg
        # `list_namespaced_pods`) if this is the first iteration.
        if self.connection is None:
            self.connection = await self.request

        # Abort at the current iteration if the user has called `stop` on this
        # stream instance.
        if self._stop:
            raise StopAsyncIteration

        # Fetch the next K8s response. This is where the callee's async
        # iterator will yield until K8s sends another Http chunk through the
        # connection.
        line = await self.connection.content.readline()

        # Stop the iterator if K8s sends an empty response. This happens when
        # eg the supplied timeout has expired.
        if len(line) == 0:
            raise StopAsyncIteration

        return self.unmarshal_event(line)

    def stop(self):
        self._stop = True

    @staticmethod
    def unmarshal_event(data: bytes):
        """Return the K8s response `data` in a `WatchResponse` tuple.

        """
        try:
            line = data.decode('utf8')
            js = json.loads(line)

            # Unpack the watched event and extract the event name (ADDED, MODIFIED,
            # etc) and the raw event content.
            name, k8s_obj = js['type'], js['object']
        except UnicodeDecodeError:
            # fixup: log message
            print('unicode error')
            return WatchResponse(name=None, raw=data, obj=None)
        except json.decoder.JSONDecodeError:
            # fixup: log message
            print('json error')
            return WatchResponse(name=None, raw=data, obj=None)
        except KeyError:
            print('key error')
            # fixup: log message
            return WatchResponse(name=None, raw=data, obj=None)

        klass = k8s.swagger.determine_type(k8s_obj['apiVersion'], k8s_obj['kind'])

        # Something went wrong. A typical example would be that the user
        # supplied a resource version that was too old. In that case K8s would
        # not send a conventional ADDED/DELETED/... event but an error.
        if name.lower() == 'error' or klass is None:
            return WatchResponse(name=name, raw=data, obj=None)

        # De-serialise the K8s response and return everything.
        obj = k8s.swagger.deserialize(data=k8s_obj, klass=klass)
        return WatchResponse(name=name, raw=data, obj=obj)
