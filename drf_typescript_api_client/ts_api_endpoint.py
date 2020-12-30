import logging
import re

from typing import Any, List, Optional, Type

from rest_framework import serializers

from .exceptions import DRFTypeScriptAPIClientException
from .drf_to_ts import DRFViewMapper

_logger = logging.getLogger(f"drf-typescript-api-client.{__name__}")


def ts_api_endpoint(
    path: List[str],
    urlconf: Any = None,
    url: Optional[str] = None,
    method: str = "GET",
    description: Optional[str] = None,
    query_serializer: Optional[Type[serializers.Serializer]] = None,
    body_serializer: Optional[Type[serializers.Serializer]] = None,
    response_serializer: Optional[Type[serializers.Serializer]] = None
):
    """Any Django Rest Framework view with this decorator will be added to a
    dynamically-generated TypeScript file with the approprate TypeScript type interfaces.

    @ts_api_interface(path=("foo", "list"), response=FooSerializer)
    @api_client(['GET'])
    def foo(request):
        pass
    """
    if not isinstance(path, list) and not isinstance(path, tuple) and not isinstance(path, str):
        raise TypeError("`path` must be a list, tuple, or string.")
    if isinstance(path, str):
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", path):
            raise ValueError(
                "If `path` is a string, it must begin with a letter and consist of only alphanumeric characters.")
    else:
        if len(path) == 0:
            raise ValueError(
                "If `path` is a list or tuple, it must have at least one component.")
        for elem in path:
            if not isinstance(elem, str):
                raise TypeError(
                    "If `path` is a list or tuple, each item must be a string.")
            if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", elem):
                raise ValueError(
                    "If `path` is a list or tuple, each item must be a string beginning with a letter and consisting of only alphanumeric characters.")

    if not isinstance(method, str):
        raise TypeError("`method` must be a string.")
    allowed_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
    if method not in allowed_methods + [x.lower() for x in allowed_methods]:
        raise ValueError("`method` must be one of %s" %
                         ", ".join(allowed_methods))

    if query_serializer is not None \
            and not isinstance(query_serializer, serializers.Serializer) \
            and not isinstance(query_serializer, serializers.ListSerializer) \
            and not issubclass(query_serializer, serializers.Serializer):
        raise ValueError(
            "`query_serializer` must be a Serializer or ListSerializer instance, a Serializer subclass, or None.")
    if body_serializer is not None \
            and not isinstance(body_serializer, serializers.Serializer) \
            and not isinstance(body_serializer, serializers.ListSerializer) \
            and not issubclass(body_serializer, serializers.Serializer):
        raise ValueError(
            "`query_serializer` must be a Serializer or ListSerializer instance, a Serializer subclass, or None.")
    if response_serializer is not None \
            and not isinstance(response_serializer, serializers.Serializer) \
            and not isinstance(response_serializer, serializers.ListSerializer) \
            and not issubclass(response_serializer, serializers.Serializer):
        raise ValueError(
            "`query_serializer` must be a Serializer or ListSerializer instance, a Serializer subclass, or None.")

    def decorator(view):
        _logger.debug("Updating mapping for %s", view)
        if len(path) == 0:
            raise DRFTypeScriptAPIClientException(
                "`path` must have at least one component")
        mapper = DRFViewMapper(
            path=path,
            view=view,
            urlconf=urlconf,
            url=url,
            method=method,
            description=description,
            query_serializer=query_serializer,
            body_serializer=body_serializer,
            response_serializer=response_serializer
        )
        mapper.update_mappings()
        return view

    return decorator
