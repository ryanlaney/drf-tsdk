import inspect
import logging
from typing import Type

from rest_framework import serializers

from .exceptions import DRFTypeScriptAPIClientException
from .helpers import TypeScriptEndpointDefinition, TypeScriptInterfaceDefinition, TypeScriptPropertyDefinition

_logger = logging.getLogger(f"drf-typescript-api-client.{__name__}")


class DRFViewMapper:

    mappings = dict()  # a mapping of DRF views to typescript API endpoints, represented by TypeScriptEndpointDefinition instances

    def __init__(self, path, view, urlconf=None, url=None, query_serializer=None, request_serializer=None, response_serializer=None):
        self.path = path
        self.view = view
        self.urlconf = urlconf
        self.url = url
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
                    method="GET",
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
