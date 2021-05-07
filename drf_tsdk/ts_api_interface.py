import logging
import re

from typing import Optional

from .drf_to_ts import DRFSerializerMapper

_logger = logging.getLogger(f"drf-tsdk.{__name__}")


def ts_api_interface(
    name: Optional[str] = None, should_export: bool = True, method: str = "read"
):
    """Any Django Rest Framework Serializer with this decorator will be added to a
    dynamically-generated TypeScript file with the approprate type definitions.

    @ts_api_interface(name="IFoo")
    class FooSerializer(serializers.Serializer):
        pass
    """
    if name is not None and not isinstance(name, str):
        raise TypeError("`name` must be a string or None.")
    if name is not None and not re.search(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
        raise ValueError(
            "`name` must start with a letter and contain only alphanumeric characters."
        )
    if not isinstance(should_export, bool):
        raise TypeError("`should_export` must be a boolean.")

    def decorator(class_):
        _logger.debug("Getting interface for %s", class_)
        mapper = DRFSerializerMapper(
            serializer=class_, name=name, should_export=should_export, method=method
        )
        mapper.update_mappings()
        return class_

    return decorator
