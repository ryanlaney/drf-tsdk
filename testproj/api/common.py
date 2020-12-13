from rest_framework import serializers


class SuccessSerializer(serializers.Serializer):
    serializer = serializers.BooleanField()
