"""Create and delete the namespace <foo>."""
import asyncio

import aiokubernetes as k8s


async def main():
    # Create a client instance and load the credentials from ~/.kube/kubeconfig
    api_client = k8s.config.new_client_from_config()
    api_v1 = k8s.CoreV1Api(api_client)

    # Name of the namespace.
    name = 'foo'

    # ----------------------------------------------------------------------
    # Create the namespace.
    # ----------------------------------------------------------------------
    manifest = {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {'name': name},
    }
    resp = await api_v1.create_namespace(body=manifest)
    if resp.http.status == 201:
        print(f'Namespace <{name}> created')
    elif resp.http.status == 409:
        print(f'Namespace <{name}> already exists')
    else:
        print(f'Error {resp.http.status}')
        print(resp.http.text)

    # ----------------------------------------------------------------------
    # When we try to create the same namespace a second time it must fail.
    # ----------------------------------------------------------------------
    resp = await api_v1.create_namespace(body=manifest)
    assert resp.http.status == 409
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
    resp = await api_v1.delete_namespace(name=name, body=delete_opts)
    assert resp.http.status == 200
    print(f'Namespace <{name}> deleted')

    # Close all pending connections.
    await api_client.close()


if __name__ == '__main__':
    # Setup event loop and start the program.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(main()))
    loop.close()
