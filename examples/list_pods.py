"""Print the name of all pods in the cluster."""
import asyncio

import aiokubernetes as k8s


async def main():
    # Create a client instance and load the credentials from ~/.kube/kubeconfig
    config = k8s.utils.load_config(warn=False)
    client = k8s.clients.make_aiohttp_client(config)
    proxy = k8s.api_proxy.Proxy(config)

    # Ask for all Pods.
    cargs = k8s.api.CoreV1Api(proxy).list_namespace(watch=False)
    ret = await client.request(**cargs)

    # Ensure the API call to Kubernetes succeeded.
    assert ret.status == 200

    obj = k8s.swagger.unpack(await ret.read())

    # Print the pod names.
    for i in obj.items:
        print(f"{i.metadata.namespace} {i.metadata.name}")

    # Close all pending connections.
    await client.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
