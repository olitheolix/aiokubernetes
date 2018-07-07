"""Watch all namespaces in two clusters."""
import argparse
import asyncio

import aiokubernetes as k8s


async def watch_resource(cluster_name, resource, **kwargs):
    async for event in k8s.Watch(resource, **kwargs):
        print(f"{event.name} {event.obj.kind} {event.obj.metadata.name}")


async def start(kubeconf_a, kubeconf_b):
    # Create client API instances to each cluster.
    api_client_a = k8s.config.new_client_from_config(kubeconf_a)
    api_client_b = k8s.config.new_client_from_config(kubeconf_b)

    # Specify and dispatch the tasks.
    tasks = [
        watch_resource("Cluster A: ", k8s.CoreV1Api(api_client_a).list_namespace),
        watch_resource("Cluster B: ", k8s.CoreV1Api(api_client_b).list_namespace),
    ]
    await asyncio.gather(*tasks)

    # Terminate the connection pool for a clean shutdown.
    await api_client_a.session.close()
    await api_client_b.session.close()


def main():
    # Read the two Kubeconfig files from the command line.
    parser = argparse.ArgumentParser(
        description=("You can use the same kubeconfig file twice if you only "
                     "have one cluster.")
    )
    parser.add_argument('kubeconfig_a', type=str, help='Path to kubeconfig file')
    parser.add_argument('kubeconfig_b', type=str, help='Path to kubeconfig file')
    args = parser.parse_args()

    # Setup the main task.
    task = start(args.kubeconfig_a, args.kubeconfig_b)

    # Setup event loop and setup the program.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(task))
    loop.close()


if __name__ == '__main__':
    main()
