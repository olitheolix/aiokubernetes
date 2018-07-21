"""Watch multiple K8s event streams without threads."""
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

    # Namespaces and Pods are in the K8s Core API, Deployments in an extension.
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
