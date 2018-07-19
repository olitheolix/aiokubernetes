import datetime
import aiokubernetes as k8s

from types import SimpleNamespace


class TestProxyClass:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_ctor(self):
        args, kwargs = (1, 2), dict(x=1, y=2)
        proxy = k8s.api_proxy.Proxy('config', *args, **kwargs)

    def test_select_header_accept_empty(self):
        fun = k8s.api_proxy.Proxy.select_header_accept

        for empty in (tuple(), list(), None):
            assert fun(empty) is None

    def test_select_header_accept_non_empty(self):
        fun = k8s.api_proxy.Proxy.select_header_accept

        assert fun(['foo', 'bar']) == 'foo, bar'
        assert fun(['foo', 'bar', 'APPLICATION/json']) == 'application/json'

    def test_select_header_content_type_empty(self):
        fun = k8s.api_proxy.Proxy.select_header_content_type

        for empty in (tuple(), list(), None):
            assert fun(empty) == 'application/json'

    def test_select_header_content_type_non_empty(self):
        fun = k8s.api_proxy.Proxy.select_header_content_type

        assert fun(['foo', 'bar']) == 'foo'
        assert fun(['foo', 'bar', 'APPLICATION/json']) == 'application/json'
        assert fun(['foo', 'bar', '*/*']) == 'application/json'

    def test_sanitize_for_serialization_basic(self):
        # Basic types must pass unchanged.
        basic = (None, 1, 1.5, 'string', b'bytes')

        fun = k8s.api_proxy.sanitize_for_serialization
        for obj in basic:
            assert fun(obj) is obj

        # Every element in a list or tuple be serialised independently and
        # returned as a list/tuple.
        assert fun(tuple(basic)) == tuple(basic)
        assert fun(list(basic)) == list(basic)

        # Every element in a dictionary must be sanitised individually. The
        # dictionary must be a copy to avoid side effects.
        demo_dict = {str(idx): obj for idx, obj in enumerate(basic)}
        ret = fun(demo_dict)
        assert ret == demo_dict
        assert ret is not demo_dict

        dt = datetime.datetime.now()
        assert fun(dt) == dt.isoformat()

    def test_sanitize_for_serialization_swagger_object(self):
        obj = SimpleNamespace()
        obj.api_version = 'v1'
        obj.grace_period_seconds = 5
        obj.orphan_dependents = True
        obj.attribute_map = {
            'api_version': 'apiVersion',
            'grace_period_seconds': 'gracePeriodSeconds',
            'orphan_dependents': 'orphanDependents'
        }
        obj.swagger_types = {
            'api_version': 'str',
            'grace_period_seconds': 'int',
            'orphan_dependents': 'bool'
        }

        fun = k8s.api_proxy.sanitize_for_serialization
        ret = fun(obj)
        assert ret == {
            'apiVersion': 'v1',
            'gracePeriodSeconds': 5,
            'orphanDependents': True,
        }

    def test_build_url(self):
        fun = k8s.api_proxy.build_url
        config = k8s.configuration.Configuration()
        config.host = 'myhost'

        kwargs = fun(
            config,
            resource_path='/api/v1/namespaces/{namespace}/pods/{name}/exec',
            path_params={'name': 'login-cd546cd56-q8254', 'namespace': 'foo'},
            query_params=[('command', ['/bin/sh', 'echo err >&2']), ('stderr', True)],
            header_params={'Accept': '*/*', 'Content-Type': 'application/json'},
            post_params={'Accept': '*/*', 'Content-Type': 'application/json'},
            auth_settings=['BearerToken'],
            body=None
        )

        assert kwargs == {
            'body': None,
            'headers': {
                'Accept': '*/*',
                'Content-Type': 'application/json'
            },
            'post_params': {
                'Accept': '*/*', 'Content-Type': 'application/json'
            },
            'query_params': [
                ('command', '/bin/sh'), ('command', 'echo err >&2'), ('stderr', True)
            ],
            'url': 'myhost/api/v1/namespaces/foo/pods/login-cd546cd56-q8254/exec',
            '_request_timeout': 10
        }
