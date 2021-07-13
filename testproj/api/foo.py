from rest_framework import serializers
from rest_framework.viewsets import ViewSet

from drf_tsdk import ts_api_endpoint, ts_api_interface

from .common import SuccessSerializer
from .serializers import MyCustomField


@ts_api_interface(name="IFooQuery")
class FooQuerySerializer(serializers.Serializer):
    q1 = serializers.UUIDField(required=True, help_text="Description of `q1`")
    q2 = serializers.DateField(required=False)
    q3 = serializers.IntegerField(default=3)
    q4 = serializers.BooleanField(required=False, help_text="Description of `q2`")


class InnerFooSerializer(serializers.Serializer):
    y1 = serializers.CharField()
    y2 = serializers.DateTimeField()
    y3 = serializers.UUIDField(allow_null=True, help_text="Description of `y3`")
    y4 = serializers.ListField(child=serializers.CharField())


@ts_api_interface(name="IFoo")
class FooSerializer(serializers.Serializer):
    char_field = serializers.CharField(
        help_text="This is some help text for `char_field`"
    )
    decimal_field = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True
    )
    datetime_field = serializers.DateTimeField(allow_null=True, read_only=True)
    list_field_char_child = serializers.ListField(child=serializers.CharField())
    list_field_choice_child = serializers.ListField(
        child=serializers.ChoiceField(choices=("choiceA", "choiceB", "choiceC"))
    )
    dict_field = serializers.DictField()
    json_field = serializers.JSONField(write_only=True)
    choice_field = serializers.ChoiceField(
        choices=("choice1", "choice2", "choice3", 'choice"4')
    )
    write_only_serializer_field = InnerFooSerializer(
        write_only=True,
        many=True,
        help_text="Description of `write_only_serializer_field`",
    )
    read_only_serializer_field = InnerFooSerializer(
        read_only=True, many=True, allow_null=True
    )
    dict_field_with_integer_child = serializers.DictField(
        child=serializers.IntegerField()
    )
    dict_field_with_serializer_child = serializers.DictField(child=InnerFooSerializer())
    dict_field_with_list_serializer_child = serializers.DictField(
        child=InnerFooSerializer(many=True)
    )
    custom_field = MyCustomField(some_attribute="test string")


class FooWriteSerializer(FooSerializer):
    pass


class FooView(ViewSet):
    @ts_api_endpoint(
        path=("foo", "list"),
        description="Get a list of Foos",
        query_serializer=FooQuerySerializer,
        body_serializer=None,
        response_serializer=FooSerializer(many=True),
    )
    def list(self, request):
        pass

    @ts_api_endpoint(
        path=("foo", "create"),
        description="Create a Foo",
        query_serializer=None,
        body_serializer=FooWriteSerializer,
        response_serializer=FooSerializer,
    )
    def create(self, request, test=None):
        pass

    @ts_api_endpoint(
        path=("foo", "get"),
        description="Get a single Foo",
        query_serializer=None,
        body_serializer=None,
        response_serializer=FooSerializer,
    )
    def retrieve(self, request, pk):
        pass

    @ts_api_endpoint(
        path=("foo", "update"),
        description="Update a Foo",
        query_serializer=None,
        body_serializer=FooSerializer,
        response_serializer=FooSerializer,
    )
    def update(self, request, pk):
        pass

    @ts_api_endpoint(
        path=("foo", "delete"),
        description="Delete a Foo",
        query_serializer=None,
        body_serializer=None,
        response_serializer=SuccessSerializer,
    )
    def destroy(self, request, pk):
        pass
