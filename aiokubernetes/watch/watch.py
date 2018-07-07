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

import functools
import json
import pydoc
from collections import namedtuple

import aiokubernetes as k8s

# All API responses will be wrapped into this tuple.
# The `name` will be 'ADDED', MODIFIED, etc, `raw` will the unprocessed but
# Json decoded response from K8s and `obj` will be the Swagger object created
# from `raw` (may be None if there was an error).
WatchResponse = namedtuple('WatchResponse', 'name raw obj')


def _find_return_type(func):
    """Return the K8s response type as a string, eg `V1Namespace`.

    Return None if the return type was not in the doc string of `func`.

    Raise `AssertionError` if the doc string was ambiguous.

    NOTE: this function _assumes_ the doc strings have a certain type.
    """
    # Find all the lines that mention the return type.
    lines = [_ for _ in pydoc.getdoc(func).splitlines() if _.startswith(":return:")]

    # Return None if the doc string does not mention a return type (user
    # probably specified an invalid function; would be good to catch at some
    # point).
    if len(lines) == 0:
        return None

    # Raise an exception if we could not unambiguously determine the return type.
    assert len(lines) == 1, 'Unable to determine return type for {}'.format(func)

    # Strip the leading ':return:' and trailing 'List' string to extract the
    # correct type name.
    line = lines[0]
    rtype = line.partition(":return:")[2].strip()
    rtype = rtype.rpartition("List")[0].strip()
    return rtype


class Watch(object):

    def __init__(self, api_func, *args, **kwargs):
        """Watch an API resource and stream the result back via a generator.

        :param api_func: The API function pointer, for instance,
                     CoreV1Api().list_namespace`. Any parameter to the function
                     can be passed after this parameter.

        :return: Event object with these keys:
                   'type': The type of event such as "ADDED", "DELETED", etc.
                   'raw_object': a dict representing the watched object.
                   'object': A model representation of raw_object. The name of
                             model will be determined based on
                             the api_func's doc string. If it cannot be
                             determined, 'object' value will be the same as
                             'raw_object'.

        Example:
            v1 = kubernetes_asyncio.client.CoreV1Api()
            watch = kubernetes_asyncio.watch.Watch()
            async for e in watch.stream(v1.list_namespace, timeout_seconds=10):
                type = e['type']
                object = e['object']  # object is one of type return_type
                raw_object = e['raw_object']  # raw_object is a dict
                ...
                if should_stop:
                    watch.stop()

        """
        self._api_client = api_func.__self__.api_client
        self._stop = False

        # Make this more explicit and cover with a test.
        self.return_type = _find_return_type(api_func)
        kwargs['watch'] = True
        kwargs['_preload_content'] = False

        self.api_func = functools.partial(api_func, *args, **kwargs)
        self.connection = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        # Set the response object to the user supplied function (eg
        # `list_namespaced_pods`) if this is the first iteration.
        if self.connection is None:
            tmp = await self.api_func()
            self.connection = tmp.http.content
            del tmp

        # Abort at the current iteration if the user has called `stop` on this
        # stream instance.
        if self._stop:
            raise StopAsyncIteration

        # Fetch the next K8s response. This is where the callee's async
        # iterator will yield until K8s sends another Http chunk through the
        # connection.
        line = await self.connection.readline()

        # Stop the iterator if K8s sends an empty response. This happens when
        # eg the supplied timeout has expired.
        if len(line) == 0:
            raise StopAsyncIteration

        return self.unmarshal_event(line, self.return_type)

    def stop(self):
        self._stop = True

    @staticmethod
    def unmarshal_event(data: bytes, response_type):
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
            return WatchResponse(name=None, raw=data, obj=None)
        except json.decoder.JSONDecodeError:
            # fixup: log message
            return WatchResponse(name=None, raw=data, obj=None)
        except KeyError:
            # fixup: log message
            return WatchResponse(name=None, raw=data, obj=None)

        # Something went wrong. A typical example would be that the user
        # supplied a resource version that was too old. In that case K8s would
        # not send a conventional ADDED/DELETED/... event but an error.
        if name.lower() == 'error' or response_type is None:
            return WatchResponse(name=name, raw=data, obj=None)

        # De-serialise the K8s response and return everything.
        obj = k8s.swagger.deserialize(data=k8s_obj, klass=response_type)
        return WatchResponse(name=name, raw=data, obj=obj)
