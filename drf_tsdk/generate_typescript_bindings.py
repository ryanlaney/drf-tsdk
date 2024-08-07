import inspect
import json
import logging
import os
import re
from typing import Any, Callable, List, Optional

from django.urls import URLPattern

from .drf_to_ts import DRFSerializerMapper, DRFViewMapper
from .exceptions import DRFTypeScriptAPIClientException
from .url_resolver import resolve_urls

# import jsbeautifier


_logger = logging.getLogger(f"drf-tsdk.{__name__}")


def _default_processor(content):
    return (
        "/** This file was generated automatically by drf-tsdk. */" + "\n\n" + content
    )


def _get_ts_interface_text(value) -> str:
    text = (
        f"{'export ' if value.should_export else ''} interface {value.name} "
        + value.ts_definition_string(is_interface_definition=True, method=value.method)
    )
    return text


def _get_headers(headers, csrf_token_variable_name) -> str:
    ret = {}
    ret["Content-Type"] = "application/json"
    for key, value in headers.items():
        ret[key] = value
    ret_stringified = json.dumps(ret)
    if csrf_token_variable_name is not None:
        ret_stringified = (
            '{"X-CSRFToken": '
            + csrf_token_variable_name
            + ", "
            + ret_stringified.split("{")[1]
        )
    return ret_stringified


# TODO: this is pretty hacky, and probably doesn't work in certain cases, esp. with regex. Need to refactor this.


def _get_url(value, url_patterns: dict) -> (str, str, List[str], Any):
    """Returns URL and method of the endpoint"""

    url_pattern = url_patterns.get(
        inspect.getmodule(value.view).__name__ + ":" + value.view.__qualname__
    )
    if url_pattern:
        return url_pattern

    url_pattern = url_patterns.get(
        inspect.getmodule(value.view).__name__ + ":" + value.view.__name__
    )
    if url_pattern:
        return url_pattern

    if hasattr(str(value.view), "cls"):
        url_pattern = url_patterns.get(str(value.view.cls))
        if url_pattern:
            return url_pattern

    url_pattern = next(
        iter(
            [
                x
                for x in url_patterns.values()
                if x[3].__module__ == value.view.__module__
                and x[3].cls.__name__ == value.view.cls.__name__
            ]
        ),
        None,
    )
    if url_pattern:
        return url_pattern

    raise DRFTypeScriptAPIClientException(
        f"No pattern found for View {str(value.view)} {str(value.view.__name__)} in module {str(value.view.__module__)} line {value.view.__code__.co_firstlineno}"
    )


def _get_ts_endpoint_text(
    key, value, headers, csrf_token_variable_name, url_patterns
) -> str:
    text = ""
    if not isinstance(value, dict) and value.description:
        text += "/** " + value.description.replace("\n", "\n * ") + " */\n"
    text += f"{key}:"
    if isinstance(value, dict):
        text += " {"
        for _key, _value in value.items():
            text += "\n"
            text += _get_ts_endpoint_text(
                _key, _value, headers, csrf_token_variable_name, url_patterns
            )
        text += "\n" + "},"
    else:
        # print(_get_url(value, url_patterns))
        url, method, args, _ = _get_url(value, url_patterns)
        text += (
            " (\n"
            + (",\n").join([f"{arg}: string" for arg in args])
            + ((",\n") if len(args) > 0 else "")
            + "params: {\n"
            + (
                ""
                if not value.query_serializer
                else "query?: "
                + value.query_serializer.ts_definition_string(method="read")
                + ",\n"
            )
            + (
                ""
                if not value.body_serializer
                else "data?: "
                + value.body_serializer.ts_definition_string(method="write")
                + ",\n"
            )
            + "options?: RequestInit,\n"
            + "/** Called when the request returns a successful response */\n"
            + "onSuccess?(result: "
            + (
                "any"
                if not value.response_serializer
                else value.response_serializer.ts_definition_string(method="read")
            )
            + "): void,\n"
            + "/** Called when the request errors out */\n"
            + "onError?(error: any): void,\n"
            + (
                (
                    "/** If `true`, uses data that was cached previously when this request returned a successful response. */\n"
                    + "shouldUseCache?: boolean = false,\n"
                    + "/** If `true`, caches the returned data if the request is successful. */\n"
                    + "shouldUpdateCache?: boolean = false\n"
                )
                if method.lower().strip() == "get"
                else ""
            )
            + "},\n"
            + ") : Promise<Response> "
            + ("?" if method.lower().strip() == "get" else "")
            + " => {\n"
            + "const requestPath = "
            + url
            + ' + (params.query ? ("?" + new URLSearchParams(params.query).toString()) : "");'
            + (
                (
                    "if (params.shouldUseCache && cache[requestPath]) { params.onSuccess && params.onSuccess(cache[requestPath]) } else {"
                )
                if method.lower().strip() == "get"
                else ""
            )
            + "return fetch(requestPath, {\n"
            + 'method: "'
            + method
            + '",\n'
            + "headers: "
            + _get_headers(headers, csrf_token_variable_name)
            + ",\n"
            + (
                ""
                if not value.body_serializer
                else "body: JSON.stringify(params.data),\n"
            )
            + "...params.options, \n"
            + "})\n"
            + """.then((response) => {
                if (response.ok) {
                    return response.json()
                        .then((result) => {
                            if (params.shouldUpdateCache){ cache[requestPath] = result }; params.onSuccess && params.onSuccess(result)
            })
                        .catch((error) => params.onError && params.onError(error))
                }
                return response.text()
                    .then((result) => params.onError && params.onError({
                        response: response,
                        status: response.status,
                        statusText: response.statusText,
                        message: result
                    }))
                    .catch((error) => params.onError && params.onError(error))
                })
            }"""
            + ("}," if method.lower().strip() == "get" else ",")
        )
    return text


def _get_typescript_bindings(
    api_name: str,
    headers: dict,
    csrf_token_variable_name: Optional[str],
    post_processor: Callable[[str], str],
    url_patterns: List[URLPattern],
) -> str:
    """
    Generates the TypeScript API Client documentation text.
    """
    if re.search(r"[^0-9A-Za-z_]", api_name):
        raise DRFTypeScriptAPIClientException(
            "`class_name` may only contain alphanumeric characters,"
        )
    if re.search(r"[0-9]", api_name[0]):
        raise DRFTypeScriptAPIClientException(
            "`class_name` must not begin with a number."
        )

    content = ""

    # cache
    content += "const cache = {};\n\n"

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
        content += _get_ts_endpoint_text(
            key, value, headers, csrf_token_variable_name, url_patterns
        )
        sep = "\n"

    content += f"\n}};\n\nexport default {api_name};\n"

    if post_processor is not None:
        content = post_processor(content)
    return content


def generate_typescript_bindings(
    output_path: str,
    api_name: str = "API",
    headers: dict = {},
    csrf_token_variable_name: Optional[str] = None,
    post_processor: Optional[Callable[[str], str]] = _default_processor,
    urlpatterns=None,
) -> None:
    """Generates the TypeScript API Client .ts file

    :param str output_path: The path of the TypeScript file
    :param dict headers: A dictionary of headers to add to every request
    :param str csrf_token_variable_name: A variable name, function call, or other JavaScript-evaluable string which returns the CSRF token
    :param str api_name: The name of the API object
    :param post_processor: If provided, processes the API documentation after compiling and before writing the file (to add a comment or other markup, for instance).

    Ex:
    comment='// this is a comment'
    generate_typescript_bindings(output_path='/path/to/api.ts', api_name='MyAPIClass',
                        post_processor=lambda docs: comment + '\\n\\n' + docs)
    """
    assert urlpatterns is not None, "urlpatterns must be specified"

    if not isinstance(output_path, str):
        raise TypeError("`output_path` must be a string.")
    if not isinstance(api_name, str):
        raise TypeError("`api_name` must be a string")
    if post_processor is not None and not callable(post_processor):
        raise TypeError("`post_processor` must be a Callable or None")

    for view_mapper in DRFViewMapper.mappers:
        view_mapper.update_mappings()

    for serializer_mapper in DRFSerializerMapper.mappers:
        serializer_mapper.update_mappings()

    # TODO: very hacky
    url_patterns = resolve_urls(urlpatterns)
    url_patterns_dict = {}
    for url_pattern in url_patterns:
        # ViewSets
        if hasattr(url_pattern.url_pattern.callback, "actions") and isinstance(
            url_pattern.url_pattern.callback.actions, dict
        ):
            for method, func in url_pattern.url_pattern.callback.actions.items():
                # print(getattr(url_pattern.url_pattern.callback.cls, "__name__"), value.view.__qualname__)
                if hasattr(url_pattern.url_pattern.pattern, "_route"):
                    path = str(url_pattern.url_pattern.pattern._route)
                    re_pattern = r"\<[A-Za-z0-9_]+\:([A-Za-z0-9_]+)\>"
                    re_path = re.sub(re_pattern, r"${\1}", path)
                else:
                    path = str(url_pattern.url_pattern.pattern._regex)
                    re_pattern = r"\(\?P\<([A-Za-z0-9_]+)\>.+?\)\/"
                    re_path = re.sub(re_pattern, r"${\1}/", path)
                    re_pattern = r"\(\?P\<([A-Za-z0-9_]+)\>.+?\)\$"
                    re_path = re.sub(re_pattern, r"${\1}", re_path)
                    if re_path[0] == "^":
                        re_path = re_path[1:]
                    if re_path[-1] == "$":
                        re_path = re_path[:-1]
                quote = '"' if path == re_path else "`"
                ts_path = f"{quote}/{str(url_pattern.base_url)}{re_path}{quote}"
                ts_method = method.upper()
                ts_args = re.findall(r"\$\{(.*?)\}", re_path)
                url_patterns_dict[
                    inspect.getmodule(url_pattern.url_pattern.callback).__name__
                    + ":"
                    + getattr(
                        getattr(url_pattern.url_pattern.callback.cls, func),
                        "__qualname__",
                    )
                ] = (ts_path, ts_method, ts_args, url_pattern.url_pattern.callback)
                url_patterns_dict[str(url_pattern.url_pattern.callback)] = (
                    ts_path,
                    ts_method,
                    ts_args,
                    url_pattern.url_pattern.callback,
                )
        # APIViews
        elif hasattr(
            url_pattern.url_pattern.callback, "view_class"
        ) and "WrappedAPIView" not in str(url_pattern.url_pattern.callback):
            actions = {
                k: v
                for k, v in url_pattern.url_pattern.callback.view_class.__dict__.items()
                if callable(v)
            }
            for method, func in actions.items():
                if hasattr(url_pattern.url_pattern.pattern, "_route"):
                    path = str(url_pattern.url_pattern.pattern._route)
                    re_pattern = r"\<[A-Za-z0-9_]+\:([A-Za-z0-9_]+)\>"
                    re_path = re.sub(re_pattern, r"${\1}", path)
                else:
                    path = str(url_pattern.url_pattern.pattern._regex)
                    re_pattern = r"\(\?P\<([A-Za-z0-9_]+)\>.+?\)\/"
                    re_path = re.sub(re_pattern, r"${\1}/", path)
                    re_pattern = r"\(\?P\<([A-Za-z0-9_]+)\>.+?\)\$"
                    re_path = re.sub(re_pattern, r"${\1}", re_path)
                    if re_path[0] == "^":
                        re_path = re_path[1:]
                    if re_path[-1] == "$":
                        re_path = re_path[:-1]
                quote = '"' if path == re_path else "`"
                ts_path = f"{quote}/{str(url_pattern.base_url)}{re_path}{quote}"
                ts_method = method.upper()
                ts_args = re.findall(r"\$\{(.*?)\}", re_path)
                url_patterns_dict[
                    inspect.getmodule(url_pattern.url_pattern.callback).__name__
                    + ":"
                    + getattr(
                        getattr(url_pattern.url_pattern.callback.view_class, method),
                        "__qualname__",
                    )
                ] = (ts_path, ts_method, ts_args, url_pattern.url_pattern.callback)
                url_patterns_dict[str(url_pattern.url_pattern.callback)] = (
                    ts_path,
                    ts_method,
                    ts_args,
                    url_pattern.url_pattern.callback,
                )
        # @api_views
        elif hasattr(url_pattern.url_pattern.callback, "cls"):
            if hasattr(url_pattern.url_pattern.pattern, "_route"):
                path = str(url_pattern.url_pattern.pattern._route)
                re_pattern = r"\<[A-Za-z0-9_]+\:([A-Za-z0-9_]+)\>"
                re_path = re.sub(re_pattern, r"${\1}", path)
            else:
                path = str(url_pattern.url_pattern.pattern._regex)
                re_pattern = r"\(\?P\<([A-Za-z0-9_]+)\>.+?\)\/"
                re_path = re.sub(re_pattern, r"${\1}/", path)
                re_pattern = r"\(\?P\<([A-Za-z0-9_]+)\>.+?\)\$"
                re_path = re.sub(re_pattern, r"${\1}", re_path)
                if re_path[0] == "^":
                    re_path = re_path[1:]
                if re_path[-1] == "$":
                    re_path = re_path[:-1]
            quote = '"' if path == re_path else "`"
            ts_path = f"{quote}/{str(url_pattern.base_url)}{re_path}{quote}"
            ts_method = next(
                iter(
                    [
                        x
                        for x in url_pattern.url_pattern.callback.cls.http_method_names
                        if x != "options"
                    ]
                ),
                "get",
            ).upper()
            ts_args = re.findall(r"\$\{(.*?)\}", re_path)
            url_patterns_dict[
                inspect.getmodule(url_pattern.url_pattern.callback).__name__
                + ":"
                + url_pattern.url_pattern.callback.__name__
            ] = (ts_path, ts_method, ts_args, url_pattern.url_pattern.callback)
            url_patterns_dict[str(url_pattern.url_pattern.callback)] = (
                ts_path,
                ts_method,
                ts_args,
                url_pattern.url_pattern.callback,
            )

    # print(url_patterns_dict)
    # return
    # print([{
    #         'pattern': {
    #             'route': p.url_pattern.pattern._route,
    #             'regex_dict': p.url_pattern.pattern._regex_dict,
    #             'is_endpoint': p.url_pattern.pattern._is_endpoint,
    #             'name': p.url_pattern.pattern.name,
    #             'converters': p.url_pattern.pattern.converters
    #         },
    #         'callback': p.url_pattern.callback,
    #         'callbackdict': p.url_pattern.callback.__dict__,
    #         'default_args': p.url_pattern.default_args,
    #         'name': p.url_pattern.name
    #     } for p in url_patterns])
    # return

    _logger.debug("Getting current TypeScript SDK")
    mode = "w"
    if os.path.exists(output_path):
        mode = "r+"
    with open(output_path, mode) as output_file:
        if mode == "r+":
            current_text = output_file.read()
        typescript_bindings_text = _get_typescript_bindings(
            api_name=api_name,
            headers=headers,
            csrf_token_variable_name=csrf_token_variable_name,
            post_processor=post_processor,
            url_patterns=url_patterns_dict,
        )
        prettified = (
            typescript_bindings_text  # jsbeautifier.beautify(typescript_bindings_text)
        )
        if mode == "w" or current_text.strip() != prettified.strip():
            _logger.debug("Changes detected, rebuilding the SDK")
            if mode == "r+":
                output_file.seek(0)
                output_file.truncate()
            output_file.write(prettified)
            output_file.close()
