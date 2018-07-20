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
import tempfile
import unittest
import unittest.mock

import pytest

import aiokubernetes.config
import aiokubernetes.config.incluster_config as incluster_config

from .config_exception import ConfigException

pjoin = os.path.join


@unittest.mock.patch.object(incluster_config.os, 'getenv')
class TestCreateConfigFromServiceAccount:
    def test_join_host_port(self, m_env):
        """Concatenate host and port for IPv4 and IPv6."""
        assert incluster_config._join_host_port("127.0.0.1", "80") == "127.0.0.1:80"
        assert incluster_config._join_host_port("::1", "80") == "[::1]:80"

    def test_success(self, m_env):
        """Create service account credentials and correct env variables."""

        # Make `os.getenv` return a valid set of environemnt variables.
        env = {
            "KUBERNETES_SERVICE_HOST": "hostname",
            "KUBERNETES_SERVICE_PORT": "1234",
        }
        m_env.side_effect = lambda key, default: env[key] if key in env else default

        # Use a temporary folder to create dummy token- and certificate files.
        with tempfile.TemporaryDirectory() as dirname:
            # File names of token and cert file.
            fname_token, fname_cert = pjoin(dirname, 'token'), pjoin(dirname, 'cert')

            # Create dummy content for the files.
            open(fname_cert, 'w').write('my cert')
            open(fname_token, 'w').write('my token')

            # Compile the configuration using the service account tokens in the
            # Pod and verify it got the correct file and compiled the correct host.
            conf = incluster_config.load(fname_token, fname_cert)
            assert isinstance(conf, aiokubernetes.configuration.Configuration)
            assert conf.host == 'https://hostname:1234'
            assert conf.ssl_ca_cert == fname_cert
            assert conf.api_key['authorization'] == "bearer my token"

    def test_missing_env(self, m_env):
        """Pretend the environment variables are missing or empty."""

        # List of invalid environment variable setups.
        envs = [
            {},
            {"KUBERNETES_SERVICE_HOST": "hostname"},
            {"KUBERNETES_SERVICE_PORT": "1234"},
            {"KUBERNETES_SERVICE_HOST": ""},
            {"KUBERNETES_SERVICE_PORT": ""},
        ]
        for env in envs:
            m_env.side_effect = lambda key, default: env[key] if key in env else default
            with pytest.raises(ConfigException):
                incluster_config.load(None, None)

    def test_missing_token_or_cert(self, m_env):
        """Certificate and/or token are missing."""

        # Make `os.getenv` return a valid set of environemnt variables.
        env = {
            "KUBERNETES_SERVICE_HOST": "hostname",
            "KUBERNETES_SERVICE_PORT": "1234",
        }
        m_env.side_effect = lambda key, default: env[key] if key in env else default

        # Use a temporary folder to create dummy token- and certificate files.
        with tempfile.TemporaryDirectory() as dirname:
            # File names of token and cert file.
            fname_token, fname_cert = pjoin(dirname, 'token'), pjoin(dirname, 'cert')

            # Create dummy content for the files.
            open(fname_cert, 'w').write('my cert')
            open(fname_token, 'w').write('my token')

            # Token file does not exist.
            with pytest.raises(ConfigException):
                incluster_config.load(fname_token, '/foo')
            # Certificate file does not exist.
            with pytest.raises(ConfigException):
                incluster_config.load('/foo', fname_cert)

    def test_empty_token_or_cert(self, m_env):
        """Certificate and/or token files are empty."""

        # Make `os.getenv` return a valid set of environemnt variables.
        env = {
            "KUBERNETES_SERVICE_HOST": "hostname",
            "KUBERNETES_SERVICE_PORT": "1234",
        }
        m_env.side_effect = lambda key, default: env[key] if key in env else default

        # Use a temporary folder to create dummy token- and certificate files.
        with tempfile.TemporaryDirectory() as dirname:
            # File names of token and cert file.
            fname_token, fname_cert = pjoin(dirname, 'token'), pjoin(dirname, 'cert')

            # Certificate file is empty.
            open(fname_cert, 'w').write('')
            open(fname_token, 'w').write('my token')
            with pytest.raises(ConfigException):
                incluster_config.load(fname_token, fname_cert)

            # Token file is empty.
            open(fname_cert, 'w').write('my cert')
            open(fname_token, 'w').write('')
            with pytest.raises(ConfigException):
                incluster_config.load(fname_token, fname_cert)


if __name__ == '__main__':
    unittest.main()
