import logging
import re
from typing import Optional, Type

from django.conf import settings

from rest_framework import serializers

_logger = logging.getLogger(__name__)


SERIALIZER_FIELD_MAPPINGS = {
    serializers.BooleanField: "boolean",
    serializers.NullBooleanField: "boolean | null",
    serializers.CharField: "string",
    serializers.EmailField: "string",
    serializers.RegexField: "string",
    serializers.SlugField: "string",
    serializers.URLField: "string",
    serializers.UUIDField: "string",
    serializers.FilePathField: "string",
    serializers.IPAddressField: "string",
    serializers.IntegerField: "number",
    serializers.FloatField: "number",
    serializers.DecimalField: "number",
    serializers.DateTimeField: "string",
    serializers.DateField: "string",
    serializers.TimeField: "string",
    serializers.DurationField: "string",
    serializers.DictField: "{ [key: string] : any }",
    serializers.HStoreField: "{ [key: string] : any }",
    serializers.JSONField: "any",
}

if hasattr(settings, "DRF_TSDK"):
    SERIALIZER_FIELD_MAPPING_OVERRIDES = settings.DRF_TSDK.get(
        "SERIALIZER_FIELD_MAPPINGS"
    )
    if SERIALIZER_FIELD_MAPPING_OVERRIDES:
        for k, v in SERIALIZER_FIELD_MAPPING_OVERRIDES.items():
            SERIALIZER_FIELD_MAPPINGS[k] = v


class TypeScriptPropertyDefinition:
    def __init__(
        self,
        name,
        ts_type,
        is_optional=False,
        is_nullable=False,
        is_many=False,
        is_readonly=False,
        is_writeonly=False,
        comment=None,
    ):
        self.name = name
        self.ts_type = ts_type
        self.is_optional = is_optional
        self.is_nullable = is_nullable
        self.is_many = is_many
        self.is_readonly = is_readonly
        self.is_writeonly = is_writeonly
        self.comment = comment

    def _format_name(self) -> str:
        """Adds quotes arount a string if it contains non-alphanumeric characters"""
        if re.search(r"[^0-9A-Za-z_]", self.name):
            return '"%s"' % self.name.replace('"', '\\"')
        return self.name

    def ts_definition_string(self, method: str = "read") -> Optional[str]:
        if self.is_readonly and method == "write":
            return None
        if self.is_writeonly and method == "read":
            return None
        ret = (
            ""
            if not self.comment
            else ("/** " + self.comment.replace("\n", "\n * ") + " */\n")
        )
        ret += (
            self._format_name()
            + ("?" if self.is_optional else "")
            + ": "
            + self.ts_type
            + ("[]" if self.is_many else "")
            + (" | null" if self.is_nullable else "")
        )
        return ret


class TypeScriptEndpointDefinition:
    def __init__(
        self,
        view,
        description=None,
        query_serializer=None,
        body_serializer=None,
        response_serializer=None,
    ):
        self.view = view
        self.description = description
        self.query_serializer = query_serializer
        self.body_serializer = body_serializer
        self.response_serializer = response_serializer


class TypeScriptInterfaceDefinition:
    def __init__(
        self,
        serializer: Type[serializers.Serializer],
        name: Optional[str] = None,
        should_export: bool = True,
        property_definition=None,
        method: str = "read",
    ):
        serializer_ = serializer

        self.is_many = False
        if isinstance(serializer_, serializers.ListSerializer):
            # print("FOUDN LIST SERIALIZER: ", str(_serializer))
            serializer_ = serializer_.child
            self.is_many = True
            # print("LIST SERIALIZER CHILD: ", str(_serializer))

        if not isinstance(serializer_, serializers.Serializer):
            serializer_ = serializer_()

        self.property_definition = property_definition
        self.serializer = serializer_
        self.name = name or serializer_.__class__.__name__
        if re.search(r"[^0-9A-Za-z_]", self.name):
            self.name = '"%s"' % self.name.replace('"', '\\"')
        self.should_export = should_export
        self.properties = self._get_interface_definition()
        self.method = method

    def ts_definition_string(
        self, method: str = "read", is_interface_definition: bool = False
    ) -> str:
        from .drf_to_ts import DRFSerializerMapper

        if (
            method == "read"
            and not is_interface_definition
            and self.serializer.__class__ in DRFSerializerMapper.mappings.keys()
        ):
            ret = ""
            if hasattr(self.serializer, "help_text") and self.serializer.help_text:
                ret = f"/** {self.serializer.help_text} */\n"
            name = DRFSerializerMapper.mappings[self.serializer.__class__].name
            ret += name + ("[]" if self.is_many else "")
            return ret

        property_strings = []
        for property_ in self.properties:
            if isinstance(property_, TypeScriptInterfaceDefinition):

                is_read_only = (
                    hasattr(property_.serializer, "read_only")
                    and property_.serializer.read_only
                )
                if method == "write" and is_read_only:
                    continue

                is_write_only = (
                    hasattr(property_.serializer, "write_only")
                    and property_.serializer.write_only
                )
                if method == "read" and is_write_only:
                    continue

                if (
                    property_.serializer.__class__
                    in DRFSerializerMapper.mappings.keys()
                    and method == "read"
                ):
                    ret = ""
                    if (
                        hasattr(self.serializer, "help_text")
                        and self.serializer.help_text
                    ):
                        ret = f"/** {self.serializer.help_text} */\n"
                    name = DRFSerializerMapper.mappings[
                        property_.serializer.__class__
                    ].name
                    ret += (
                        property_.name
                        + ("?" if property_.property_definition.is_optional else "")
                        + ": "
                        + name
                        + ("[]" if property_.property_definition.is_many else "")
                        + (
                            " | null"
                            if property_.property_definition.is_nullable
                            else ""
                        )
                    )
                    property_strings.append(ret)
                else:
                    ret = ""
                    if (
                        hasattr(property_.serializer, "help_text")
                        and property_.serializer.help_text
                    ):
                        ret = f"/** {property_.serializer.help_text} */\n"
                    not_required = (
                        hasattr(property_.serializer, "required")
                        and not property_.serializer.required
                        and not is_read_only
                    )
                    ret += (
                        property_.name
                        + ("?" if not_required else "")
                        + ": "
                        + property_.ts_definition_string(method=method)
                        + ("[]" if property_.property_definition.is_many else "")
                        + (
                            " | null"
                            if property_.property_definition.is_nullable
                            else ""
                        )
                    )
                    property_strings.append(ret)
            else:
                property_strings.append(property_.ts_definition_string(method=method))
        return (
            "{"
            + ",\n".join(
                [
                    property_string
                    for property_string in property_strings
                    if property_string is not None
                ]
            )
            + "}"
        )

    def _get_interface_definition(self) -> Type[TypeScriptPropertyDefinition]:
        """
        Returns an object representing a TypeScript interface

        :param serializer: A DRF Serializer class instance
        :return: An InterfaceDefinition instance
        """

        if hasattr(self.serializer, "get_fields"):
            _logger.debug(
                "Getting serializer definition for '%s'", type(self.serializer).__name__
            )
            drf_fields = self.serializer.get_fields().items()
        else:
            _logger.debug(
                "Getting serializer definition for '%s'", self.serializer.__name__
            )
            drf_fields = self.serializer._declared_fields.items()

        properties = []
        for key, value in drf_fields:
            property_definition = self._get_property_definition(key, value)
            if isinstance(value, serializers.Serializer) or isinstance(
                value, serializers.ListSerializer
            ):
                properties.append(
                    TypeScriptInterfaceDefinition(
                        value, key, property_definition=property_definition
                    )
                )
            else:
                properties.append(property_definition)
        return properties

    def _get_property_definition(
        self, name: str, field
    ) -> Type[TypeScriptPropertyDefinition]:
        """
        Returns an objecting representing a TypeScript parameter.

        :param name: The name of the serializer field
        :param field: The definition of the serializer field
        :return: A TypeScriptParameterDefinition instance
        """
        if hasattr(field, "child") and not isinstance(field, serializers.DictField):
            is_many = True
            field_type = type(field.child)
            effective_field = field.child
        elif hasattr(field, "child_relation") and not isinstance(
            field, serializers.DictField
        ):
            is_many = True
            field_type = type(field.child_relation)
            effective_field = field.child_relation
        else:
            is_many = False
            field_type = type(field)
            effective_field = field

        # get TypeScript type string based on DRF serializer field type
        ts_type = SERIALIZER_FIELD_MAPPINGS.get(field_type)
        if ts_type is None:
            if isinstance(effective_field, serializers.ChoiceField) and hasattr(
                effective_field, "choices"
            ):
                ts_type = (
                    ("(" if is_many else "")
                    + " | ".join(
                        [
                            (
                                ('"' + choice.replace('"', '\\"') + '"')
                                if isinstance(choice, str)
                                else str(choice)
                            )
                            for choice in effective_field.choices
                        ]
                    )
                    + (")" if is_many else "")
                )
            else:
                for key, value in SERIALIZER_FIELD_MAPPINGS.items():
                    if issubclass(field_type, key):
                        ts_type = value
                        break
        if ts_type is None:
            ts_type = "any"

        if (
            isinstance(field, serializers.DictField)
            and hasattr(field, "child")
            and field.child
        ):
            if isinstance(field.child, serializers.ListSerializer):
                definition = TypeScriptInterfaceDefinition(
                    serializer=field.child,
                    should_export=False,
                    method="read" if not hasattr(self, "method") else self.method,
                )
                child_type = (
                    definition.ts_definition_string(
                        method="read" if not hasattr(self, "method") else self.method
                    )
                    + "[]"
                )
            elif isinstance(field.child, serializers.Serializer):
                definition = TypeScriptInterfaceDefinition(
                    serializer=field.child,
                    should_export=False,
                    method="read" if not hasattr(self, "method") else self.method,
                )
                child_type = definition.ts_definition_string(
                    method="read" if not hasattr(self, "method") else self.method
                )
            else:
                child_type = self._get_property_definition(
                    name="dummy", field=field.child
                ).ts_type
            ts_type = f"{{ [key: string] : {child_type} }}"

        return TypeScriptPropertyDefinition(
            name=name,
            ts_type=ts_type,
            is_optional=not (hasattr(field, "read_only") and field.read_only)
            and ((hasattr(field, "required") and not field.required)),
            is_nullable=hasattr(field, "allow_null") and field.allow_null,
            is_many=is_many,
            is_readonly=hasattr(field, "read_only") and field.read_only,
            is_writeonly=hasattr(field, "write_only") and field.write_only,
            comment=None if not hasattr(field, "help_text") else field.help_text,
        )
