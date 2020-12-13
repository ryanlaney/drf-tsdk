from rest_framework import serializers
from rest_framework.decorators import api_view

from drf_typescript_api_client import ts_api_client


class InnerInnerBarSerializer(serializers.Serializer):
    c1 = serializers.CharField()
    c2 = serializers.CharField()


class InnerBarSerializer(serializers.Serializer):
    b1 = serializers.CharField()
    b2 = serializers.CharField()
    b3 = InnerInnerBarSerializer()


class BarSerializer(serializers.Serializer):
    a1 = serializers.CharField()
    a2 = serializers.DecimalField(
        max_digits=7, decimal_places=6, allow_null=True)
    a3 = InnerBarSerializer(many=True)


@api_view(['GET'])
@ts_api_client(path=["bar"], urlconf=None, url="/api/v1/bar", query_serializer=None, request_serializer=None, response_serializer=BarSerializer(many=True))
def bar(request):
    pass
