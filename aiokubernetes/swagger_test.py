import json

import aiokubernetes as k8s


class TestProxyClass:
    def test_determine_swagger_type_ok(self):
        fun = k8s.swagger.determine_type

        assert fun('V1', 'Podlist') == 'V1PodList'
        assert fun('V1', 'Pod') == 'V1Pod'
        assert fun('Extensions/v1beta1', 'Deployment') == 'ExtensionsV1beta1Deployment'

        assert fun('V1', 'DeleteOptions') == 'V1DeleteOptions'

        # If it ends in `list`, capitalise the list.
        assert fun('V1', 'Namespacelist') == 'V1NamespaceList'

    def test_unpack_ok(self):
        # Create a Swagger object for this test. It must have a valid
        # `api_version` and `kind` for this test to work.
        manifest = k8s.V1DeleteOptions(
            api_version='V1', kind='DeleteOptions', grace_period_seconds=0,
            propagation_policy='Foreground',
        )

        # Serialise the object: Swagger -> Dict -> Json -> Bytes
        manifest_dict = k8s.api_proxy.sanitize_for_serialization(manifest)
        manifest_bytes = json.dumps(manifest_dict).encode('utf8')

        # The byte string is what a client would receive from K8s. Unwrap it
        # into a Swagger class.
        ret = k8s.swagger.unpack(manifest_bytes)
        assert ret == manifest

    def test_unpack_invalid_input(self):
        assert k8s.swagger.unpack(b'\xff') is None
        assert k8s.swagger.unpack(b'not ]json') is None

    def test_unpack_watch_ok(self):
        # Create a Swagger object for this test. It must have a valid
        # `api_version` and `kind` for this test to work.
        manifest = k8s.V1DeleteOptions(
            api_version='V1', kind='DeleteOptions', grace_period_seconds=0,
            propagation_policy='Foreground',
        )

        # Serialise the object: Swagger -> Dict -> Json -> Bytes
        manifest_dict = k8s.api_proxy.sanitize_for_serialization(manifest)

        watch_response = {'type': 'ADDED', 'object': manifest_dict}
        raw_data = json.dumps(watch_response).encode('utf8')

        # The byte string is what a client would receive from K8s. Unwrap it
        # into a Swagger class.
        name, obj = k8s.swagger.unpack_watch(raw_data)
        assert name == 'ADDED'
        assert obj == manifest

    def test_unpack_watch_invalid_input(self):
        assert k8s.swagger.unpack_watch(b'\xff') is None
        assert k8s.swagger.unpack_watch(b'not ]json') is None

        raw = json.dumps({'foo': 'ADDED'}).encode('utf8')
        assert k8s.swagger.unpack_watch(raw) is None
