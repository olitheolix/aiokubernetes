"""Watch multiple K8s event streams without threads."""
import asyncio

import aiokubernetes as k8s


async def watch_resource(resource, **kwargs):
    # Consume and print the events as they stream in from the `resource`
    async for event in k8s.Watch(resource, **kwargs):
        print(f"{event.name} {event.obj.kind} {event.obj.metadata.name}")


async def main():
    # Create a client instance and load the credentials from ~/.kube/kubeconfig
    api_client = k8s.config.new_client_from_config()

    # Namespaces and Pods are part of the K8s Core API.
    corev1 = k8s.CoreV1Api(api_client)

    # Deployments are part of the Extension API (still in beta).
    extv1beta = k8s.ExtensionsV1beta1Api(api_client)

    # Specify and dispatch the tasks.
    tasks = [
        watch_resource(corev1.list_namespace, timeout_seconds=5),
        watch_resource(corev1.list_pod_for_all_namespaces, timeout_seconds=5),
        watch_resource(extv1beta.list_deployment_for_all_namespaces, timeout_seconds=5),
    ]
    await asyncio.gather(*tasks)

    # Terminate the connection pool for a clean shutdown.
    await api_client.session.close()


if __name__ == '__main__':
    # Setup event loop and start the program.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(main()))
    loop.close()
