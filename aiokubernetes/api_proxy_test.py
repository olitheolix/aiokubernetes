import aiokubernetes.api_proxy as api_proxy


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
        """Ensure ctor creates deep copies of the input."""
        args, kwargs = (1, 2), dict(x=1, y=2)
        proxy = api_proxy.Proxy('config', *args, **kwargs)

        # Proxy instance must store copies of the inputs.
        assert proxy.args == args
        assert proxy.kwargs == kwargs
        assert proxy.args is not args
        assert proxy.kwargs is not kwargs

    def test_select_header_accept_empty(self):
        fun = api_proxy.Proxy.select_header_accept

        for empty in (tuple(), list(), None):
            assert fun(empty) is None

    def test_select_header_accept_non_empty(self):
        fun = api_proxy.Proxy.select_header_accept

        assert fun(['foo', 'bar']) == 'foo, bar'
        assert fun(['foo', 'bar', 'APPLICATION/json']) == 'application/json'

    def test_select_header_content_type_empty(self):
        fun = api_proxy.Proxy.select_header_content_type

        for empty in (tuple(), list(), None):
            assert fun(empty) == 'application/json'

    def test_select_header_content_type_non_empty(self):
        fun = api_proxy.Proxy.select_header_content_type

        assert fun(['foo', 'bar']) == 'foo'
        assert fun(['foo', 'bar', 'APPLICATION/json']) == 'application/json'
        assert fun(['foo', 'bar', '*/*']) == 'application/json'
