import ssl

import aiohttp
import requests


def get_aiohttp(config):
    assert config.ssl_ca_cert is not None
    ca_certs = config.ssl_ca_cert
    ssl_context = ssl.create_default_context(cafile=ca_certs)

    connector = aiohttp.TCPConnector(
        limit=4,
        ssl_context=ssl_context,
        verify_ssl=config.verify_ssl
    )
    return aiohttp.ClientSession(connector=connector)


def get_requests(config):
    assert config.ssl_ca_cert is not None

    sess = requests.Session()
    sess.verify = config.ssl_ca_cert
    return sess
