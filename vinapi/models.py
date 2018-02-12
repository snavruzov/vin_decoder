from django.core.exceptions import ValidationError
from jsoneditor.fields.postgres_jsonfield import JSONField
from datetime import datetime
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


"""
Django Model to map database table Basic fields.

The Basic Model will create a PostgreSQL table while the app bootstrap.

Note that fields dimensions and weight both uses 
JSONFiled field type to store jsonb data in the DB, PostgreSQL supports native json types starting
from version 9.3.
https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/forms/#jsonfield

 
"""


# Validation the field for the correct VIN standard,
# 17 character VIN standard was issued from 1980.
def validate_vin(value):
    from vinapi.services import vin_validator
    if not vin_validator(value):
        raise ValidationError(
            '%(value)s is not passed from check-digit validation.',
            params={'value': value},
        )


class Basic(models.Model):
    VIN = models.CharField(validators=[validate_vin], max_length=17, primary_key=True)
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1980), MaxValueValidator(datetime.now().year)])
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    color = models.CharField(max_length=100, blank=True)
    dimensions = JSONField(blank=True)
    weight = JSONField(blank=True)
