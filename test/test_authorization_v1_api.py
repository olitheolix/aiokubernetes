# coding: utf-8

"""
    Kubernetes

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: v1.10.6
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import unittest

import aiokubernetes
from aiokubernetes.api.authorization_v1_api import AuthorizationV1Api  # noqa: E501
from aiokubernetes.rest import ApiException


class TestAuthorizationV1Api(unittest.TestCase):
    """AuthorizationV1Api unit test stubs"""

    def setUp(self):
        self.api = aiokubernetes.api.authorization_v1_api.AuthorizationV1Api(None)  # noqa: E501

    def tearDown(self):
        pass

    def test_create_namespaced_local_subject_access_review(self):
        """Test case for create_namespaced_local_subject_access_review

        """
        pass

    def test_create_self_subject_access_review(self):
        """Test case for create_self_subject_access_review

        """
        pass

    def test_create_self_subject_rules_review(self):
        """Test case for create_self_subject_rules_review

        """
        pass

    def test_create_subject_access_review(self):
        """Test case for create_subject_access_review

        """
        pass

    def test_get_api_resources(self):
        """Test case for get_api_resources

        """
        pass


if __name__ == '__main__':
    unittest.main()
