"""Create and delete the namespace <foo>."""
import asyncio

import aiokubernetes as k8s


async def main():
    # Create a client instance and load the credentials from ~/.kube/kubeconfig
    config = k8s.utils.load_config(warn=False)
    client = k8s.clients.make_aiohttp_client(config)
    proxy = k8s.api_proxy.Proxy(config)

    # Name of the namespace.
    name = 'aiokubernetes-test'

    # ----------------------------------------------------------------------
    # Create the namespace.
    # ----------------------------------------------------------------------
    manifest = {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {'name': name},
    }
    cargs = k8s.api.CoreV1Api(proxy).create_namespace(body=manifest)
    ret = await client.request(**cargs)
    if ret.status == 201:
        print(f'Namespace <{name}> created')
    elif ret.status == 409:
        print(f'Namespace <{name}> already exists')
    else:
        print(f'Error {ret.status}')
        print(await ret.text())

    # ----------------------------------------------------------------------
    # When we try to create the same namespace a second time it must fail.
    # ----------------------------------------------------------------------
    ret = await client.request(**cargs)
    assert ret.status == 409
    print(f'Namespace <{name}> already exists')

    # ----------------------------------------------------------------------
    # Delete the namespace.
    # ----------------------------------------------------------------------
    delete_opts = k8s.V1DeleteOptions(
        api_version='v1',
        kind='DeleteOptions',
        grace_period_seconds=0,
        propagation_policy='Foreground',
    )
    cargs = k8s.api.CoreV1Api(proxy).delete_namespace(name=name, body=delete_opts)
    ret = await client.request(**cargs)
    assert ret.status == 200
    print(f'Namespace <{name}> deleted')

    # Close all pending connections.
    await client.close()


if __name__ == '__main__':
    # Setup event loop and start the program.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(main()))
    loop.close()
