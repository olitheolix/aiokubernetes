import aiokubernetes as k8s


class TestProxyClass:
    def test_determine_swagger_type_ok(self):
        fun = k8s.swagger.determine_type

        assert fun('V1', 'Podlist') == 'V1PodList'
        assert fun('V1', 'Pod') == 'V1Pod'
        assert fun('Extensions/v1beta1', 'Deployment') == 'ExtensionsV1beta1Deployment'

        # If it ends in `list`, capitalise the list.
        assert fun('V1', 'Namespacelist') == 'V1NamespaceList'
