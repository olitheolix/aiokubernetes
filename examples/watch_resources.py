"""Watch multiple K8s event streams without threads."""
import asyncio
import os
import warnings

import aiokubernetes as k8s


async def watch_resource(client, cargs):
    # Consume and print the events as they stream in from the `resource`
    watch = k8s.watch.Watch2(client.request(**cargs))
    async for event in watch:
        print(f"{event.name} {event.obj.kind} {event.obj.metadata.name}")


async def main():
    # Create a client instance and load the credentials from ~/.kube/kubeconfig
    kubeconf = os.path.expanduser(os.environ.get('KUBECONFIG', '~/.kube/config'))
    client_config = k8s.configuration.Configuration()
    with warnings.catch_warnings(record=True):
        k8s.config.kube_config.load_kube_config(
            config_file=kubeconf,
            client_configuration=client_config,
            persist_config=False
        )
    client = k8s.clients.make_aiohttp_client(client_config)
    proxy = k8s.api_proxy.Proxy(client_config)

    # Namespaces and Pods are part of the K8s Core API.
    corev1 = k8s.CoreV1Api(proxy)

    # Deployments are part of the Extension API (still in beta).
    extv1beta = k8s.ExtensionsV1beta1Api(proxy)

    cargs_ns = corev1.list_namespace(timeout_seconds=5, watch=True)
    cargs_pods = corev1.list_pod_for_all_namespaces(timeout_seconds=5, watch=True)
    cargs_deploy = extv1beta.list_deployment_for_all_namespaces(timeout_seconds=5, watch=True)

    # Specify and dispatch the tasks.
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
