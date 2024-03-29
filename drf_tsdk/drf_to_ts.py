import logging
from typing import List, Optional, Type

from rest_framework import serializers

from .exceptions import DRFTypeScriptAPIClientException
from .helpers import TypeScriptEndpointDefinition, TypeScriptInterfaceDefinition

_logger = logging.getLogger(f"drf-tsdk.{__name__}")


class DRFViewMapper:

    mappers: "List[DRFViewMapper]" = []

    mappings = (
        dict()
    )  # a mapping of DRF views to typescript API endpoints, represented by TypeScriptEndpointDefinition instances

    def __init__(
        self,
        path,
        view,
        description=None,
        query_serializer=None,
        body_serializer=None,
        response_serializer=None,
    ):
        self.path = path
        self.view = view
        self.description = description
        self.query_serializer = query_serializer
        self.body_serializer = body_serializer
        self.response_serializer = response_serializer

        DRFViewMapper.mappers.append(self)

    def _update_mappings_for_path(self, path, mappings_for_path):
        if path[0] not in DRFViewMapper.mappings:
            if len(path) > 1:
                mappings_for_path[path[0]] = self._update_mappings_for_path(
                    path=path[1:], mappings_for_path=dict()
                )
            else:
                mappings_for_path[path[0]] = TypeScriptEndpointDefinition(
                    view=self.view,
                    description=self.description,
                    query_serializer=None
                    if not self.query_serializer
                    else TypeScriptInterfaceDefinition(self.query_serializer),
                    body_serializer=None
                    if not self.body_serializer
                    else TypeScriptInterfaceDefinition(self.body_serializer),
                    response_serializer=None
                    if not self.response_serializer
                    else TypeScriptInterfaceDefinition(self.response_serializer),
                )
        elif isinstance(DRFViewMapper.mappings[path[0]], TypeScriptEndpointDefinition):
            return mappings_for_path
        elif isinstance(DRFViewMapper.mappings[path[0]], dict):
            mappings_for_path[path[0]] = self._update_mappings_for_path(
                path=path[1:], mappings_for_path=mappings_for_path[path[0]]
            )
        else:
            raise DRFTypeScriptAPIClientException("An unknown error occurred")
        return mappings_for_path

    def update_mappings(self):
        DRFViewMapper.mappings = self._update_mappings_for_path(
            self.path, mappings_for_path=DRFViewMapper.mappings
        )


class DRFSerializerMapper:

    mappers: "List[DRFSerializerMapper]" = []

    mappings = (
        dict()
    )  # a mapping of DRF serializers to typescript API interfaces, represented by TypeScriptInterfaceDefinition instances

    def __init__(
        self,
        serializer: Type[serializers.Serializer],
        name: Optional[str] = None,
        should_export: bool = True,
        method: str = "read",
    ):
        self.serializer = serializer
        self.name = name
        self.should_export = should_export
        self.method = method

        DRFSerializerMapper.mappers.append(self)

    def _update_mappings(self):
        definition = TypeScriptInterfaceDefinition(
            serializer=self.serializer,
            name=self.name,
            should_export=self.should_export,
            method=self.method,
        )
        DRFSerializerMapper.mappings[self.serializer] = definition

    def update_mappings(self):
        self._update_mappings()
