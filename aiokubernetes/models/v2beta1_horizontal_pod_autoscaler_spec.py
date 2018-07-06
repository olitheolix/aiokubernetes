# coding: utf-8

"""
    Kubernetes

    No description provided (generated by Swagger Codegen https://github.com/swagger-api/swagger-codegen)  # noqa: E501

    OpenAPI spec version: v1.10.6
    
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401


from aiokubernetes.models.v2beta1_cross_version_object_reference import V2beta1CrossVersionObjectReference  # noqa: F401,E501
from aiokubernetes.models.v2beta1_metric_spec import V2beta1MetricSpec  # noqa: F401,E501


class V2beta1HorizontalPodAutoscalerSpec(object):
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
        'max_replicas': 'int',
        'metrics': 'list[V2beta1MetricSpec]',
        'min_replicas': 'int',
        'scale_target_ref': 'V2beta1CrossVersionObjectReference'
    }

    attribute_map = {
        'max_replicas': 'maxReplicas',
        'metrics': 'metrics',
        'min_replicas': 'minReplicas',
        'scale_target_ref': 'scaleTargetRef'
    }

    def __init__(self, max_replicas=None, metrics=None, min_replicas=None, scale_target_ref=None):  # noqa: E501
        """V2beta1HorizontalPodAutoscalerSpec - a model defined in Swagger"""  # noqa: E501

        self._max_replicas = None
        self._metrics = None
        self._min_replicas = None
        self._scale_target_ref = None
        self.discriminator = None

        self.max_replicas = max_replicas
        if metrics is not None:
            self.metrics = metrics
        if min_replicas is not None:
            self.min_replicas = min_replicas
        self.scale_target_ref = scale_target_ref

    @property
    def max_replicas(self):
        """Gets the max_replicas of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501

        maxReplicas is the upper limit for the number of replicas to which the autoscaler can scale up. It cannot be less that minReplicas.  # noqa: E501

        :return: The max_replicas of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501
        :rtype: int
        """
        return self._max_replicas

    @max_replicas.setter
    def max_replicas(self, max_replicas):
        """Sets the max_replicas of this V2beta1HorizontalPodAutoscalerSpec.

        maxReplicas is the upper limit for the number of replicas to which the autoscaler can scale up. It cannot be less that minReplicas.  # noqa: E501

        :param max_replicas: The max_replicas of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501
        :type: int
        """
        if max_replicas is None:
            raise ValueError("Invalid value for `max_replicas`, must not be `None`")  # noqa: E501

        self._max_replicas = max_replicas

    @property
    def metrics(self):
        """Gets the metrics of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501

        metrics contains the specifications for which to use to calculate the desired replica count (the maximum replica count across all metrics will be used).  The desired replica count is calculated multiplying the ratio between the target value and the current value by the current number of pods.  Ergo, metrics used must decrease as the pod count is increased, and vice-versa.  See the individual metric source types for more information about how each type of metric must respond.  # noqa: E501

        :return: The metrics of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501
        :rtype: list[V2beta1MetricSpec]
        """
        return self._metrics

    @metrics.setter
    def metrics(self, metrics):
        """Sets the metrics of this V2beta1HorizontalPodAutoscalerSpec.

        metrics contains the specifications for which to use to calculate the desired replica count (the maximum replica count across all metrics will be used).  The desired replica count is calculated multiplying the ratio between the target value and the current value by the current number of pods.  Ergo, metrics used must decrease as the pod count is increased, and vice-versa.  See the individual metric source types for more information about how each type of metric must respond.  # noqa: E501

        :param metrics: The metrics of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501
        :type: list[V2beta1MetricSpec]
        """

        self._metrics = metrics

    @property
    def min_replicas(self):
        """Gets the min_replicas of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501

        minReplicas is the lower limit for the number of replicas to which the autoscaler can scale down. It defaults to 1 pod.  # noqa: E501

        :return: The min_replicas of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501
        :rtype: int
        """
        return self._min_replicas

    @min_replicas.setter
    def min_replicas(self, min_replicas):
        """Sets the min_replicas of this V2beta1HorizontalPodAutoscalerSpec.

        minReplicas is the lower limit for the number of replicas to which the autoscaler can scale down. It defaults to 1 pod.  # noqa: E501

        :param min_replicas: The min_replicas of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501
        :type: int
        """

        self._min_replicas = min_replicas

    @property
    def scale_target_ref(self):
        """Gets the scale_target_ref of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501

        scaleTargetRef points to the target resource to scale, and is used to the pods for which metrics should be collected, as well as to actually change the replica count.  # noqa: E501

        :return: The scale_target_ref of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501
        :rtype: V2beta1CrossVersionObjectReference
        """
        return self._scale_target_ref

    @scale_target_ref.setter
    def scale_target_ref(self, scale_target_ref):
        """Sets the scale_target_ref of this V2beta1HorizontalPodAutoscalerSpec.

        scaleTargetRef points to the target resource to scale, and is used to the pods for which metrics should be collected, as well as to actually change the replica count.  # noqa: E501

        :param scale_target_ref: The scale_target_ref of this V2beta1HorizontalPodAutoscalerSpec.  # noqa: E501
        :type: V2beta1CrossVersionObjectReference
        """
        if scale_target_ref is None:
            raise ValueError("Invalid value for `scale_target_ref`, must not be `None`")  # noqa: E501

        self._scale_target_ref = scale_target_ref

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
        if not isinstance(other, V2beta1HorizontalPodAutoscalerSpec):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
