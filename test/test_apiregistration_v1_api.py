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
from aiokubernetes.api.apiregistration_v1_api import ApiregistrationV1Api  # noqa: E501
from aiokubernetes.rest import ApiException


class TestApiregistrationV1Api(unittest.TestCase):
    """ApiregistrationV1Api unit test stubs"""

    def setUp(self):
        self.api = aiokubernetes.api.apiregistration_v1_api.ApiregistrationV1Api(None)  # noqa: E501

    def tearDown(self):
        pass

    def test_create_api_service(self):
        """Test case for create_api_service

        """
        pass

    def test_delete_api_service(self):
        """Test case for delete_api_service

        """
        pass

    def test_delete_collection_api_service(self):
        """Test case for delete_collection_api_service

        """
        pass

    def test_get_api_resources(self):
        """Test case for get_api_resources

        """
        pass

    def test_list_api_service(self):
        """Test case for list_api_service

        """
        pass

    def test_patch_api_service(self):
        """Test case for patch_api_service

        """
        pass

    def test_read_api_service(self):
        """Test case for read_api_service

        """
        pass

    def test_replace_api_service(self):
        """Test case for replace_api_service

        """
        pass

    def test_replace_api_service_status(self):
        """Test case for replace_api_service_status

        """
        pass


if __name__ == '__main__':
    unittest.main()
