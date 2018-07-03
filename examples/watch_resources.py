"""Watch multiple K8s event streams without threads."""
import asyncio

import aiokubernetes as k8s


async def watch_namespaces():
    v1 = k8s.api.CoreV1Api()
    async for event in k8s.watch.Watch(v1.list_namespace, timeout_seconds=1):
        etype, obj = event['type'], event['object']
        print(f"{etype} namespace {obj.metadata.name}")


async def watch_pods():
    v1 = k8s.api.CoreV1Api()
    async for event in k8s.watch.Watch(v1.list_pod_for_all_namespaces, timeout_seconds=1):
        evt, obj = event['type'], event['object']
        print(f"{evt} pod {obj.metadata.name} in NS {obj.metadata.namespace}")


def main():
    # Load the kubeconfig file specified in the KUBECONFIG environment
    # variable, or fall back to `~/.kube/config`.
    k8s.config.load_kube_config()

    # Define the tasks to watch namespaces and pods.
    tasks = [
        asyncio.ensure_future(watch_namespaces()),
        asyncio.ensure_future(watch_pods()),
    ]

    # Push tasks into event loop.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))
    loop.close()


if __name__ == '__main__':
    main()
