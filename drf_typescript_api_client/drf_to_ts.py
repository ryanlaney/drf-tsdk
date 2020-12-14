import inspect
import logging
from typing import Type, Optional

from rest_framework import serializers

from .exceptions import DRFTypeScriptAPIClientException
from .helpers import TypeScriptEndpointDefinition, TypeScriptInterfaceDefinition, TypeScriptPropertyDefinition

_logger = logging.getLogger(f"drf-typescript-api-client.{__name__}")


class DRFViewMapper:

    mappings = dict()  # a mapping of DRF views to typescript API endpoints, represented by TypeScriptEndpointDefinition instances

    def __init__(self, path, view, urlconf: Optional[str] = None, url: Optional[str] = None, method: str = "GET", query_serializer=None, request_serializer=None, response_serializer=None):
        self.path = path
        self.view = view
        self.urlconf = urlconf
        self.url = url
        self.method = method
        self.query_serializer = query_serializer
        self.request_serializer = request_serializer
        self.response_serializer = response_serializer

    def _update_mappings_for_path(self, path, mappings_for_path):
        if path[0] not in DRFViewMapper.mappings:
            if len(path) > 1:
                mappings_for_path[path[0]] = self._update_mappings_for_path(
                    path=path[1:], mappings_for_path=dict())
            else:
                mappings_for_path[path[0]] = TypeScriptEndpointDefinition(
                    url=self.url,
                    args=inspect.signature(self.view).parameters,
                    method=self.method,
                    query_serializer=None if not self.query_serializer else TypeScriptInterfaceDefinition(
                        self.query_serializer),
                    request_serializer=None if not self.request_serializer else TypeScriptInterfaceDefinition(
                        self.request_serializer),
                    response_serializer=None if not self.response_serializer else TypeScriptInterfaceDefinition(
                        self.response_serializer)
                )
        elif isinstance(DRFViewMapper.mappings[path[0]], TypeScriptEndpointDefinition):
            return mappings_for_path
        elif isinstance(DRFViewMapper.mappings[path[0]], dict):
            mappings_for_path[path[0]] = self._update_mappings_for_path(
                path=path[1:], mappings_for_path=mappings_for_path[path[0]])
        else:
            raise DRFTypeScriptAPIClientException("An unknown error occurred")
        return mappings_for_path

    def update_mappings(self):
        DRFViewMapper.mappings = self._update_mappings_for_path(
            self.path, mappings_for_path=DRFViewMapper.mappings)


class DRFSerializerMapper:

    mappings = dict()  # a mapping of DRF serializers to typescript API interfaces, represented by TypeScriptInterfaceDefinition instances

    def __init__(self, serializer: Type[serializers.Serializer], name: Optional[str] = None, should_export: bool = True):
        self.serializer = serializer
        self.name = name
        self.should_export = should_export

    def _update_mappings(self):
        definition = TypeScriptInterfaceDefinition(
            serializer=self.serializer, name=self.name, should_export=self.should_export)
        DRFSerializerMapper.mappings[self.serializer] = definition

    def update_mappings(self):
        self._update_mappings()
