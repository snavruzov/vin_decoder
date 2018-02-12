"""
VIN decoder services

Sample full VIN JSON response data received from the DecodeThis API
{
    decode: {
    status: "SUCCESS",
    Valid: "True",
    vehicle: [
        {
            body: "SEDAN 2-DR",
            driveline: "RWD",
            engine: "2.5L V6",
            Equip: [
                {
                    name: "Model Year",
                    unit: "",
                    value: "1981"
                },
                ...
            ],
            id: "97249",
            make: "Alfa Romeo",
            model: "GTV-6",
            trim: "Base",
            year: "1981"
        }
    ],
    version: "DECODE",
    VIN: "ZARAA6698B1001345"
    }
}

"""

import requests
import logging

from json import JSONDecodeError
from django.db import DatabaseError
from django.db import connection
from requests.exceptions import *

from vinapi.serializers import BasicSerializer
from vinapi.tasks import background
from .configs import *

logger = logging.getLogger(__name__)


def decode_vin(vin):
    """
    function that requests third-party URL(https://www.decodethis.com)
    and parses JSON response. Successful VIN details are stored in the DB.

    :param vin: VIN number
    :return: dictionary of VIN detail result
    """
    result = {}
    status = status_codes()['SUCCESS']
    try:
        # Authorise in the service DecodeThis for the API_KEY to be able to request VIN details
        r = requests.get(vin_api_url(vin=vin))
        objects = r.json()

        if objects and objects['decode']['status'] == 'SUCCESS':
            details = objects['decode']['vehicle']
            if details and isinstance(details, list):
                dimension_mapper = {}
                weight_mapper = {}
                color = ''
                for block in details[0]['Equip']:
                    if block['unit'] in dimension_units:
                        dimension_mapper[block['name']] = block['value']
                    if block['unit'] in weight_units:
                        weight_mapper[block['name']] = block['value']
                    if block['name'] == 'Exterior Color':
                        color = block['value']

                result = store_detail(
                    vin=vin,
                    year=details[0]['year'],
                    make=details[0]['make'],
                    model=details[0]['model'],
                    _type=details[0]['body'],
                    color=color,
                    dimensions=dimension_mapper,
                    weight=weight_mapper
                )

                # Namespace controlling to facilitate garbage-collector
                del dimension_mapper, weight_mapper, color, block, details
        elif objects:
            status = status_codes(code=objects['decode']['status'])['OTHER']
        else:
            status = status_codes()['NOTFOUND']

    except JSONDecodeError as jsonerr:
        logger.error('JSON decoding error, %s.' % jsonerr)
        status = status_codes(msg='JSON decoding error.')['APIERR']
        pass
    except ConnectionError or ConnectTimeout as connerr:
        logger.error('Connection error, %s.' % connerr)
        status = status_codes(msg='API service connection error.')['APIERR']
        pass
    except DatabaseError as dberr:
        logger.error('DataBase connection error, %s.' % dberr)
        status = status_codes()['DBERR']
        pass
    except KeyError as keyerr:
        logger.error('JSON key error, %s.' % keyerr)
        status = status_codes(msg='JSON key error.')['APIERR']
        pass

    result['status'] = status
    del status

    return result


def store_detail(vin, year, make, model, _type, color, dimensions, weight):
    """
    Parsing decoded VIN results into a pretty
    structured JSON fields and store in the database
    :param vin:
    :param year:
    :param make:
    :param model:
    :param _type:
    :param color:
    :param dimensions:
    :param weight:
    :return: dictionary result
    """
    result = {
        'VIN': vin,
        'year': int(year),
        'make': make,
        'model': model,
        'type': _type,
        'color': color,
        'dimensions': dimensions,
        'weight': weight
    }

    # check the queue for the vin code existence, if True ignore and don't
    # save twice throwing duplicate key errors
    if task_queue.count(vin) == 0:
        task_queue.append(vin)
        serialize_save(result)

    return result


@background
def serialize_save(result):
    """
    storing vin results using django-rest framework serializer object
    it is performed in the background thread, since it's unnecessary to
    wait for the database transaction time if the third-party service returned VIN details
    :param result: dictionary param
    :return: empty
    """
    serializer = BasicSerializer(data=result)
    if serializer.is_valid():
        serializer.save()
    # removing from the queue
    del task_queue[task_queue.index(result['VIN'])]
    # Django creates a new connection per thread and this needs to be manually closed:
    connection.close()


def vin_validator(vin):
    """
    function that validates VIN value using check-digit calculation
    following ISO 3779:2009 standard specification.
    Check-digit validation is compulsory for all road vehicles sold in North America.
    :param vin: VIN code
    :return: boolean value per validated VIN
    """
    def transliterate(c):
        return '0123456789.ABCDEFGH..JKLMN.P.R..STUVWXYZ'.index(c) % 10

    def check_digit(_vin):
        _map = '0123456789X'
        weights = '8765432X098765432'
        _sum = 0
        for i in range(0, 17):
            _sum += transliterate(_vin[i]) * _map.index(weights[i])
        return _map[_sum % 11]

    if len(vin) != 17:
        return False

    return check_digit(vin) == vin[8]
