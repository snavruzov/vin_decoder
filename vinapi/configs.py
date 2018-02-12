# Queue list that holds VIN elements, candidate elements to be stored in the database
task_queue = []


def vin_api_url(vin, api_key='jUYdFF3AtxKqmuazznR2'):
    """
    URL of the service to retrieve VIN details, the service is passed
    {vin} and api_{key} params, if no key passed, default api key will be used
    :param vin: VIN number
    :param api_key: Third-party API service key,
    the service requires an authorization to get the key
    :return: URL string
    """
    return 'https://www.decodethis.com/webservices/decodes/' \
           '{vin}/{key}/1.json'.format(vin=vin, key=api_key)


# Vehicle dimensions measure units
dimension_units = ['in.', 'cu.ft.']
# Vehicle weight measure units
weight_units = ['lbs']


def status_codes(msg='', code=''):
    """
    Status codes that represented in JSON response, indicates VIN decode success
    JSON contains code and message fields that describe how the decoding process handled
    :param msg: manual message to be displayed
    :param code: manual code to be displayed
    :return: dictionary result
    """
    codes = {
        'APIERR': {'code': 'APIERR', 'message': '%s' % msg},
        'SUCCESS': {'code': 'SUCCESS', 'message': '%s' % msg},
        'DBERR': {
            'code': 'DBERR',
            'message': '%s.' % msg if msg else 'something wrong in database level'
        },
        'NOTFOUND': {
            'code': 'NOTFOUND',
            'message': '%s.' % msg if msg else 'object is empty'
        },
        'VINERR': {
            'code': 'VINERR',
            'message': '%s.' % msg if msg else 'VIN code error, invalid check-digit'
        },
        'OTHER': {'code': '%s' % code, 'message': '%s' % msg}
    }

    return codes


