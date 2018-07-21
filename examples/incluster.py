"""Use service account credentials to list all pods in the cluster.

NOTE: must run inside a Pod with the correct service account credentials. See
`manifests/deploy-pod-with-sa.yaml` for an example to set this up.
"""
import asyncio

import aiokubernetes as k8s


async def main():
    # Assume we are inside a Pod. Load its service account credentials.
    config = k8s.config.incluster_config.load()
    client = k8s.clients.get_aiohttp(config)
    proxy = k8s.api_proxy.Proxy(config)

    # Ask for all Pods in the cluster.
    cargs = k8s.api.CoreV1Api(proxy).list_pod_for_all_namespaces()
    ret = await client.request(**cargs)
    assert ret.http.status == 200

    # Print the pod names.
    for i in ret.obj.items:
        print(f"{i.metadata.namespace} {i.metadata.name}")

    # Close all pending connections.
    await client.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
