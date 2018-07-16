# Copyright 2016 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import aiokubernetes as k8s

from .config_exception import ConfigException

# Location where Kubernetes will put the service account token and certificate
# files inside a Pod.
CERT_FNAME = "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"
TOKEN_FNAME = "/var/run/secrets/kubernetes.io/serviceaccount/token"


def _join_host_port(host, port):
    """Adapted golang's net.JoinHostPort"""
    template = "%s:%s"
    host_requires_bracketing = ':' in host or '%' in host
    if host_requires_bracketing:
        template = "[%s]:%s"
    return template % (host, port)


def load_service_account_config(token_filename=TOKEN_FNAME, cert_filename=CERT_FNAME):
    """Return a client `Configuration` instance with service account credentials.

    Args:
        token_filename: str
            Leave blank to use the K8s default location inside pod.
        cert_filename: str
            Leave blank to use the K8s default location inside pod.

    Returns:
        Configuration

    """

    # Extract the API location from the env variables K8s creates inside the Pod.
    host = os.getenv("KUBERNETES_SERVICE_HOST", '')
    port = os.getenv("KUBERNETES_SERVICE_PORT", '')
    if host == '' or port == '':
        raise ConfigException("Service host/port is either empty or not set.")

    # Compile the full host name with scheme and port.
    host = "https://" + _join_host_port(host, port)

    # Token and certificate files must exist.
    if not os.path.isfile(token_filename):
        raise ConfigException(f"Token file <{token_filename}> does not exists.")
    if not os.path.isfile(cert_filename):
        raise ConfigException(f"Certificate file <{cert_filename}> does not exists.")

    # Load the token.
    token = open(token_filename).read()
    if len(token) == 0:
        raise ConfigException(f"Token file <{token_filename}> exists but is empty.")

    # Verify the cert is not empty. NOTE: we will not actually need the
    # certificate itself, just the file name.
    cert = open(cert_filename).read()
    if len(cert) == 0:
        raise ConfigException(f"Cert file <{cert_filename}> exists but is empty.")

    # Compile and return the Configuration instance.
    config = k8s.configuration.Configuration()
    config.host = host
    config.ssl_ca_cert = cert_filename
    config.api_key['authorization'] = "bearer " + token
    return config
