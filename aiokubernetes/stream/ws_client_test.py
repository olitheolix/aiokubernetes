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

import asyncio
from types import SimpleNamespace

import aiohttp
import asynctest
from asynctest import TestCase, mock

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

        # Mocked async iterator to simulate the message streaming in from a
        # websocket connection. We must also turn this mock into an async
        # context managers because this is what `aiohttp` does and our
        # WebsocketApiClient assumes it deals with `aiohttp`.
        m_ws = asynctest.mock.MagicMock()
        m_ws.__aiter__.return_value = [
            SimpleNamespace(data=(b'\x01message1 '), type=aiohttp.WSMsgType.BINARY),
            SimpleNamespace(data=(b'\x01message2 '), type=aiohttp.WSMsgType.BINARY),
        ]
        m_ws.__aenter__.return_value = m_ws.__aexit__.return_value = m_ws

        # Stub out the Rest client that will ultimately be called on to create
        # the Websocket connection.
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

    @mock.patch.object(k8s.api_client, 'rest')
    async def test_ws_put_messages_into_queue(self, m_rest):
        """Messages must go into a queue as they stream in."""

        # Mocked async iterator to simulate the message streaming in from a
        # websocket connection. We must also turn this mock into an async
        # context managers because this is what `aiohttp` does and our
        # WebsocketApiClient assumes it deals with `aiohttp`.
        m_ws = asynctest.mock.MagicMock()
        m_ws.__aiter__.return_value = [
            SimpleNamespace(data=(b'\x01message1 '), type=aiohttp.WSMsgType.BINARY),
            SimpleNamespace(data=(b'\x01message2 '), type=aiohttp.WSMsgType.BINARY),
        ]
        m_ws.__aenter__.return_value = m_ws.__aexit__.return_value = m_ws

        # Stub out the Rest client that will ultimately be called on to create
        # the Websocket connection.
        m_rest.RESTClientObject.return_value.pool_manager = m_rest
        m_rest.ws_connect.return_value = m_ws

        queue = asyncio.Queue()

        # Make the websocket request through our Mock. Pass our Queue along to
        # the WebsocketClient to receive message immediately.
        ws = k8s.CoreV1Api(api_client=WebsocketApiClient(queue=queue))
        await ws.connect_get_namespaced_pod_exec(
            'pod', 'namespace', command="mock-command",
            stderr=True, stdin=False, stdout=True, tty=False
        )

        # Messages must also have been pushed into the queue as they came in.
        assert queue.qsize() == 2
        self.assertEqual(await queue.get(), b'\x01message1 ')
        self.assertEqual(await queue.get(), b'\x01message2 ')


if __name__ == '__main__':
    asynctest.main()
