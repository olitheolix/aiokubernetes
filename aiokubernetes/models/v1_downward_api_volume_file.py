# coding: utf-8

"""
    Kubernetes

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: v1.10.6
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401


from aiokubernetes.models.v1_object_field_selector import V1ObjectFieldSelector  # noqa: F401,E501
from aiokubernetes.models.v1_resource_field_selector import V1ResourceFieldSelector  # noqa: F401,E501


class V1DownwardAPIVolumeFile(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'field_ref': 'V1ObjectFieldSelector',
        'mode': 'int',
        'path': 'str',
        'resource_field_ref': 'V1ResourceFieldSelector'
    }

    attribute_map = {
        'field_ref': 'fieldRef',
        'mode': 'mode',
        'path': 'path',
        'resource_field_ref': 'resourceFieldRef'
    }

    def __init__(self, field_ref=None, mode=None, path=None, resource_field_ref=None):  # noqa: E501
        """V1DownwardAPIVolumeFile - a model defined in Swagger"""  # noqa: E501

        self._field_ref = None
        self._mode = None
        self._path = None
        self._resource_field_ref = None
        self.discriminator = None

        if field_ref is not None:
            self.field_ref = field_ref
        if mode is not None:
            self.mode = mode
        self.path = path
        if resource_field_ref is not None:
            self.resource_field_ref = resource_field_ref

    @property
    def field_ref(self):
        """Gets the field_ref of this V1DownwardAPIVolumeFile.  # noqa: E501

        Required: Selects a field of the pod: only annotations, labels, name and namespace are supported.  # noqa: E501

        :return: The field_ref of this V1DownwardAPIVolumeFile.  # noqa: E501
        :rtype: V1ObjectFieldSelector
        """
        return self._field_ref

    @field_ref.setter
    def field_ref(self, field_ref):
        """Sets the field_ref of this V1DownwardAPIVolumeFile.

        Required: Selects a field of the pod: only annotations, labels, name and namespace are supported.  # noqa: E501

        :param field_ref: The field_ref of this V1DownwardAPIVolumeFile.  # noqa: E501
        :type: V1ObjectFieldSelector
        """

        self._field_ref = field_ref

    @property
    def mode(self):
        """Gets the mode of this V1DownwardAPIVolumeFile.  # noqa: E501

        Optional: mode bits to use on this file, must be a value between 0 and 0777. If not specified, the volume defaultMode will be used. This might be in conflict with other options that affect the file mode, like fsGroup, and the result can be other mode bits set.  # noqa: E501

        :return: The mode of this V1DownwardAPIVolumeFile.  # noqa: E501
        :rtype: int
        """
        return self._mode

    @mode.setter
    def mode(self, mode):
        """Sets the mode of this V1DownwardAPIVolumeFile.

        Optional: mode bits to use on this file, must be a value between 0 and 0777. If not specified, the volume defaultMode will be used. This might be in conflict with other options that affect the file mode, like fsGroup, and the result can be other mode bits set.  # noqa: E501

        :param mode: The mode of this V1DownwardAPIVolumeFile.  # noqa: E501
        :type: int
        """

        self._mode = mode

    @property
    def path(self):
        """Gets the path of this V1DownwardAPIVolumeFile.  # noqa: E501

        Required: Path is  the relative path name of the file to be created. Must not be absolute or contain the '..' path. Must be utf-8 encoded. The first item of the relative path must not start with '..'  # noqa: E501

        :return: The path of this V1DownwardAPIVolumeFile.  # noqa: E501
        :rtype: str
        """
        return self._path

    @path.setter
    def path(self, path):
        """Sets the path of this V1DownwardAPIVolumeFile.

        Required: Path is  the relative path name of the file to be created. Must not be absolute or contain the '..' path. Must be utf-8 encoded. The first item of the relative path must not start with '..'  # noqa: E501

        :param path: The path of this V1DownwardAPIVolumeFile.  # noqa: E501
        :type: str
        """
        if path is None:
            raise ValueError("Invalid value for `path`, must not be `None`")  # noqa: E501

        self._path = path

    @property
    def resource_field_ref(self):
        """Gets the resource_field_ref of this V1DownwardAPIVolumeFile.  # noqa: E501

        Selects a resource of the container: only resources limits and requests (limits.cpu, limits.memory, requests.cpu and requests.memory) are currently supported.  # noqa: E501

        :return: The resource_field_ref of this V1DownwardAPIVolumeFile.  # noqa: E501
        :rtype: V1ResourceFieldSelector
        """
        return self._resource_field_ref

    @resource_field_ref.setter
    def resource_field_ref(self, resource_field_ref):
        """Sets the resource_field_ref of this V1DownwardAPIVolumeFile.

        Selects a resource of the container: only resources limits and requests (limits.cpu, limits.memory, requests.cpu and requests.memory) are currently supported.  # noqa: E501

        :param resource_field_ref: The resource_field_ref of this V1DownwardAPIVolumeFile.  # noqa: E501
        :type: V1ResourceFieldSelector
        """

        self._resource_field_ref = resource_field_ref

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in self.swagger_types.items():
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, V1DownwardAPIVolumeFile):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
