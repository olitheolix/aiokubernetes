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
from asynctest import TestCase

import aiokubernetes as k8s


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


if __name__ == '__main__':
    asynctest.main()
