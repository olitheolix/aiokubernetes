import copy
import datetime
import json
from urllib.parse import urlencode


class Proxy:
    def __init__(self, config, *args, **kwargs):
        self.config = config
        self.args, self.kwargs = args, kwargs

    def call_api(self, *args, **kwargs):
        # print(args, kwargs.keys())
        # print('Query params:', kwargs.get('query_params', None))
        args = tuple(args)
        kwargs = copy.deepcopy(kwargs)

        resource_path, method, path_params, query_params, header_params = args
        kwargs = build_url(
            self.config, resource_path, path_params, query_params,
            header_params, kwargs['post_params'], kwargs['auth_settings'], kwargs['body']
        )
        del args, resource_path, path_params, query_params, header_params

        headers = kwargs['headers']
        if 'Content-Type' not in headers:
            headers['Content-Type'] = 'application/json'

        client_args = {
            "headers": headers,
            "method": method,
            "timeout": 5 * 60,
            "url": kwargs['url'],
        }

        if len(kwargs['query_params']) > 0:
            client_args["url"] += '?' + urlencode(kwargs['query_params'])

        if kwargs['body'] is not None:
            client_args["data"] = json.dumps(kwargs['body'])

        return client_args

    @staticmethod
    def select_header_accept(accepts):
        """Returns `Accept` based on an array of accepts provided.

        :param: accepts: List of headers.
        :return: Accept (e.g. application/json).
        """
        if not accepts:
            return None

        accepts = [x.lower() for x in accepts]

        if 'application/json' in accepts:
            return 'application/json'
        else:
            return ', '.join(accepts)

    @staticmethod
    def select_header_content_type(content_types):
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


def build_url(config, resource_path, path_params, query_params, header_params,
              post_params, auth_settings, body):
    assert isinstance(header_params, dict)
    assert isinstance(path_params, dict)
    assert isinstance(query_params, (tuple, list))

    # Convert all Swagger models to Json compatible Python dicts.
    body = sanitize_for_serialization(body)
    header_params = dict(sanitize_for_serialization(header_params))
    path_params = dict(sanitize_for_serialization(path_params))
    post_params = dict(sanitize_for_serialization(post_params))
    query_params = sanitize_for_serialization(query_params)

    # Convert "/api/v1/namespace/{namespace}" -> "/api/v1/namespace/foo"
    # This is particularly easy to do because it utilises the same syntax as
    # the Python format strings.
    resource_path = resource_path.format(**path_params)

    # Convert [("limit", 5), ("command", ["ls", "pwd"])] to
    # [("limit", 5), ("command", "ls"), ("command", "pwd")]
    sane_query_params = []
    for k, v in query_params:
        if isinstance(v, (list, tuple)):
            sane_query_params.extend([(k, _) for _ in v])
        else:
            sane_query_params.append((k, v))
    query_params = sane_query_params
    del sane_query_params

    # auth setting
    update_params_for_auth(config, header_params, query_params, auth_settings)

    # Compile complete Request URL.
    url = config.host + resource_path

    kwargs = {
        'body': body,
        'headers': header_params,
        'post_params': post_params,
        'query_params': query_params,
        'url': url,
        '_request_timeout': 10
    }
    return kwargs


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

    fixup: rename this to swagger_to_json

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
        print('***', obj.attribute_map, obj.swagger_types)
        print(dir(obj))
        # Convert model obj to dict except attributes `swagger_types`,
        # `attribute_map` and attributes which value is not None. Convert
        # attribute name to json key in model definition for request.
        obj_dict = {obj.attribute_map[attr]: getattr(obj, attr)
                    for attr, _ in obj.swagger_types.items()
                    if getattr(obj, attr) is not None}

    return {k: sanitize_for_serialization(v) for k, v in obj_dict.items()}
