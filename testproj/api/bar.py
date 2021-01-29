from rest_framework import serializers
from rest_framework.decorators import api_view

from drf_tsdk import ts_api_endpoint, ts_api_interface


@ts_api_interface(should_export=False)
class InnerInnerBarSerializer(serializers.Serializer):
    c1 = serializers.CharField()
    c2 = serializers.CharField()


@ts_api_interface(name="IInnerBar")
class InnerBarSerializer(serializers.Serializer):
    b1 = serializers.CharField()
    b2 = serializers.CharField()
    b3 = InnerInnerBarSerializer(
        allow_null=True, required=False)


@ts_api_interface(name="IBar")
class BarSerializer(serializers.Serializer):
    a1 = serializers.CharField()
    a2 = serializers.DecimalField(
        max_digits=7, decimal_places=6, allow_null=True)
    a3 = InnerBarSerializer(many=True, write_only=True)
    a4 = serializers.ListField(child=serializers.CharField())


@ts_api_endpoint(path=["bar"], query_serializer=None, body_serializer=None, response_serializer=BarSerializer(many=True))
@api_view(['GET'])
def bar(request):
    pass
