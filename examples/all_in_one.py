"""Test all components of `aiokubernetes`.

This script will create two async tasks. One will watch the namespaces and the
other will create a deployment, log into the created Pod and issue some
commands and then delete the deployment again.

NOTE: This is both a demo and an integration test. See the other examples for
more concise feature demonstrations.
"""
import asyncio
import os

import aiohttp
import yaml

import aiokubernetes as k8s


async def watch_resource(resource, **kwargs):
    async for event in k8s.Watch(resource, **kwargs):
        print(f"{event.name} {event.obj.kind} {event.obj.metadata.name}")


async def create_deployment(api_client):
    img_alpine_34, img_alpine_35 = 'alpine:3.4', 'alpine:3.5'
    time_between_steps = 3

    # Create deployment.
    base_path = os.path.dirname(os.path.abspath(__file__))
    fname = os.path.join(base_path, 'create-deployment.yaml')
    body = yaml.safe_load(open(fname, 'r'))
    name, namespace = body['metadata']['name'], body['metadata']['namespace']
    img_orig = body['spec']['template']['spec']['containers'][0]['image']
    del fname

    body['spec']['template']['spec']['containers'][0]['image'] = img_alpine_34
    img_new = body['spec']['template']['spec']['containers'][0]['image']
    print(f'Replaced <{img_orig}> with <{img_new}>')

    # ---------- Create ----------
    k8s_v1beta = k8s.ExtensionsV1beta1Api(api_client)
    print(f'Creating deployment {name}...')
    resp = await k8s_v1beta.create_namespaced_deployment(body=body, namespace=namespace)
    assert isinstance(resp.http, aiohttp.client_reqrep.ClientResponse)
    print('****', resp.http.method, resp.http.status, resp.http.url)

    # ---------- Patch ----------
    # print(f'Patching deployment {name}...')
    # fname = os.path.join(base_path, 'patch-deployment.yaml')
    # body_patch = yaml.safe_load(open(fname, 'r'))
    # resp = await k8s_v1beta.patch_namespaced_deployment(
    #     name=name, namespace=namespace, body=body_patch)
    # await asyncio.sleep(time_between_steps)

    # ---------- Connect to Pod ----------
    print(f'\nConnecting to a login pod: ', end='', flush=True)
    for i in range(300):
        resp = await k8s.CoreV1Api(api_client).list_namespaced_pod(namespace)
        assert isinstance(resp.http, aiohttp.client_reqrep.ClientResponse)
        pods = resp.obj.items
        pods = [_ for _ in pods if _.metadata.name.lower().startswith('login')]
        pods = [_ for _ in pods if _.status.phase.lower() == 'running']

        if resp.http.status != 200 or len(pods) == 0:
            print('.', end='', flush=True)
            await asyncio.sleep(0.1)
            continue
        print('\n****', resp.http.method, resp.http.status, resp.http.url, '\n')

        if len(pods) > 1:
            print('Found multiple login pods')

        pod_name = pods[0].metadata.name
        print(f'Connecting to Pod <{pod_name}>')

        v1_ws = k8s.CoreV1Api(api_client=api_client)
        exec_command = [
            '/bin/sh', '-c',
            'echo This is stderr >&2; sleep 0s; echo This is stdout'
        ]
        websocket = await v1_ws.connect_get_namespaced_pod_exec(
            pod_name, namespace,
            command=exec_command,
            stderr=True, stdin=False,
            stdout=True, tty=False
        )
        assert isinstance(websocket.http, aiohttp.client._WSRequestContextManager)

        async with websocket.http as ws:
            async for msg in ws:
                print(f'  Websocket received: {msg.data}')
        break
    else:
        print('No login has entered "running" state yet - skip connection test')

    # ---------- Replace ----------
    img_orig = body['spec']['template']['spec']['containers'][0]['image']
    body['spec']['template']['spec']['containers'][0]['image'] = img_alpine_35
    img_new = body['spec']['template']['spec']['containers'][0]['image']
    print(f'Replaced <{img_orig}> with <{img_new}>')

    print(f'\nReplacing deployment {name}...')
    resp = await k8s_v1beta.replace_namespaced_deployment(
        name=name, namespace=namespace, body=body)
    assert isinstance(resp.http, aiohttp.client_reqrep.ClientResponse)
    print('****', resp.http.method, resp.http.status, resp.http.url)

    # ---------- Delete ----------
    await asyncio.sleep(time_between_steps)
    print(f'\nDeleting deployment {name}...')
    del_opts = k8s.V1DeleteOptions(
        api_version='v1', kind='DeleteOptions', grace_period_seconds=0,
        propagation_policy='Foreground',
    )
    resp = await k8s_v1beta.delete_namespaced_deployment(
        name=name, namespace=namespace, body=del_opts)
    assert isinstance(resp.http, aiohttp.client_reqrep.ClientResponse)
    print('****', resp.http.method, resp.http.status, resp.http.url)

    print('------------ End of Demo ------------')


async def setup():
    # Create client API instances (Websocket and Http).
    api_client = k8s.config.new_client_from_config()

    # Specify and dispatch the tasks.
    tasks = [
        create_deployment(api_client),
        watch_resource(k8s.CoreV1Api(api_client).list_namespace, timeout_seconds=1),
    ]
    await asyncio.gather(*tasks)

    print('\nShutting down')
    await api_client.session.close()


def main():
    # Setup event loop and setup the program.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.ensure_future(setup()))
    loop.close()


if __name__ == '__main__':
    main()
