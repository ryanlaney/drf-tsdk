import inspect
import logging
import re
from typing import Callable, Optional, Tuple, Type

from django.urls import reverse

from rest_framework import serializers
from rest_framework.response import Response

from .mappings import mappings
from .exceptions import DRFTypeScriptAPIClientException

_logger = logging.getLogger(f"drf-typescript-api-client.{__name__}")

__view_mappings = dict()
__mapping_overrides = dict()

_comment = "/** This file was generated automatically by drf-typescript-api-client. */"


def _default_handler(content): return _comment + "\n\n" + content


class TypeScriptFieldDefinition:
    def __init__(self, name, ts_type, is_optional=False, is_many=False, is_readonly=False, comment=None):
        self.name = name
        self.ts_type = ts_type
        self.is_optional = is_optional
        self.is_many = is_many
        self.is_readonly = is_readonly
        self.comment = comment


class TypeScriptEndpointDefinition:
    def __init__(self, url, args, method, query_serializer=None, request_serializer=None, response_serializer=None):
        self.url = url
        self.args = args
        self.method = method
        self.query_serializer = query_serializer
        self.request_serializer = request_serializer
        self.response_serializer = response_serializer


def tsapiclient(
    path: Tuple[str, ...],
    query_serializer: Optional[Type[serializers.Serializer]] = None,
    request_serializer: Optional[Type[serializers.Serializer]] = None,
    response_serializer: Optional[Type[serializers.Serializer]] = None
):
    """Any Django Rest Framework view with this decorator will be added to a
    dynamically-generated TypeScript file with the approprate TypeScript type interfaces.

    @tsapiclient(path=("foo", "list"), response=FooSerializer)
    @api_client(['GET'])
    def foo(request):
        pass
    """
    def decorator(view):
        global __view_mappings
        if len(path) == 0:
            raise DRFTypeScriptAPIClientException(
                "`path` must have at least one component")
        __view_mappings = _update_view_mappings(
            mappings=__view_mappings,
            path=path,
            view=view,
            query_serializer=query_serializer,
            request_serializer=request_serializer,
            response_serializer=response_serializer
        )
        return view

    return decorator


def _update_view_mappings(
    mappings: dict, path: Tuple[str, ...], view: Callable[..., Type[Response]],
    query_serializer: Optional[Type[serializers.Serializer]],
    request_serializer: Optional[Type[serializers.Serializer]],
    response_serializer: Optional[Type[serializers.Serializer]]
) -> dict:
    if path[0] not in mappings:
        if len(path) > 1:
            mappings[path[0]] = _update_view_mappings(
                mappings=dict(),
                path=path[1:],
                view=view,
                query_serializer=query_serializer,
                request_serializer=request_serializer,
                response_serializer=response_serializer
            )
        else:
            mappings[path[0]] = TypeScriptEndpointDefinition(
                # url=reverse(view),
                url="/api/v1/test",
                args=[key for key in inspect.signature(
                    view).parameters.keys() if key not in ('self', 'request', )],
                method="GET",
                query_serializer=query_serializer,
                request_serializer=request_serializer,
                response_serializer=response_serializer
            )
    elif isinstance(mappings[path[0]], TypeScriptEndpointDefinition):
        return mappings
    elif isinstance(mappings[path[0]], dict):
        mappings[path[0]] = _update_view_mappings(
            mappings=mappings[path[0]],
            path=path[1:],
            view=view,
            query_serializer=query_serializer,
            request_serializer=request_serializer,
            response_serializer=response_serializer
        )
    else:
        print(mappings[path[0]])
        raise DRFTypeScriptAPIClientException("An unknown error occurred")
    return mappings


def _get_serializer_definition(serializer: Type[serializers.Serializer]) -> str:
    _serializer = serializer
    print(dir(_serializer))
    if isinstance(_serializer, serializers.ListSerializer):
        print("FOUDN LIST SERIALIZER: ", str(_serializer))
        _serializer = _serializer.child
        print("LIST SERIALIZER CHILD: ", str(_serializer))

    if not isinstance(_serializer, serializers.Serializer):
        _serializer = _serializer()

    if hasattr(_serializer, 'get_fields'):
        _logger.info("Getting serializer definition for '%s'",
                     type(_serializer).__name__)
        drf_fields = _serializer.get_fields().items()
    else:
        _logger.info("Getting serializer definition for '%s'",
                     _serializer.__name__)
        drf_fields = _serializer._declared_fields.items()

    ts_fields = []
    for key, value in drf_fields:
        ts_fields.append(_get_field_definition(key, value, serializer))
        # if value.read_only or not value.required:
        #     op = '?:'
        # else:
        #     op = ':'
        # if value.help_text:
        #     ts_fields.append(f"/** {value.help_text} */")
        # ts_fields.append(f"{ts_field[0]}{op} {ts_field[1]};")
        # collapsed_fields = '\n'.join(ts_fields)
    # return "{\n%s\n}" % collapsed_fields
    return ts_fields


def _get_field_definition(field_name: str, field, serializer: Type[serializers.Serializer]) -> Tuple[str, str]:
    '''
    Generates and returns a tuple representing the Typescript field name and Type.
    '''
    if hasattr(field, 'child'):
        is_many = True
        field_type = type(field.child)
    elif hasattr(field, 'child_relation'):
        is_many = True
        field_type = type(field.child_relation)
    else:
        is_many = False
        field_type = type(field)

    return TypeScriptFieldDefinition(
        name=field_name,
        ts_type=mappings.get(field_type, "any"),
        is_optional=not field.required,
        is_many=is_many,
        is_readonly=hasattr(field, "read_only"),
        comment=field.help_text
    )


def _get_ts_endpoint_text(key, value, indent):
    text = ("  " * indent) + f"{key}:"
    if isinstance(value, dict):
        text += " {"
        for _key, _value in value.items():
            text += "\n"
            text += _get_ts_endpoint_text(_key, _value, indent + 2)
        text += "\n" + ("  " * indent) + "},"
    else:
        args = ",".join([(arg + ": string") for arg in value.args])
        text += " (\n" + str("  " * (indent + 2)) \
            + (",\n" + str("  " * (indent + 2))).join([(arg + ": string") for arg in value.args]) \
            + ((",\n" + str("  " * (indent + 2))) if args != "" else "") \
            + "params: {\n" \
            + ("" if not value.query_serializer else str("  " * (indent + 4)) + "queryParams?: { foo: any }," + "\n") \
            + ("" if not value.request_serializer else str("  " * (indent + 4)) + "data?: { foo: any }" + "\n") \
            + str("  " * (indent + 4)) + "options?: any,\n" \
            + str("  " * (indent + 4)) + "onSuccess?(" \
            + ("" if not value.response_serializer else "{ foo: any }") \
            + "): void,\n" \
            + str("  " * (indent + 4)) + "onError?(error: any): void\n" \
            + str("  " * (indent + 2)) + "},\n" \
            + str("  " * indent) + ") : void => {\n" \
            + str("  " * (indent + 2)) + 'fetch("/api/v1/test", {\n' \
            + str("  " * (indent + 4)) + 'method: "GET",\n' \
            + ("" if not value.request_serializer else str("  " * (indent + 4)) + 'body: params.data,\n') \
            + str("  " * (indent + 4)) + "...params.options,\n" \
            + str("  " * (indent + 2)) + "})\n" \
            + str("  " * (indent + 4)) + ".then((response) => response.json())\n" \
            + str("  " * (indent + 4)) + ".then((result) => params.onSuccess && params.onSuccess(result))\n" \
            + str("  " * (indent + 4)) + ".catch((error) => params.onError && params.onError(error));\n" \
            + str("  " * indent) + "},"
    return text


def _get_api_client(api_name: str, handler: Optional[Callable[[str], str]]) -> str:
    """
    Generates the TypeScript API Client documentation text.
    """
    if re.match(r"[^0-9A-Za-z_]", api_name):
        raise DRFTypeScriptAPIClientException(
            "`class_name` may only contain alphanumeric characters,")
    if re.match(r"[0-9]", api_name[0]):
        raise DRFTypeScriptAPIClientException(
            "`class_name` must not begin with a number.")

    print(__view_mappings)
    body = str(__view_mappings)
    content = ""
    sep = ""
    for key, value in __view_mappings.items():
        content += sep
        content += _get_ts_endpoint_text(key, value, 2)
        sep = "\n"

    output = f"const {api_name} = {{\n{ content }\n}};\n\nexport default {api_name};\n"
    if handler is not None:
        output = handler(output)
    return output


def generate_api_client(
    output_path: str, api_name: str = "API", handler: Optional[Callable[[str], str]] = _default_handler
) -> None:
    """Generates the TypeScript API Client .ts file

    :param str api_name: The name of the API object
    :param handler: If provided, processes the API documentation before writing the file

    Ex:
    comment='// this is a comment'
    generate_api_client(output_path='/path/to/api.ts', api_name='MyAPIClass', handler=lambda docs: comment + '\\n\\n' + docs)
    """
    with open(output_path, 'w') as output_file:
        api_client_text = _get_api_client(api_name=api_name, handler=handler)
        output_file.write(api_client_text)
