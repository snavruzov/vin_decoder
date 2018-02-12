"""
REST view that captures HTTP requests consumes vin related parameters


Notice Django REST Framework serializer(BasicSerializer) is used to handle Django Model objects.
http://www.django-rest-framework.org/tutorial/1-serialization/
"""

import logging
from django.http import JsonResponse
from rest_framework import viewsets

from .serializers import BasicSerializer
from .models import Basic
from vinapi.services import decode_vin, vin_validator

logger = logging.getLogger(__name__)


class DecodeViewSet(viewsets.ReadOnlyModelViewSet):

    @staticmethod
    def decode(request, vin):
        """
        GET endpoint checks VIN values for the DB existence,
        if there is no details in the DB table switches to the decode_vin() function
        that requests a third-party service and stores extracted results in the database
        or returns empty JSON if some error occurred.
        Check for the server logs to track errors

        :param vin: Vehicle Identification Number, required, 17 characters, ISO 3779:2009
        https://www.iso.org/standard/52200.html
        :param request:
        :return: JSON response that contains VIN decoded details or error details
         if something wrong happened.
        """

        from vinapi.configs import status_codes
        # First validate GET passed VIN param
        # VIN better to be in uppercase to pass check-digit calculation
        vin = str.upper(vin)
        if vin_validator(vin):
            try:
                vindata = Basic.objects.get(pk=vin)
                logger.warning("VIN exists, retrieving from the database.")
                serializer = BasicSerializer(vindata, many=False)
                # No need to store and serialize JSON "status" field in the database
                s_data = serializer.data
                s_data['status'] = status_codes()['SUCCESS']
            except Basic.DoesNotExist:
                logger.warning("VIN doesn't exist in the database, retrieving and decoding manually.")
                s_data = decode_vin(vin=vin)

            return JsonResponse(s_data)
        else:
            logger.warning("Wrong VIN number, invalid check-digit calculation.")
            return JsonResponse({
                'VIN': vin,
                'status': status_codes()['VINERR'],
            })
