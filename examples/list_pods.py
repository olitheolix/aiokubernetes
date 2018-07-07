"""Print the name of all pods in the cluster."""
import asyncio

import aiokubernetes as k8s


async def main():
    # Create a client instance and load the credentials from ~/.kube/kubeconfig
    api_client = k8s.config.new_client_from_config()

    # Ask for all Pods.
    v1 = k8s.api.CoreV1Api(api_client)
    ret = await v1.list_pod_for_all_namespaces()

    # Ensure the API call to Kubernetes succeeded.
    assert ret.http.status == 200

    # Print the pod names.
    for i in ret.obj.items:
        print(f"{i.metadata.namespace} {i.metadata.name}")

    # Close all pending connections.
    await api_client.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
