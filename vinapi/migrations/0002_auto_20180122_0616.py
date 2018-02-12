# Generated by Django 2.0.1 on 2018-01-22 06:16

import django.core.validators
from django.db import migrations, models
import jsoneditor.fields.postgres_jsonfield
import vinapi.models


class Migration(migrations.Migration):

    dependencies = [
        ('vinapi', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basic',
            name='VIN',
            field=models.CharField(max_length=17, primary_key=True, serialize=False, validators=[vinapi.models.validate_vin]),
        ),
        migrations.AlterField(
            model_name='basic',
            name='dimensions',
            field=jsoneditor.fields.postgres_jsonfield.JSONField(blank=True),
        ),
        migrations.AlterField(
            model_name='basic',
            name='weight',
            field=jsoneditor.fields.postgres_jsonfield.JSONField(blank=True),
        ),
        migrations.AlterField(
            model_name='basic',
            name='year',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1980), django.core.validators.MaxValueValidator(2018)]),
        ),
    ]