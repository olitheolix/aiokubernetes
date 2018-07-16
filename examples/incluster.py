"""Use service account credentials to list all pods in the cluster.

NOTE: must run inside a Pod with the correct service account credentials. See
`deploy-pod-with-sa.yaml` for an example to set this up.
"""
import asyncio

import aiokubernetes as k8s


async def main():
    # Assume we are inside a Pod and load its service account credentials.
    client_config = k8s.config.incluster_config.load_service_account_config()

    # Create a client with the service account credentials.
    api_client = k8s.api_client.ApiClient(configuration=client_config)

    # Ask for all Pods - no different than when running locally.
    v1 = k8s.api.CoreV1Api(api_client)
    ret = await v1.list_pod_for_all_namespaces()
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
