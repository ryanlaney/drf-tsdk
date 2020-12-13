from rest_framework import serializers
from rest_framework.viewsets import ViewSet

from drf_typescript_api_client import ts_api_client

from .common import SuccessSerializer


class FooQuerySerializer(serializers.Serializer):
    q1 = serializers.UUIDField(
        required=True, help_text="Description of `q1`")
    q2 = serializers.DateField(required=False)
    q3 = serializers.DateField(required=False)
    q4 = serializers.BooleanField(
        required=False, help_text="Description of `q2`")


class FooSerializer(serializers.Serializer):
    x1 = serializers.CharField(help_text="This is some help text for `x`")
    x2 = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True)
    x3 = serializers.DateTimeField(allow_null=True, read_only=True)
    x4 = serializers.ListField(child=serializers.CharField())
    x5 = serializers.DictField()
    x6 = serializers.JSONField(write_only=True)


class FooView(ViewSet):

    @ts_api_client(path=("foo", "list"), urlconf=None, url="/api/v1/foo", query_serializer=FooQuerySerializer, request_serializer=None, response_serializer=FooSerializer(many=True))
    def list(self, request):
        pass

    @ts_api_client(path=("foo", "create"), urlconf=None, url="/api/v1/foo", query_serializer=None, request_serializer=FooSerializer, response_serializer=FooSerializer)
    def create(self, request):
        pass

    @ts_api_client(path=("foo", "get"), urlconf=None, url="/api/v1/foo/${pk}", query_serializer=None, request_serializer=None, response_serializer=FooSerializer)
    def retrieve(self, request, pk):
        pass

    @ts_api_client(path=("foo", "update"), urlconf=None, url="/api/v1/foo/${pk}", query_serializer=None, request_serializer=FooSerializer, response_serializer=FooSerializer)
    def update(self, request, pk):
        pass

    @ts_api_client(path=("foo", "delete"), urlconf=None, url="/api/v1/foo/${pk}", query_serializer=None, request_serializer=None, response_serializer=SuccessSerializer)
    def destroy(self, request, pk):
        pass
