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

from setuptools import setup

REQUIRES = open('requirements.txt').readlines()
TESTS_REQUIRES = open('test-requirements.txt').readlines()

CLIENT_VERSION = "0.5"
PACKAGE_NAME = "aiokubernetes"
DEVELOPMENT_STATUS = "4 - Beta"


setup(
    name=PACKAGE_NAME,
    version=CLIENT_VERSION,
    description="Asynchronous Kubernetes client",
    author_email="",
    author="Kubernetes",
    license="Apache License Version 2.0",
    url="https://github.com/olitheolix/aiokubernetes",
    keywords=[
        "Swagger",
        "OpenAPI",
        "Kubernetes",
        "async",
        "asyncio",
    ],
    install_requires=REQUIRES,
    tests_require=TESTS_REQUIRES,
    packages=[
        'aiokubernetes',
        'aiokubernetes.api',
        'aiokubernetes.config',
        'aiokubernetes.watch',
        'aiokubernetes.models',
    ],
    include_package_data=True,
    long_description="""\
    Python client for kubernetes http://kubernetes.io/
    """,
    classifiers=[
        f"Development Status :: {DEVELOPMENT_STATUS}",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
