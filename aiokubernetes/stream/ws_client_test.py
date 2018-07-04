# Copyright 2017 The Kubernetes Authors.
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

from types import SimpleNamespace

import asynctest
from asynctest import CoroutineMock, TestCase, patch, mock

import aiokubernetes as k8s
from aiokubernetes.stream import WebsocketApiClient
from aiokubernetes.stream.ws_client import get_websocket_url


class WSClientTest(TestCase):

    def test_get_websocket_url(self):
        in_out = [
            ('http://localhost/api', 'ws://localhost/api'),
            ('https://localhost/api', 'wss://localhost/api'),
            ('https://domain.com/api', 'wss://domain.com/api'),
            ('https://api.domain.com/api', 'wss://api.domain.com/api'),
            ('http://api.domain.com', 'ws://api.domain.com'),
            ('https://api.domain.com', 'wss://api.domain.com'),
            ('http://api.domain.com/', 'ws://api.domain.com/'),
            ('https://api.domain.com/', 'wss://api.domain.com/'),
        ]

        for url, ws_url in in_out:
            self.assertEqual(get_websocket_url(url), ws_url)

            # The parser must cope with non-lower case schemes (eg
            # HTtp://foo.com) but always return strictly lower-case versions
            # (eg http://foo.com).
            url_upper = url.replace('http', 'HtTp')
            self.assertEqual(get_websocket_url(url_upper), ws_url)

        # Hard abort for unknown schemes.
        with self.assertRaises(AssertionError):
            get_websocket_url('foo://bar.com')

    @mock.patch.object(k8s.api_client, 'rest')
    async def test_exec_ws(self, m_rest):
        """Verify the Websocket connection sends the correct headers."""

        # Iterator mock to simulate a websocket connection. Aiohttp uses
        # async context managers which is why need to turn this mock object
        # into an async context manager afterwards as well.
        m_ws = asynctest.mock.MagicMock()
        m_ws.__aiter__.return_value = [
            SimpleNamespace(data=(chr(1) + 'message1 ').encode('utf-8')),
            SimpleNamespace(data=(chr(1) + 'message2 ').encode('utf-8')),
        ]
        m_ws.__aenter__.return_value = m_ws.__aexit__.return_value = m_ws

        m_rest.RESTClientObject.return_value.pool_manager = m_rest
        m_rest.ws_connect.return_value = m_ws

        # Make the websocket request through our Mock.
        ws = k8s.CoreV1Api(api_client=WebsocketApiClient())
        resp = await ws.connect_get_namespaced_pod_exec(
            'pod', 'namespace', command="mock-command",
            stderr=True, stdin=False, stdout=True, tty=False
        )

        # Must have returned the payload we specified in the async iterator above.
        self.assertEqual(resp.parsed, 'message1 message2 ')

        # The WS connection must have received the correct headers automatically.
        m_rest.ws_connect.assert_called_once_with(
            'wss://localhost/api/v1/namespaces/namespace/pods/pod/exec?'
            'command=mock-command&stderr=True&stdin=False&stdout=True&tty=False',
            headers={
                'sec-websocket-protocol': 'v4.channel.k8s.io',
                'Accept': '*/*',
                'User-Agent': 'Swagger-Codegen/1.0/python',
                'Content-Type': 'application/json'
            }
        )


if __name__ == '__main__':
    asynctest.main()
