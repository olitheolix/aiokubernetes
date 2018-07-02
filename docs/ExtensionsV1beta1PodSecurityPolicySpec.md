# ExtensionsV1beta1PodSecurityPolicySpec

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**allow_privilege_escalation** | **bool** | AllowPrivilegeEscalation determines if a pod can request to allow privilege escalation. If unspecified, defaults to true. | [optional] 
**allowed_capabilities** | **list[str]** | AllowedCapabilities is a list of capabilities that can be requested to add to the container. Capabilities in this field may be added at the pod author&#39;s discretion. You must not list a capability in both AllowedCapabilities and RequiredDropCapabilities. | [optional] 
**allowed_flex_volumes** | [**list[ExtensionsV1beta1AllowedFlexVolume]**](ExtensionsV1beta1AllowedFlexVolume.md) | AllowedFlexVolumes is a whitelist of allowed Flexvolumes.  Empty or nil indicates that all Flexvolumes may be used.  This parameter is effective only when the usage of the Flexvolumes is allowed in the \&quot;Volumes\&quot; field. | [optional] 
**allowed_host_paths** | [**list[ExtensionsV1beta1AllowedHostPath]**](ExtensionsV1beta1AllowedHostPath.md) | is a white list of allowed host paths. Empty indicates that all host paths may be used. | [optional] 
**default_add_capabilities** | **list[str]** | DefaultAddCapabilities is the default set of capabilities that will be added to the container unless the pod spec specifically drops the capability.  You may not list a capability in both DefaultAddCapabilities and RequiredDropCapabilities. Capabilities added here are implicitly allowed, and need not be included in the AllowedCapabilities list. | [optional] 
**default_allow_privilege_escalation** | **bool** | DefaultAllowPrivilegeEscalation controls the default setting for whether a process can gain more privileges than its parent process. | [optional] 
**fs_group** | [**ExtensionsV1beta1FSGroupStrategyOptions**](ExtensionsV1beta1FSGroupStrategyOptions.md) | FSGroup is the strategy that will dictate what fs group is used by the SecurityContext. | 
**host_ipc** | **bool** | hostIPC determines if the policy allows the use of HostIPC in the pod spec. | [optional] 
**host_network** | **bool** | hostNetwork determines if the policy allows the use of HostNetwork in the pod spec. | [optional] 
**host_pid** | **bool** | hostPID determines if the policy allows the use of HostPID in the pod spec. | [optional] 
**host_ports** | [**list[ExtensionsV1beta1HostPortRange]**](ExtensionsV1beta1HostPortRange.md) | hostPorts determines which host port ranges are allowed to be exposed. | [optional] 
**privileged** | **bool** | privileged determines if a pod can request to be run as privileged. | [optional] 
**read_only_root_filesystem** | **bool** | ReadOnlyRootFilesystem when set to true will force containers to run with a read only root file system.  If the container specifically requests to run with a non-read only root file system the PSP should deny the pod. If set to false the container may run with a read only root file system if it wishes but it will not be forced to. | [optional] 
**required_drop_capabilities** | **list[str]** | RequiredDropCapabilities are the capabilities that will be dropped from the container.  These are required to be dropped and cannot be added. | [optional] 
**run_as_user** | [**ExtensionsV1beta1RunAsUserStrategyOptions**](ExtensionsV1beta1RunAsUserStrategyOptions.md) | runAsUser is the strategy that will dictate the allowable RunAsUser values that may be set. | 
**se_linux** | [**ExtensionsV1beta1SELinuxStrategyOptions**](ExtensionsV1beta1SELinuxStrategyOptions.md) | seLinux is the strategy that will dictate the allowable labels that may be set. | 
**supplemental_groups** | [**ExtensionsV1beta1SupplementalGroupsStrategyOptions**](ExtensionsV1beta1SupplementalGroupsStrategyOptions.md) | SupplementalGroups is the strategy that will dictate what supplemental groups are used by the SecurityContext. | 
**volumes** | **list[str]** | volumes is a white list of allowed volume plugins.  Empty indicates that all plugins may be used. | [optional] 

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


