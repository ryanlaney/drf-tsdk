import logging

from typing import Any,  Optional, Tuple, Type

from rest_framework import serializers

from .exceptions import DRFTypeScriptAPIClientException
from .drf_to_ts import DRFViewMapper

_logger = logging.getLogger(f"drf-typescript-api-client.{__name__}")


def ts_api_client(
    path: Tuple[str, ...],
    urlconf: Any = None,
    url: Optional[str] = None,
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
        _logger.debug("Updating mapping for %s", view)
        if len(path) == 0:
            raise DRFTypeScriptAPIClientException(
                "`path` must have at least one component")
        mapper = DRFViewMapper(
            path=path,
            view=view,
            urlconf=urlconf,
            url=url,
            query_serializer=query_serializer,
            request_serializer=request_serializer,
            response_serializer=response_serializer
        )
        mapper.update_mappings()
        return view

    return decorator
