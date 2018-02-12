"""
Serializing and deserializing the Basic
instances into representations such as json.
"""
from django.core.exceptions import ValidationError
from rest_framework import serializers
from datetime import datetime
from rest_framework.compat import MinValueValidator, MaxValueValidator

from .models import Basic


def validate_vin(value):
    from vinapi.services import vin_validator
    if not vin_validator(value):
        raise ValidationError(
            '%(value)s is not passed from check-digit validation.',
            params={'value': value},
        )


class BasicSerializer(serializers.Serializer):
    VIN = serializers.CharField(validators=[validate_vin], read_only=False)
    year = serializers.IntegerField(
        validators=[MinValueValidator(1980), MaxValueValidator(datetime.now().year)])
    make = serializers.CharField(max_length=100)
    model = serializers.CharField(max_length=100, allow_blank=True)
    type = serializers.CharField(max_length=100, allow_blank=True)
    color = serializers.CharField(max_length=100, allow_blank=True)
    dimensions = serializers.JSONField()
    weight = serializers.JSONField()

    def create(self, validated_data):
        """
        Create and return a new `Basic VIN detail` instance, given the validated data.
        """
        return Basic.objects.create(**validated_data)

    def update(self, instance, validated_data):
        pass
