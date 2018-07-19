import datetime
import json
import re

from dateutil.parser import parse

import aiokubernetes.models
from aiokubernetes.rest import ApiException

NATIVE_TYPES_MAPPING = {
    'int': int,
    'long': int,  # noqa: F821
    'float': float,
    'str': str,
    'bool': bool,
    'date': datetime.date,
    'datetime': datetime.datetime,
    'object': object,
}


def deserialize(data, klass):
    """Deserializes dict, list, str into an object.

    :param: data: dict, list or str.
    :param: klass: class literal, or string of class name.

    :return: object.
    """
    if data is None:
        return None

    if type(klass) == str:
        # Recursively unpack types like "list[V1ContainerStatus]".
        if klass.startswith('list['):
            # "list[V1ContainerStatus]" -> "V1ContainerStatus"
            sub_kls = re.match('list\[(.*)\]', klass).group(1)
            return [deserialize(sub_data, sub_kls) for sub_data in data]

        # Recursively unpack types like "dict(str, str)".
        if klass.startswith('dict('):
            # "dict(str, int)" -> "int"
            sub_kls = re.match('dict\(([^,]*), (.*)\)', klass).group(2)
            # fixup: is this a bug? The key will not get de-serialised, only
            # the value.
            return {k: deserialize(v, sub_kls) for k, v in data.items()}

        # convert str to class
        if klass in NATIVE_TYPES_MAPPING:
            klass = NATIVE_TYPES_MAPPING[klass]
        elif hasattr(aiokubernetes.models, klass):
            klass = getattr(aiokubernetes.models, klass)
        else:
            assert False, f'Unknown type <{klass}>'

    # Convert `data` to whatever type `klass` says it is. The only
    # interesting case is where `klass` is not a native Python type like
    # `str` but is a class itself and has a `swagger_types` attributes. If
    # it does it can be parsed into a Swagger generated container class.
    if hasattr(klass, 'swagger_types'):
        return deserialize_model(data, klass)
    elif klass == datetime.date:
        return deserialize_date(data)
    elif klass == datetime.datetime:
        return deserialize_datatime(data)
    else:
        # No further processing required.
        return data


def deserialize_date(string):
    """Deserializes string to date.

    :param: string: str.
    :return: date.
    """
    try:
        return parse(string).date()
    except ValueError:
        raise ApiException(
            status=0,
            reason=f"Failed to parse `{string}` as datetime object",
        )


def deserialize_datatime(string):
    """Deserializes string to datetime.

    The string should be in iso8601 datetime format.

    :param: string: str.
    :return: datetime.
    """
    try:
        return parse(string)
    except ValueError:
        raise ApiException(
            status=0,
            reason=f"Failed to parse `{string}` as datetime object",
        )


def deserialize_model(data, klass):
    """Deserializes list or dict to model.

    :param: data: dict, list.
    :param: klass: class literal.
    :return: model object.
    """

    if getattr(klass, 'swagger_types', None) is None:
        # fixup: debug log message about unrecognised Swagger type?
        return None

    # This is unusual but has happened when there was an error.
    # fixup: reproduce with all_in_one (run it twice back-to-back, then the
    # error will materialise the second time, most likely because the
    # deployment cannot be created since it has not been deleted yet from
    # the previous run - this is speculation at this point).
    if isinstance(data, str):
        return klass()

    # Since we are parsing JSON data returned from K8s it must be either a
    # dict or a list (K8s never returns just a scalar).
    assert isinstance(data, (list, dict)), f'Bug: invalid type <{type(data)}>'

    # Do nothing unless we have data and a Swagger type.
    kwargs = {}
    if all((data, klass.swagger_types)):
        for attr, attr_type in klass.swagger_types.items():
            try:
                value = data[klass.attribute_map[attr]]
            except KeyError:
                # fixup: log message here.
                pass
            else:
                # Recursively de-serialise the object.
                kwargs[attr] = deserialize(value, attr_type)

    # Return an instance of the de-serialised class.
    return klass(**kwargs)


def determine_type(api_version: str, kind: str):
    """Return name of Swagger model for this `api_version` and `kind`.

    Example: ('Extensions/v1beta1', 'Deployment') -> 'ExtensionsV1beta1Deployment'

    This is useful to convert the K8s Json response into a Swagger generated
    Python object. The `api_version` and `kind` should be copied verbatime
    (including capitalisation) from the manifests K8s returns.

    Input:
        api_version: str
            As returned by K8s API, eg `V1`, `Extensions/v1beta1` ...
        kind: str
            As returned by K8s API, eg `Deployment`, `Namespace` ...

    Returns:
        str: Name of Swagger model that can wrap the specified data.

    """
    # Split the API name by '/', eg Extensions/v1beta1 -> (Extensions,
    # v1beta1). Then capitalize the first character only, leaving all other
    # characters untouched. This is the scheme Swagger uses for its classes.
    words = api_version.split('/')
    words = [word[0].capitalize() + word[1:] for word in words]
    api = str.join('', words)

    # Capitalise the first character of the `kind` and compile the Swagger name.
    kind = kind[0].capitalize() + kind[1:]
    klass = f'{api}{kind}'

    # Capitalise trailing `list` to match the Swagger class name.
    if klass.endswith('list'):
        klass = str.join('', klass.rpartition('list')[0]) + 'List'
    return klass


def wrap(data: bytes):
    """Return the K8s response `data` in a `WatchResponse` tuple.

    """
    try:
        line = data.decode('utf8')
        k8s_obj = json.loads(line)
    except UnicodeDecodeError:
        # fixup: log message
        return None
    except json.decoder.JSONDecodeError:
        # fixup: log message
        print('json error')
        return None
    except KeyError:
        print('key error')
        # fixup: log message
        return None

    api, kind = k8s_obj['apiVersion'], k8s_obj['kind']
    api = str.join('', [_.capitalize() for _ in api.split('/')])
    kind = kind.capitalize()
    klass = f'{api}{kind}'
    if klass.endswith('list'):
        klass = str.join('', klass.rpartition('list')[0]) + 'List'
    print(api, kind, klass)

    return deserialize(data=k8s_obj, klass=klass)
