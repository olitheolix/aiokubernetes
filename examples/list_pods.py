"""Print the name of all pods in the cluster."""
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
