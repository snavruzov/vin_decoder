from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse, resolve

from vinapi.models import Basic
from vinapi.services import decode_vin, vin_validator
from vinapi.urls import decode_detail


class BasicModelTest(TestCase):

    def test_db_table_fields_for_json_format(self):
        dimensions = {
            'Wheelbase': '120.90',
            'Track Rear': '61.50',
            'Track Front': '60.90',
            'Cargo Volume': '13.00',
            'Rear Legroom': '41.90',
            'Front Legroom': '41.90',
            'Overall Width': '73.30',
            'Rear Headroom': '38.10',
            'Front Headroom': '37.50',
            'Overall Height': '56.10',
            'Overall Length': '201.70',
            'Passenger Volume': '107.00',
            'Turning Diameter': '40.00',
            'Rear Shoulder Room': '58.40',
            'Front Shoulder Room': '58.40'
        }

        weight = {
            'Curb Weight-automatic': '4288'
        }

        vin = 'WBAGH83441DP29517'
        year = 2001
        make = 'BMW'
        model = '7-Series'
        _type = 'SEDAN 4-DR'
        color = 'Red'

        Basic.objects.create(
            VIN=vin,
            year=year,
            make=make,
            model=model,
            type=_type,
            color=color,
            dimensions=dimensions,
            weight=weight
        )

        basic_object = Basic.objects.filter(
            VIN=vin,
            dimensions__contains={'Wheelbase': '120.90'})

        self.assertQuerysetEqual(basic_object, ['<Basic: Basic object (WBAGH83441DP29517)>'])

    def test_db_table_fields_for_validation_error_for_year_value_gt_current(self):
        dimensions = {}
        weight = {}

        vin = 'WBAGH83441DP29517'
        year = 2055
        make = 'BMW'
        model = '7-Series'
        _type = 'SEDAN 4-DR'
        color = 'Red'

        create = Basic.objects.create(
            VIN=vin,
            year=year,
            make=make,
            model=model,
            type=_type,
            color=color,
            dimensions=dimensions,
            weight=weight
        )

        '''Raise for Validators check'''
        self.assertRaisesMessage(ValidationError, create.full_clean)

    def test_db_table_fields_for_validation_error_for_year_value_lt_1980(self):
        dimensions = {}
        weight = {}

        vin = 'WBAGH83441DP29517'
        year = 1950
        make = 'BMW'
        model = '7-Series'
        _type = 'SEDAN 4-DR'
        color = 'Red'

        create = Basic.objects.create(
            VIN=vin,
            year=year,
            make=make,
            model=model,
            type=_type,
            color=color,
            dimensions=dimensions,
            weight=weight
        )

        '''Raise for Validators check'''
        self.assertRaisesMessage(ValidationError, create.full_clean)

    def test_db_table_fields_for_validation_error_for_vin_value_check_digit(self):
        dimensions = {}
        weight = {}

        vin = 'SBAGH83441DP29517'
        year = 2005
        make = 'BMW'
        model = '7-Series'
        _type = 'SEDAN 4-DR'
        color = 'Red'

        create = Basic.objects.create(
            VIN=vin,
            year=year,
            make=make,
            model=model,
            type=_type,
            color=color,
            dimensions=dimensions,
            weight=weight
        )

        '''Raise for Validators check'''
        self.assertRaisesMessage(ValidationError, create.full_clean)


class VINDecoderTest(TestCase):
    def test_decode_vin_api_service_json_parser_for_exception(self):

        vin_err_samples = '123379N701843'  # VIN format that the URL service returns 500 error

        for vin in vin_err_samples:
            decode_vin(vin)
            self.assertRaisesMessage(KeyError, 'decode')

    def test_decode_vin_api_service_json_parser_for_success(self):
        vin_ok_samples = [
            '1M8GDM9AXKP042788',  # 102C3 Intercity MCI BUS, incomplete VIN detail
            '4VZVU1E90JC083273',  # BMW 7-Series, SEDAN, complete VIN detail
        ]

        import json
        for vin in vin_ok_samples:
            res = decode_vin(vin)
            self.assertJSONNotEqual(json.dumps(res), {})


class ViewTest(TestCase):
    def test_decode_view_status_code(self):
        url = reverse('decode', args=['4VZVU1E9XJC084012'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_decode_view_with_lower_case_vin(self):
        url = reverse('decode', args=['jnkcp01P1NT306746'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_decode_url_resolves_decode_view(self):
        view = resolve('/api/v1/decode/1NKDX4TX1JJ194335')
        self.assertEquals(view.func, decode_detail)

    def test_decode_view_json_for_invalid_vin_code(self):
        url = reverse('decode', args=['SBAGH83441DP29517'])
        response = self.client.get(url)
        self.assertJSONEqual(response.content, {
                                'status': {
                                    'code': "VINERR",
                                    'message': "VIN code error, invalid check-digit"
                                },
                                'VIN': "SBAGH83441DP29517"
                            })


class VINValidatorTest(TestCase):
    def test_vin_for_valid_check_digit(self):
        vin_samples = [
            'WBAGH83441DP29517',
            '1M8GDM9AXKP042788']

        for vin in vin_samples:
            self.assertTrue(vin_validator(vin))

    def test_vin_for_invalid_check_digit(self):
        vin_samples = [
            'SBAGH83441DP29517',
            'WM8GDM9AXKP04278']

        for vin in vin_samples:
            self.assertFalse(vin_validator(vin))


class VINStatusCodeTest(TestCase):

    def test_vin_status_codes_for_json_fields(self):
        from vinapi.configs import status_codes
        status = status_codes()['APIERR']
        self.assertDictEqual(status, {'code': 'APIERR', 'message': ''})
        status = status_codes()['SUCCESS']
        self.assertDictEqual(status, {'code': 'SUCCESS', 'message': ''})
        status = status_codes(msg='db connection error')['DBERR']
        self.assertDictEqual(status, {
            'code': 'DBERR',
            'message': 'db connection error.'
        })
        status = status_codes()['NOTFOUND']
        self.assertDictEqual(status, {
            'code': 'NOTFOUND',
            'message': 'object is empty'
        })
        status = status_codes()['VINERR']
        self.assertDictEqual(status, {
            'code': 'VINERR',
            'message': 'VIN code error, invalid check-digit'
        })
        status = status_codes(code='ZULU_TANGO')['OTHER']
        self.assertDictEqual(status, {'code': 'ZULU_TANGO', 'message': ''})
