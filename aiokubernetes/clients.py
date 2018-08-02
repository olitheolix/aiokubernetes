import ssl

import aiohttp
import requests


def get_aiohttp(config):
    """Return a configured AioHttp client.

    NOTE: this is a convenience function only to reduce boiler plate.

    Inputs:
        config: k8s.configuration.Config instance
            Typically you pass it whatever `k8s.utils.load_config()` returns.

    Returns:
        Requests session instance.
    """
    ssl_context = ssl.create_default_context(cafile=config.ssl_ca_cert)
    if config.cert_file:
        ssl_context.load_cert_chain(config.cert_file, keyfile=config.key_file)

    connector = aiohttp.TCPConnector(
        limit=4,
        ssl_context=ssl_context,
        verify_ssl=config.verify_ssl  # Bool, usually True.
    )
    return aiohttp.ClientSession(connector=connector)


def get_requests(config):
    """Return a configured Requests client.

    NOTE: this is a convenience function only to reduce boiler plate.

    Inputs:
        config: k8s.configuration.Config instance
            Typically you pass it whatever `k8s.utils.load_config()` returns.

    Returns:
        Requests session instance.
    """
    sess = requests.Session()
    sess.verify = config.ssl_ca_cert
    return sess
