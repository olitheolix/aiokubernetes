# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from types import SimpleNamespace
from urllib.parse import urlencode, urlparse, urlunparse

import aiohttp

import aiokubernetes

STDIN_CHANNEL = 0
STDOUT_CHANNEL = 1
STDERR_CHANNEL = 2
ERROR_CHANNEL = 3
RESIZE_CHANNEL = 4


def get_websocket_url(url):
    parts = urlparse(url)
    assert parts.scheme in ('http', 'https'), f'Unknown scheme <{parts.scheme}>'
    new_scheme = 'ws' if parts.scheme == 'http' else 'wss'
    return urlunparse(parts._replace(scheme=new_scheme))


class WebsocketApiClient(aiokubernetes.api_client.ApiClient):
    def __init__(self, *args, **kwargs):
        self.queue = kwargs.pop('queue', None)
        super().__init__(*args, **kwargs)

    async def request(self, method, url, query_params=None, headers=None,
                      post_params=None, body=None, _preload_content=True,
                      _request_timeout=None):

        # Expand command parameter list to individual command params
        if query_params:
            new_query_params = []
            for key, value in query_params:
                if key == 'command' and isinstance(value, list):
                    for command in value:
                        new_query_params.append((key, command))
                else:
                    new_query_params.append((key, value))
            query_params = new_query_params

        headers = headers or {}
        if 'sec-websocket-protocol' not in headers:
            headers['sec-websocket-protocol'] = 'v4.channel.k8s.io'

        if query_params:
            url += '?' + urlencode(query_params)

        url = get_websocket_url(url)

        if _preload_content:
            resp_all = ''
            pool = self.rest_client.pool_manager
            async with pool.ws_connect(url, headers=headers) as ws:
                async for msg in ws:
                    # The messages are of type `aiohttp.WSMessage`.
                    # We currently only allow binary content.
                    # fixup: graceful handling of alternative content; stream
                    # raw content through queue?
                    assert msg.type == aiohttp.WSMsgType.BINARY, 'Wrong message type'
                    msg = msg.data

                    # Ignore empty messages.
                    if len(msg) == 0:
                        continue

                    # Put the message verbatim into the user supplied queue.
                    if self.queue is not None:
                        await self.queue.put(msg)

                    # The first byte determines if the message was printed on
                    # STDOUT or STDERR. Ignore the messages that were neither
                    # (ie ERROR_CHANNEL).
                    # fixup: when do we actually get an ERROR_CHANNEL? Add test.
                    channel, data = msg[0], msg[1:]
                    if len(data) > 0 and channel in [STDOUT_CHANNEL, STDERR_CHANNEL]:
                        resp_all += data.decode('utf8')

            # fixme: Make this an aiohttp response.
            async def data_json():
                return resp_all
            return SimpleNamespace(
                data=resp_all,
                json=data_json,
                status=200,
                response_type=None,
                method='WEBSOCKET',
                url=url,
            )
        else:
            return self.rest_client.pool_manager.ws_connect(url)
