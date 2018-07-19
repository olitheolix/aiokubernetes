"""Print the name of all pods in the cluster."""
import asyncio
import json
import os
import warnings

import aiokubernetes as k8s


async def watch(request):
    ret = await request
    while True:
        line = await ret.content.readline()
        if len(line) == 0:
            break
        print(json.loads(line)['object']['metadata']['name'])
    print('done')

    # async for event in k8s.Watch(resource, **kwargs):
    #     print(f"{event.name} {event.obj.kind} {event.obj.metadata.name}")


async def main():
    kubeconf = os.path.expanduser(os.environ.get('KUBECONFIG', '~/.kube/config'))
    client_config = k8s.configuration.Configuration()
    with warnings.catch_warnings(record=True):
        k8s.config.kube_config.load_kube_config(
            config_file=kubeconf,
            client_configuration=client_config,
            persist_config=False
        )
    client = k8s.clients.make_aiohttp_client(client_config)

    api_dummy = k8s.api_proxy.Proxy(client_config)
    cargs = k8s.api.CoreV1Api(api_dummy).list_namespace(watch=False)
    ret = await client.request(**cargs)
    obj = k8s.swagger.wrap(await ret.read())
    for item in obj.items:
        print(item.metadata.name)
    ret.close()

    print('\n----\n')
    cargs = k8s.api.CoreV1Api(api_dummy).list_namespace(watch=True, timeout_seconds=3)
    await watch(client.request(**cargs))

    print('\n----\n')
    cargs = k8s.ExtensionsV1beta1Api(api_dummy).list_deployment_for_all_namespaces(watch=True, timeout_seconds=10)
    mywatch = k8s.watch.watch.Watch2(client.request(**cargs))
    async for w in mywatch:
        print(w.obj.kind, w.obj.metadata.namespace, w.obj.metadata.name)

    await client.close()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
