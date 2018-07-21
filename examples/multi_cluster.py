"""Watch all namespaces in two clusters."""
import argparse
import asyncio

import aiokubernetes as k8s


async def watch_resource(client, cargs):
    """Consume and print the events as they stream in."""

    # Use helper class to consume the K8s events via an async iterator.
    watch = k8s.watch.AioHttpClientWatch(client.request(**cargs))
    async for event in watch:
        print(f"{event.name} {event.obj.kind} {event.obj.metadata.name}")


async def start(kubeconf_a, kubeconf_b):
    # Create client API instances to each cluster.
    config_a = k8s.utils.load_config(kubeconf_a, warn=False)
    config_b = k8s.utils.load_config(kubeconf_b, warn=False)
    client_a = k8s.clients.get_aiohttp(config_a)
    client_b = k8s.clients.get_aiohttp(config_b)
    proxy_a = k8s.api_proxy.Proxy(config_a)
    proxy_b = k8s.api_proxy.Proxy(config_b)

    cargs_ns_a = k8s.CoreV1Api(proxy_a).list_namespace(timeout_seconds=5, watch=True)
    cargs_ns_b = k8s.CoreV1Api(proxy_b).list_namespace(timeout_seconds=5, watch=True)

    # Specify and dispatch the tasks.
    tasks = [
        watch_resource(client_a, cargs_ns_a),
        watch_resource(client_b, cargs_ns_b),
    ]
    await asyncio.gather(*tasks)

    # Close all pending connections.
    await client_a.close()
    await client_b.close()


def main():
    # Read the two Kubeconfig files from the command line.
    parser = argparse.ArgumentParser(
        description=("You can use the same kubeconfig file twice if you only "
                     "have one cluster.")
    )
    parser.add_argument(
        'kubeconfig_a', type=str, help='Path to kubeconfig file'
    )
    parser.add_argument(
        'kubeconfig_b', type=str, help='Path to kubeconfig file'
    )
    args = parser.parse_args()

    # Setup the main task.
    task = start(args.kubeconfig_a, args.kubeconfig_b)

    # Setup event loop and setup the program.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(task))
    loop.close()


if __name__ == '__main__':
    main()
