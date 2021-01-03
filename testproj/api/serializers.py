from rest_framework import serializers


class MyCustomField(serializers.ReadOnlyField):
    def __init__(self, some_attribute, *args, **kwargs):
        self.some_attribute = some_attribute
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        return self.some_attribute
