from rest_framework import serializers
from rest_framework.decorators import api_view

from drf_typescript_api_client import ts_api_client


class InnerInnerBarSerializer(serializers.Serializer):
    g = serializers.CharField()
    h = serializers.CharField()


class InnerBarSerializer(serializers.Serializer):
    d = serializers.CharField()
    e = serializers.CharField()
    f = InnerInnerBarSerializer()


class BarSerializer(serializers.Serializer):
    a = serializers.CharField()
    b = serializers.DecimalField(
        max_digits=7, decimal_places=6, allow_null=True)
    c = InnerBarSerializer(many=True)


@api_view(['GET'])
@ts_api_client(path=["bar"], urlconf=None, url="/api/v1/bar", query_serializer=None, request_serializer=None, response_serializer=BarSerializer(many=True))
def bar(request):
    pass
