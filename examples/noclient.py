"""Print the name of all pods in the cluster."""
import asyncio
import json

import aiokubernetes as k8s


async def watch(request):
    ret = await request
    while True:
        line = await ret.content.readline()
        if len(line) == 0:
            break
        print(json.loads(line)['object']['metadata']['name'])
    print('done')


async def main():
    # Create a client instance and load the credentials from ~/.kube/kubeconfig
    config = k8s.utils.load_config(warn=False)
    client = k8s.clients.get_aiohttp(config)
    proxy = k8s.api_proxy.Proxy(config)

    cargs = k8s.api.CoreV1Api(proxy).list_namespace(watch=False)
    ret = await client.request(**cargs)
    obj = k8s.swagger.unpack(await ret.read())
    for item in obj.items:
        print(item.metadata.name)
    ret.close()

    print('\n----\n')
    cargs = k8s.api.CoreV1Api(proxy).list_namespace(watch=True, timeout_seconds=3)
    await watch(client.request(**cargs))

    print('\n----\n')
    extv1 = k8s.ExtensionsV1beta1Api(proxy)
    cargs = extv1.list_deployment_for_all_namespaces(watch=True, timeout_seconds=3)
    mywatch = k8s.watch.AioHttpClientWatch(client.request(**cargs))
    async for w in mywatch:
        print(w.obj.kind, w.obj.metadata.namespace, w.obj.metadata.name)

    await client.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
