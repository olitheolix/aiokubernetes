[![Build Status](https://travis-ci.org/olitheolix/aiokubernetes.svg?branch=master)](https://travis-ci.org/olitheolix/aiokubernetes)
[![PyPI version](https://badge.fury.io/py/aiokubernetes.svg)](https://badge.fury.io/py/aiokubernetes)
[![pypi supported versions](https://img.shields.io/pypi/pyversions/aiokubernetes.svg)](https://pypi.python.org/pypi/aiokubernetes)

<p align="center"><img src="aiokubernetes.svg" width="50%"></p>

# Async Kubernetes Client


See the [documentation](https://aiokubernetes.readthedocs.io/en/latest/) and
[examples](examples/) for usage instructions.


## Key Features

- Based on [aiohttp](https://aiohttp.readthedocs.io/en/stable/).
- Websocket stream when executing commands in Pods.
- Uses [Swagger](https://github.com/swagger-api/swagger-codegen) to generate Kubernetes models and API calls.
- Based on the [Kubernetes Python client generator](https://github.com/kubernetes-client/gen).
- Python 3.7 support.

## Getting Started

```bash
pip install aiokubernetes
```

### List all Pods

```python
import asyncio
import aiokubernetes as k8s

async def main():
    # Load default kubeconfig file and create an aiohttp client instance.
    config = k8s.utils.load_config(warn=False)
    client = k8s.clients.get_aiohttp(config)
    proxy = k8s.api_proxy.Proxy(config)

    # Ask Kubernetes for all Pods.
    cargs = k8s.api.CoreV1Api(proxy).list_namespace(watch=False)
    ret = await client.request(**cargs)

    # Ensure the API call to Kubernetes did succeed.
    assert ret.status == 200

    # Optional: wrap the JSon response into a Swagger generated Python object.
    obj = k8s.swagger.unpack(await ret.read())

    # Print the pod names.
    for i in obj.items:
        print(f"{i.metadata.namespace} {i.metadata.name}")

    # Close all pending client connections.
    await client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
```

### Concurrently Watch Multiple Resources
Watch several Kubernetes resources for 5 seconds then shut down gracefully.

```python
import asyncio

import aiokubernetes as k8s


async def watch_resource(client, cargs):
    """Consume and print the events as they stream in."""

    # Use helper class to consume the K8s events via an async iterator.
    watch = k8s.watch.AioHttpClientWatch(client.request(**cargs))
    async for event in watch:
        print(f"{event.name} {event.obj.kind} {event.obj.metadata.name}")


async def main():
    # Load default kubeconfig file and create an aiohttp client instance.
    config = k8s.utils.load_config(warn=False)
    client = k8s.clients.get_aiohttp(config)
    proxy = k8s.api_proxy.Proxy(config)

    # Namespaces and Pods are in the K8s Core API, Deployments in an extension (unless you run a very recent K8s version).
    corev1 = k8s.CoreV1Api(proxy)
    extv1beta = k8s.ExtensionsV1beta1Api(proxy)

    # Compile the necessary request parameters (headers, body, parameters, ...)
    # for the API calls we want to make. We also specify watch=True because we
    # want to listen to changes.
    cargs_ns = corev1.list_namespace(timeout_seconds=5, watch=True)
    cargs_pods = corev1.list_pod_for_all_namespaces(timeout_seconds=5, watch=True)
    cargs_deploy = extv1beta.list_deployment_for_all_namespaces(timeout_seconds=5, watch=True) # noqa

    # Define and dispatch the tasks.
    tasks = [
        watch_resource(client, cargs_ns),
        watch_resource(client, cargs_pods),
        watch_resource(client, cargs_deploy),
    ]
    await asyncio.gather(*tasks)

    # Close all pending connections.
    await client.close()


if __name__ == '__main__':
    # Setup event loop and start the program.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(main()))
    loop.close()
```

## Source code

```bash
git clone https://github.com/olitheolix/aiokubernetes.git
cd aiokubernetes
pip install -r requirements.txt
pip install -r test-requirements.txt
```

Feel free to submit pull requests and issues.

### Unit Tests

We use [pytest](https://docs.pytest.org/en/latest/):

```bash
# Run tests sequentially.
pytest

# Run tests in 8 parallel processes.
pytest -n8
```

### CI Tests
[Travis](https://travis-ci.com/olitheolix/aiokubernetes) runs all tests in
Docker containers (see [.travis](.travis.yml) for details).

You can run these containerised tests locally as well to ensure Travis on
Github will approve your build _before_ you push it.

```bash
docker run -ti -v`pwd`:/src python:3.6-alpine3.7 /bin/ash -c "cd /src; ash scripts/run-ci-tests.sh"
docker run -ti -v`pwd`:/src python:3.7-alpine3.7 /bin/ash -c "cd /src; ash scripts/run-ci-tests.sh"
```


## Motivation
Like [Python Kubernetes](https://github.com/kubernetes-client/python) and
[kubernetes_asyncio](https://github.com/tomplus/kubernetes_asyncio), this
client library uses the
[Swagger-generated](https://github.com/kubernetes-client/gen) Api- and model
classes. Unlike those two libraries, it only supports Python 3.6+. All Python
2.x code paths are gone, as is the dependency on
[six](https://pypi.org/project/six/).


Also unlike
[kubernetes_asyncio](https://github.com/tomplus/kubernetes_asyncio),
`aiokubernetes` is _not_ backwards compatible with the synchronous [Python
Kubernetes](https://github.com/kubernetes-client/python) client. The
differences are, however, minor from a user's point of view (see the
[examples/](examples)).

The primary difference is the increased emphasis on "Explicit is better than
implicit" ([Zen of Python](https://www.python.org/dev/peps/pep-0020/)). To that
end, `aiokubernetes` _never_ creates implicit HTTP session objects (the user
must supply `ApiClient` instances) and the library _always_ returns the
native HTTP response object.

The HTTP response object is particularly useful for debugging because it
provides trivial access to Url, method, path, headers, status code and raw
response data before it was de-serialised into a Swagger class.

The plan is to simplify the new `ApiClient` further and cover it with tests
along the way because the auto-generated `api_client.py` and `rest.py` classes
have none, unfortunately.


## License

``aiokubernetes`` is licensed under the [Apache 2 license](LICENSE).


![](https://cdn.pixabay.com/photo/2012/04/01/18/55/work-in-progress-24027_1280.png)
