import logging
import re
from typing import Callable, Optional

import jsbeautifier

from .helpers import TypeScriptEndpointDefinition, TypeScriptInterfaceDefinition
from .exceptions import DRFTypeScriptAPIClientException
from .drf_to_ts import DRFViewMapper, DRFSerializerMapper

_logger = logging.getLogger(f"drf-typescript-api-client.{__name__}")


def _default_processor(content):
    return "/** This file was generated automatically by drf-typescript-api-client. */" + "\n\n" + content


def _get_ts_interface_text(value) -> str:
    text = f"{'export ' if value.should_export else ''} interface {value.name} " + \
        value.ts_definition_string(is_interface_definition=True)
    return text


def _get_ts_endpoint_text(key, value) -> str:
    text = f"{key}:"
    if isinstance(value, dict):
        text += " {"
        for _key, _value in value.items():
            text += "\n"
            text += _get_ts_endpoint_text(_key, _value)
        text += "\n" + "},"
    else:
        text += " (\n" \
            + (",\n").join([(k + ": string" + (" | null" if v.default is None else ""))
                            for k, v in value.args.items() if k not in ('self', 'request', 'args', 'kwargs')]) \
            + ((",\n") if len([k for k in value.args.keys() if k not in ('self', 'request', 'args', 'kwargs')]) > 0 else "") \
            + "params: {\n" \
            + ("" if not value.query_serializer else "query?: " + value.query_serializer.ts_definition_string(method="read") + ",\n") \
            + ("" if not value.body_serializer else "data?: " + value.response_serializer.ts_definition_string(method="write") + "\n") \
            + "options?: any,\n" \
            + "onSuccess?(result: " \
            + ("" if not value.response_serializer else value.response_serializer.ts_definition_string(method="read")) \
            + "): void,\n" \
            + "onError?(error: any): void\n" \
            + "},\n" \
            + ") : Promise<Response> => {\n" \
            + 'return fetch(' + ("`" if value.url and "$" in value.url else '"') + (value.url or "") + ("`" if value.url and "$" in value.url else '"') + ("" if not value.query_serializer else (" + \"?\" + new URLSearchParams(params.query || {}).toString()")) + ', {\n' \
            + 'method: "' + value.method + '",\n' \
            + ("" if not value.body_serializer else 'body: params.data,\n') \
            + "...params.options, \n" \
            + "})\n" \
            + ".then((response) => response.json())\n" \
            + ".then((result: " + value.response_serializer.ts_definition_string(method="read") + ") => params.onSuccess & params.onSuccess(result))\n" \
            + ".catch((error) => params.onError & params.onError(error)); \n" \
            + "}, "
    return text


def _get_api_client(api_name: str, post_processor: Callable[[str], str]) -> str:
    """
    Generates the TypeScript API Client documentation text.
    """
    if re.match(r"[^0-9A-Za-z_]", api_name):
        raise DRFTypeScriptAPIClientException(
            "`class_name` may only contain alphanumeric characters,")
    if re.match(r"[0-9]", api_name[0]):
        raise DRFTypeScriptAPIClientException(
            "`class_name` must not begin with a number.")

    content = ""

    # interfaces
    sep = ""
    for _, value in DRFSerializerMapper.mappings.items():
        content += sep
        content += _get_ts_interface_text(value)
        sep = "\n\n"

    content += "\n\n"

    content += f"const {api_name} = {{\n"

    # endpoints
    sep = ""
    for key, value in DRFViewMapper.mappings.items():
        content += sep
        content += _get_ts_endpoint_text(key, value)
        sep = "\n"

    content += f"\n}};\n\nexport default {api_name};\n"

    if post_processor is not None:
        content = post_processor(content)
    return content


def generate_api_client(
    output_path: str, api_name: str = "API", post_processor: Optional[Callable[[str], str]] = _default_processor
) -> None:
    """Generates the TypeScript API Client .ts file

    :param str api_name: The name of the API object
    :param post_processor: If provided, processes the API documentation after compiling and before writing the file (to add a comment or other markup, for instance).

    Ex:
    comment='// this is a comment'
    generate_api_client(output_path='/path/to/api.ts', api_name='MyAPIClass',
                        post_processor=lambda docs: comment + '\\n\\n' + docs)
    """
    if not isinstance(output_path, str):
        raise TypeError("`output_path` must be a string.")
    if not isinstance(api_name, str):
        raise TypeError("`api_name` must be a string")
    if post_processor is not None and not callable(post_processor):
        raise TypeError("`post_processor` must be a Callable or None")

    _logger.debug("Generating TypeScript API client")
    with open(output_path, 'w') as output_file:
        api_client_text = _get_api_client(
            api_name=api_name, post_processor=post_processor)
        prettified = jsbeautifier.beautify(api_client_text)
        output_file.write(prettified)
