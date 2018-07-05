"""Print the name of all pods in the cluster."""
import asyncio

import aiokubernetes as k8s


async def main():
    # Create an API client instance based on the file specified in the
    # KUBECONFIG environment variable (fall back `~/.kube/config` if KUBECONFIG
    # variable does not exist).
    api_client = k8s.config.new_client_from_config()

    # Ask for all Pods.
    v1 = k8s.api.CoreV1Api(api_client)
    ret = await v1.list_pod_for_all_namespaces()

    # Ensure the API call to Kubernetes succeeded.
    assert ret.http.status == 200

    # Print the pod names.
    for i in ret.parsed.items:
        print(f"{i.metadata.namespace} {i.metadata.name}")

    # Terminate the connection pool for a clean shutdown.
    await api_client.session.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
