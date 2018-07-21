"""Print the name of all pods in the cluster."""
import asyncio
import ssl

import aiohttp
import requests

import aiokubernetes as k8s


async def main():
    # Load default kubeconfig file and create an aiohttp client instance.
    config = k8s.utils.load_config(warn=False)

    # --- Compile the API request parameters to list all Pods in the cluster ---

    # `cargs` is a dict with keys for 'data' (body), 'headers', 'method' (eg
    # GET, POST), and 'url'. This encompasses the necessary information _any_
    # REST client would need to successfully list the K8s namespaces.
    cargs = k8s.api.CoreV1Api(k8s.api_proxy.Proxy(config)).list_namespace(watch=False)

    # --- Setup the AioHttp client ---
    connector = aiohttp.TCPConnector(
        limit=4,
        ssl_context=ssl.create_default_context(cafile=config.ssl_ca_cert),
        verify_ssl=True,
    )
    client_aiohttp = aiohttp.ClientSession(connector=connector)

    # --- Setup the Requests client ---
    client_requests = requests.Session()
    client_requests.verify = config.ssl_ca_cert

    # --- Ask with asynchronous client ---
    ret = await client_aiohttp.request(**cargs)
    assert ret.status == 200
    text_async = await ret.text()
    await client_aiohttp.close()

    # --- Ask with synchronous client ---
    ret = client_requests.request(**cargs, verify=config.ssl_ca_cert)
    assert ret.status_code == 200
    text_sync = ret.text

    # --- Verify that both clients returned the same data ---
    assert text_sync == text_async

    # Optional: wrap the raw (byte encoded) response into a Swagger object.
    obj = k8s.swagger.unpack(text_sync.encode('utf8'))

    # Print the pod names.
    for i in obj.items:
        print(f"{i.metadata.namespace} {i.metadata.name}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
