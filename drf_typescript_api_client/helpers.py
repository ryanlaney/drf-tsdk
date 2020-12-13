from typing import Optional, Type
import logging

from rest_framework import serializers

_logger = logging.getLogger(__name__)


DEFAULT_SERIALIZER_FIELD_MAPPINGS = {
    serializers.BooleanField: 'boolean',
    serializers.NullBooleanField: 'boolean | null',
    serializers.CharField: 'string',
    serializers.EmailField: 'string',
    serializers.RegexField: 'string',
    serializers.SlugField: 'string',
    serializers.URLField: 'string',
    serializers.UUIDField: 'string',
    serializers.FilePathField: 'string',
    serializers.IPAddressField: 'string',
    serializers.IntegerField: 'number',
    serializers.FloatField: 'number',
    serializers.DecimalField: 'number',
    serializers.DateTimeField: 'string',
    serializers.DateField: 'string',
    serializers.TimeField: 'string',
    serializers.DurationField: 'string',
    serializers.DictField: 'Map'
}


class TypeScriptPropertyDefinition:
    def __init__(self, name, ts_type, is_optional=False, is_nullable=False, is_many=False, is_readonly=False, is_writeonly=False, comment=None):
        self.name = name
        self.ts_type = ts_type
        self.is_optional = is_optional
        self.is_nullable = is_nullable
        self.is_many = is_many
        self.is_readonly = is_readonly
        self.is_writeonly = is_writeonly
        self.comment = comment

    def ts_definition_string(self, method: str = "read") -> Optional[str]:
        if self.is_readonly and method == "write":
            return None
        if self.is_writeonly and method == "read":
            return None
        return self.name + ("?" if self.is_optional else "") + ": " + self.ts_type + (" | null" if self.is_nullable else "")


class TypeScriptEndpointDefinition:
    def __init__(self, url, args, method, query_serializer=None, request_serializer=None, response_serializer=None):
        self.url = url
        self.args = args
        self.method = method
        self.query_serializer = query_serializer
        self.request_serializer = request_serializer
        self.response_serializer = response_serializer


class TypeScriptInterfaceDefinition:
    def __init__(self, serializer: Type[serializers.Serializer]):
        serializer_ = serializer
        if isinstance(serializer_, serializers.ListSerializer):
            # print("FOUDN LIST SERIALIZER: ", str(_serializer))
            serializer_ = serializer_.child
            # print("LIST SERIALIZER CHILD: ", str(_serializer))

        if not isinstance(serializer_, serializers.Serializer):
            serializer_ = serializer_()

        self.serializer = serializer_
        self.properties = self._get_interface_definition()

    def ts_definition_string(self, method: str = "read") -> str:
        property_strings = [property_.ts_definition_string(
            method=method) for property_ in self.properties]
        return "{" + ",\n".join([property_string for property_string in property_strings if property_string is not None]) + "}"

    def _get_interface_definition(self) -> Type[TypeScriptPropertyDefinition]:
        '''
        Returns an object representing a TypeScript interface

        :param serializer: A DRF Serializer class instance
        :return: An InterfaceDefinition instance
        '''

        if hasattr(self.serializer, 'get_fields'):
            _logger.info("Getting serializer definition for '%s'",
                         type(self.serializer).__name__)
            drf_fields = self.serializer.get_fields().items()
        else:
            _logger.info("Getting serializer definition for '%s'",
                         self.serializer.__name__)
            drf_fields = self.serializer._declared_fields.items()

        properties = []
        for key, value in drf_fields:
            properties.append(self._get_property_definition(
                key, value))
        return properties

    def _get_property_definition(self, name: str, field) -> Type[TypeScriptPropertyDefinition]:
        '''
        Returns an objecting representing a TypeScript parameter.

        :param name: The name of the serializer field
        :param field: The definition of the serializer field
        :return: A TypeScriptParameterDefinition instance
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

        return TypeScriptPropertyDefinition(
            name=name,
            ts_type=DEFAULT_SERIALIZER_FIELD_MAPPINGS.get(field_type, "any"),
            is_optional=hasattr(field, 'required') and not field.required,
            is_nullable=hasattr(field, 'allow_null') and field.allow_null,
            is_many=is_many,
            is_readonly=hasattr(field, "read_only") and field.read_only,
            is_writeonly=hasattr(field, "write_only") and field.read_only,
            comment=None if not hasattr(
                field, 'help_text') else field.help_text
        )
