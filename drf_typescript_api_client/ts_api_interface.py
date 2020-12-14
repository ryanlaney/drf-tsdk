import logging

from typing import Optional

from .drf_to_ts import DRFSerializerMapper

_logger = logging.getLogger(f"drf-typescript-api-client.{__name__}")


def ts_api_interface(name: Optional[str] = None, should_export: bool = True):
    """Any Django Rest Framework Serializer with this decorator will be added to a
    dynamically-generated TypeScript file with the approprate type definitions.

    @ts_api_interface(name="IFoo")
    class FooSerializer(serializers.Serializer):
        pass
    """
    def decorator(class_):
        _logger.debug("Getting interface for %s", class_)
        mapper = DRFSerializerMapper(
            serializer=class_, name=name, should_export=should_export)
        mapper.update_mappings()
        return class_

    return decorator
