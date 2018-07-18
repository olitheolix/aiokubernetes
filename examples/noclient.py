"""Print the name of all pods in the cluster."""
import asyncio
import datetime
import json
import os
import ssl
import warnings

import aiohttp
import aiokubernetes as k8s
from urllib.parse import quote, urlencode


class ApiDummy:
    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.args, self.kwargs = args, kwargs

    def call_api(self, *args, **kwargs):
        # print(args, kwargs.keys())
        # print('Query params:', kwargs.get('query_params', None))
        return convert(self.config, args, kwargs)

    def select_header_accept(self, accepts):
        """Returns `Accept` based on an array of accepts provided.

        :param: accepts: List of headers.
        :return: Accept (e.g. application/json).
        """
        if not accepts:
            return

        accepts = [x.lower() for x in accepts]

        if 'application/json' in accepts:
            return 'application/json'
        else:
            return ', '.join(accepts)

    def select_header_content_type(self, content_types):
        """Returns `Content-Type` based on an array of content_types provided.

        :param: content_types: List of content-types.
        :return: Content-Type (e.g. application/json).
        """
        if not content_types:
            return 'application/json'

        content_types = [x.lower() for x in content_types]

        if 'application/json' in content_types or '*/*' in content_types:
            return 'application/json'
        else:
            return content_types[0]


def make_client(configuration):
    assert configuration.ssl_ca_cert is not None
    ca_certs = configuration.ssl_ca_cert
    ssl_context = ssl.create_default_context(cafile=ca_certs)

    connector = aiohttp.TCPConnector(
        limit=4,
        ssl_context=ssl_context,
        verify_ssl=configuration.verify_ssl
    )
    return aiohttp.ClientSession(connector=connector)


def build_url(config, resource_path, path_params, query_params, header_params,
              post_params, auth_settings, body):
    # header parameters
    header_params = header_params or {}
    if header_params:
        header_params = dict(sanitize_for_serialization(header_params))

    # path parameters
    if path_params:
        path_params = dict(sanitize_for_serialization(path_params))
        for k, v in path_params.items():
            # specified safe chars, encode everything
            resource_path = resource_path.replace(
                '{%s}' % k,
                quote(str(v), safe=config.safe_chars_for_path_param)
            )

    # query parameters
    if query_params:
        tmp = sanitize_for_serialization(query_params)
        query_params = []
        for k, v in tmp:
            if isinstance(v, (list, tuple)):
                query_params.extend([(k, _) for _ in v])
            else:
                query_params.append((k, v))
        #query_params = [(quote(k), quote(str(v))) for k, v in query_params]
        print(query_params)

    # post parameters
    if post_params:
        post_params = dict(sanitize_for_serialization(post_params))

    # auth setting
    update_params_for_auth(config, header_params, query_params, auth_settings)

    # body
    if body:
        body = sanitize_for_serialization(body)

    # request url
    url = config.host + resource_path

    kwargs = {
        'query_params': query_params,
        'headers': header_params,
        'post_params': post_params,
        'body': body,
        '_request_timeout': 10
    }

    # Make the request and wait for a response.
    return (url, kwargs)


def update_params_for_auth(config, headers, querys, auth_settings):
    """Updates header and query params based on authentication setting.

    :param: headers: Header parameters dict to be updated.
    :param: querys: Query parameters tuple list to be updated.
    :param: auth_settings: Authentication setting identifiers list.
    """
    if not auth_settings:
        return

    for auth in auth_settings:
        auth_setting = config.auth_settings().get(auth)
        if auth_setting:
            if not auth_setting['value']:
                continue
            elif auth_setting['in'] == 'header':
                headers[auth_setting['key']] = auth_setting['value']
            elif auth_setting['in'] == 'query':
                querys.append((auth_setting['key'], auth_setting['value']))
            else:
                raise ValueError(
                    'Authentication token must be in `query` or `header`'
                )


def sanitize_for_serialization(obj):
    """Builds a JSON POST object.

    If obj is None, return None.
    If obj is str, int, long, float, bool, return directly.
    If obj is datetime.datetime, datetime.date
        convert to string in iso8601 format.
    If obj is list, sanitize each element in the list.
    If obj is dict, return the dict.
    If obj is swagger model, return the properties dict.

    :param: obj: The data to serialize.
    :return: The serialized form of data.
    """
    PRIMITIVE_TYPES = (float, bool, bytes, int, str)
    if obj is None:
        return None
    elif isinstance(obj, PRIMITIVE_TYPES):
        return obj
    elif isinstance(obj, list):
        return [sanitize_for_serialization(sub_obj) for sub_obj in obj]
    elif isinstance(obj, tuple):
        return tuple(sanitize_for_serialization(sub_obj) for sub_obj in obj)
    elif isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()

    if isinstance(obj, dict):
        obj_dict = obj
    else:
        # Convert model obj to dict except attributes `swagger_types`,
        # `attribute_map` and attributes which value is not None. Convert
        # attribute name to json key in model definition for request.
        obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
                    for attr, _ in obj.swagger_types.items()
                    if getattr(obj, attr) is not None}

    return {k: sanitize_for_serialization(v) for k, v in obj_dict.items()}


def convert(config, args, kwargs):
    import copy
    kwargs = copy.deepcopy(kwargs)
    resource_path, method, path_params, query_params, header_params = args
    url, kwargs = build_url(
        config, resource_path, path_params, query_params,
        header_params, kwargs['post_params'], kwargs['auth_settings'], kwargs['body']
    )
    del args, resource_path, path_params, query_params, header_params

    headers = kwargs['headers']
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'

    client_args = {
        "method": method,
        "url": url,
        "timeout": 5 * 60,
        "headers": headers
    }

    query_params = kwargs.get('query_params', tuple())

    if len(query_params) > 0:
        client_args["url"] += '?' + urlencode(query_params)

    if kwargs['body'] is not None:
        body = json.dumps(kwargs['body'])
        client_args["data"] = body
    return client_args


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
    client = make_client(client_config)

    api_dummy = ApiDummy(client_config)
    cargs = k8s.api.CoreV1Api(api_dummy).list_namespace(watch=False)
    ret = await client.request(**cargs)
    obj = k8s.watch.watch.Watch2.unmarshal_response(await ret.read())
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
