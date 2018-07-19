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

from collections import namedtuple

import aiokubernetes as k8s

# All API responses will be wrapped into this tuple.
# The `name` will be 'ADDED', MODIFIED, etc, `raw` will the unprocessed but
# Json decoded response from K8s and `obj` will be the Swagger object created
# from `raw` (may be None if there was an error).
WatchResponse = namedtuple('WatchResponse', 'name raw obj')


class AioHttpClientWatch(object):
    """Convenience wrapper to consume K8s event stream.

    This wrapper is custom made for AioHttp clients.

    Input:
        request: AioHttp client instance.
    """
    def __init__(self, request):
        self.request = request
        self.connection = None

    def __aiter__(self):
        return self

    async def __anext__(self):
        # Set the response object to the user supplied function (eg
        # `list_namespaced_pods`) if this is the first iteration.
        if self.connection is None:
            self.connection = await self.request

        # Wait until K8s sends another line (ie another event).
        line = await self.connection.content.readline()

        # Stop the iterator when the response is empty. This happens when
        # either the user-supplied timeout expired or there is no more data.
        if len(line) == 0:
            raise StopAsyncIteration

        # Return then unpacked response.
        name, obj = k8s.swagger.unpack_watch(line)
        return WatchResponse(name=name, raw=line, obj=obj)
