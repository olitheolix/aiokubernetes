import ssl

import aiohttp


def get_aiohttp(configuration):
    assert configuration.ssl_ca_cert is not None
    ca_certs = configuration.ssl_ca_cert
    ssl_context = ssl.create_default_context(cafile=ca_certs)

    connector = aiohttp.TCPConnector(
        limit=4,
        ssl_context=ssl_context,
        verify_ssl=configuration.verify_ssl
    )
    return aiohttp.ClientSession(connector=connector)
