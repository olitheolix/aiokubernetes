# aiokubernetes.ApisApi

All URIs are relative to *https://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_api_versions**](ApisApi.md#get_api_versions) | **GET** /apis/ | 


# **get_api_versions**
> V1APIGroupList get_api_versions()



get available API versions

### Example
```python
from __future__ import print_function
import time
import aiokubernetes
from aiokubernetes.rest import ApiException
from pprint import pprint

# Configure API key authorization: BearerToken
configuration = aiokubernetes.Configuration()
configuration.api_key['authorization'] = 'YOUR_API_KEY'
# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['authorization'] = 'Bearer'

# create an instance of the API class
api_instance = aiokubernetes.ApisApi(aiokubernetes.ApiClient(configuration))

try:
    api_response = api_instance.get_api_versions()
    pprint(api_response)
except ApiException as e:
    print("Exception when calling ApisApi->get_api_versions: %s\n" % e)
```

### Parameters
This endpoint does not need any parameter.

### Return type

[**V1APIGroupList**](V1APIGroupList.md)

### Authorization

[BearerToken](../README.md#BearerToken)

### HTTP request headers

 - **Content-Type**: application/json, application/yaml, application/vnd.kubernetes.protobuf
 - **Accept**: application/json, application/yaml, application/vnd.kubernetes.protobuf

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

