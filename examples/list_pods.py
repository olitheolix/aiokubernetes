"""Print all pod names in the cluster."""
import asyncio

import aiokubernetes as k8s


async def main():
    # Load the kubeconfig file specified in the KUBECONFIG environment
    # variable, or fall back to `~/.kube/config`.
    k8s.config.load_kube_config()

    # Pod queries are part of the Core API.
    v1 = k8s.api.CoreV1Api()
    ret = await v1.list_pod_for_all_namespaces()

    # Print the pod names.
    for i in ret.items:
        print(f"{i.metadata.namespace} {i.metadata.name}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
