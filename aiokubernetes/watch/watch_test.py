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
from types import SimpleNamespace

from asynctest import CoroutineMock, Mock, TestCase

import aiokubernetes as k8s


class WatchTest(TestCase):

    def test_find_return_type(self):
        """A few basic test cases to ensure it does what it says."""
        fun = k8s.watch.watch._find_return_type

        # Must return None because the `None` object has an empty doc string
        # and is not a K8s type.
        self.assertIsNone(fun(None))

        # These have non-empty doc strings but are not a K8s types. The
        # function must therefore return None for them.
        self.assertIsNone(fun(''))
        self.assertIsNone(fun(object))

        class ClassWithValidDocString():
            """This has a valid doc string.
            :return: V1NamespaceList
            """
            pass

        self.assertEqual(fun(ClassWithValidDocString()), 'V1Namespace')

        class ClassWithInvalidDocString():
            """Multiple :return: strings.
            :return: foo
            blah
            :return: bar
            """
            pass

        with self.assertRaises(AssertionError):
            fun(ClassWithInvalidDocString())

    async def test_watch_with_decode(self):
        fake_resp = CoroutineMock()
        fake_resp.content.readline = CoroutineMock()
        side_effects = [
            {
                "type": "ADDED",
                "object": {
                    "metadata": {"name": "test{}".format(uid)},
                    "spec": {}, "status": {}
                }
            }
            for uid in range(3)
        ]
        side_effects = [json.dumps(_).encode('utf8') for _ in side_effects]
        side_effects.extend([AssertionError('Should not have been called')])
        fake_resp.content.readline.side_effect = side_effects

        # Actual API client instance because we will need it to wrap the
        # Json structure in `side_effects` into a Swagger generated Python object.
        api_client = k8s.api_client.ApiClient()

        fake_api = Mock()
        fake_api.get_namespaces = CoroutineMock(
            return_value=SimpleNamespace(parsed=fake_resp))
        fake_api.get_namespaces.__doc__ = ':return: V1NamespaceList'
        fake_api.get_namespaces.__self__ = SimpleNamespace(api_client=api_client)

        watch = k8s.watch.Watch(fake_api.get_namespaces, resource_version='123')
        count = 0
        async for e in watch:
            self.assertEqual("ADDED", e['type'])
            # make sure decoder worked and we got a model with the right name
            self.assertEqual("test%d" % count, e['object'].metadata.name)

            # Stop the watch. This must not return the next event which would
            # be an AssertionError exception.
            count += 1
            if count == len(side_effects) - 1:
                watch.stop()

        fake_api.get_namespaces.assert_called_once_with(
            _preload_content=False, watch=True, resource_version='123')

        # For a clean shutdown of the test.
        await api_client.rest_client.pool_manager.close()

    async def test_watch_k8s_empty_response(self):
        """Stop the iterator when the response is empty.

        This typically happens when the user supplied timeout expires.

        """
        # Mock the readline return value to first return a valid response
        # followed by an empty response.
        fake_resp = CoroutineMock()
        fake_resp.content.readline = CoroutineMock()
        side_effects = [
            {
                "type": "ADDED",
                "object": {"metadata": {"name": "test0"}, "spec": {}, "status": {}}
            },
            {
                "type": "ADDED",
                "object": {"metadata": {"name": "test1"}, "spec": {}, "status": {}}
            },
        ]
        side_effects = [json.dumps(_).encode('utf8') for _ in side_effects]
        fake_resp.content.readline.side_effect = side_effects + [b'']

        # Fake the K8s resource object to watch.
        fake_api = Mock()
        fake_api.get_namespaces = CoroutineMock(
            return_value=SimpleNamespace(parsed=fake_resp))
        fake_api.get_namespaces.__doc__ = ':return: V1NamespaceList'
        fake_api.get_namespaces.__self__ = fake_api

        # Iteration must cease after all valid responses were received.
        watch = k8s.watch.Watch(fake_api.get_namespaces)
        cnt = len([_ async for _ in watch])
        self.assertEqual(cnt, len(side_effects))

    def test_unmarshal_with_float_object(self):
        w = k8s.watch.Watch(k8s.api.CoreV1Api().list_namespace)
        event = w.unmarshal_event('{"type": "ADDED", "object": 1}', 'float')
        self.assertEqual("ADDED", event['type'])
        self.assertEqual(1.0, event['object'])
        self.assertTrue(isinstance(event['object'], float))
        self.assertEqual(1, event['raw_object'])

    def test_unmarshal_with_no_return_type(self):
        w = k8s.watch.Watch(k8s.api.CoreV1Api().list_namespace)
        event = w.unmarshal_event(
            '{"type": "ADDED", "object": ["test1"]}', None)
        self.assertEqual("ADDED", event['type'])
        self.assertEqual(["test1"], event['object'])
        self.assertEqual(["test1"], event['raw_object'])

    async def test_unmarshall_k8s_error_response(self):
        """Never parse messages of type ERROR.

        This test uses an actually recorded error, in this case for an outdated
        resource version.

        """
        # An actual error response sent by K8s during testing.
        k8s_err = {
            'type': 'ERROR',
            'object': {
                'kind': 'Status', 'apiVersion': 'v1', 'metadata': {},
                'status': 'Failure',
                'message': 'too old resource version: 1 (8146471)',
                'reason': 'Gone', 'code': 410
            }
        }

        watch = k8s.watch.Watch(k8s.api.CoreV1Api().list_namespace)
        ret = watch.unmarshal_event(json.dumps(k8s_err), None)
        self.assertEqual(ret['type'], k8s_err['type'])
        self.assertEqual(ret['object'], k8s_err['object'])
        self.assertEqual(ret['object'], k8s_err['object'])

    async def test_watch_with_exception(self):
        fake_resp = CoroutineMock()
        fake_resp.content.readline = CoroutineMock()
        fake_resp.content.readline.side_effect = KeyError("expected")
        fake_api = Mock()
        fake_api.get_namespaces = CoroutineMock(
            return_value=SimpleNamespace(parsed=fake_resp))
        fake_api.get_namespaces.__doc__ = ':return: V1NamespaceList'
        fake_api.get_namespaces.__self__ = fake_api

        with self.assertRaises(KeyError):
            watch = k8s.watch.Watch(fake_api.get_namespaces, timeout_seconds=10)
            [_ async for _ in watch]


if __name__ == '__main__':
    import asynctest
    asynctest.main()
