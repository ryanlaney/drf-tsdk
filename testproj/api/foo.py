from rest_framework import serializers
from rest_framework.viewsets import ViewSet

from drf_typescript_api_client import ts_api_client

from .common import SuccessSerializer


class FooQuerySerializer(serializers.Serializer):
    user = serializers.UUIDField(required=True)
    from_ = serializers.DateField(required=False)
    to = serializers.DateField(required=False)
    archived = serializers.BooleanField(required=False)


class FooSerializer(serializers.Serializer):
    x = serializers.CharField()
    y = serializers.DecimalField(
        max_digits=12, decimal_places=2, allow_null=True)
    z = serializers.DateTimeField(allow_null=True, read_only=True)


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
