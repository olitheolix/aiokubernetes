# V1APIVersions

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**api_version** | **str** | APIVersion defines the versioned schema of this representation of an object. Servers should convert recognized schemas to the latest internal value, and may reject unrecognized values. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#resources | [optional] 
**kind** | **str** | Kind is a string value representing the REST resource this object represents. Servers may infer this from the endpoint the aiokubernetes.client submits requests to. Cannot be updated. In CamelCase. More info: https://git.k8s.io/community/contributors/devel/api-conventions.md#types-kinds | [optional] 
**server_address_by_client_cid_rs** | [**list[V1ServerAddressByClientCIDR]**](V1ServerAddressByClientCIDR.md) | a map of aiokubernetes.client CIDR to server address that is serving this group. This is to help aiokubernetes.clients reach servers in the most network-efficient way possible. Clients can use the appropriate server address as per the CIDR that they match. In case of multiple matches, aiokubernetes.clients should use the longest matching CIDR. The server returns only those CIDRs that it thinks that the aiokubernetes.client can match. For example: the master will return an internal IP CIDR only, if the aiokubernetes.client reaches the server using an internal IP. Server looks at X-Forwarded-For header or X-Real-Ip header or request.RemoteAddr (in that order) to get the aiokubernetes.client IP. | 
**versions** | **list[str]** | versions are the api versions that are available. | 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


