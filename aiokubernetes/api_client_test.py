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

import asynctest
from asynctest import CoroutineMock, TestCase, mock

import aiokubernetes as k8s
from aiokubernetes.api_client import ApiResponse


class ApiClientTest(TestCase):

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

        get_websocket_url = k8s.api_client.get_websocket_url
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

    async def test_close(self):
        """The `close` method must terminate all aiohttp connections."""

        # Create our ApiClient instance but stub out the session after closing
        # the existing one created in the ctor.
        api_client = k8s.api_client.ApiClient(k8s.configuration.Configuration())
        await api_client.session.close()
        api_client.session = mock.MagicMock(close=CoroutineMock())

        self.assertIsNone(await api_client.close())
        api_client.session.close.assert_called_once

    async def test_exec_ws(self):
        """Verify the Websocket connection sends the correct headers."""

        # Create an ApiClient but close the aiohttp session created in the ctor
        # and replace it with our own Mock.
        api_client = k8s.api_client.ApiClient(k8s.configuration.Configuration())
        await api_client.close()
        api_client.session = mock.MagicMock()

        # Make the websocket request through our Mock.
        core_api = k8s.CoreV1Api(api_client=api_client)
        resp = await core_api.connect_get_namespaced_pod_exec(
            'pod', 'namespace', command="mock-command",
            stderr=True, stdin=False, stdout=True, tty=False
        )

        # The WS connection must have received the correct headers.
        api_client.session.ws_connect.assert_called_once_with(
            'wss://localhost/api/v1/namespaces/namespace/pods/pod/exec?'
            'command=mock-command&stderr=True&stdin=False&stdout=True&tty=False',
            headers={
                'sec-websocket-protocol': 'v4.channel.k8s.io',
                'Accept': '*/*',
                'User-Agent': 'Swagger-Codegen/1.0/python',
                'Content-Type': 'application/json'
            }
        )

        # The response must contain the verbatim response from the Websocket
        # session and no parsed data.
        http = api_client.session.ws_connect.return_value
        self.assertEqual(resp, ApiResponse(http=http, obj=None))


if __name__ == '__main__':
    asynctest.main()
