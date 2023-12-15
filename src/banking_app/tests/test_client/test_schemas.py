import pytest

from copy import deepcopy

from datetime import timedelta

from random import randint
from pydantic import ValidationError
from typing import Any

from src.banking_app.conf import test_settings
from src.banking_app.schemas.client import BaseClientModel
from src.banking_app.schemas.client import ClientCreate
from src.banking_app.schemas.client import ClientFullUpdate
from src.banking_app.schemas.client import ClientPartialUpdate
from src.banking_app.schemas.client import ClientRetrieve
from src.banking_app.schemas.status import StatusRetrieve
from src.banking_app.tests.test_status.test_schemas import status_data
from src.banking_app.types.client import SexEnum


def client_data() -> dict[str, Any]:
    status = StatusRetrieve(**status_data())
    data = dict(
        client_id=24,
        full_name="Zimin Denis Dmitrievich",
        birth_date=test_settings.get_date_today() - timedelta(days=360),
        sex=SexEnum.MALE,
        phone="9272554839",
        doc_num="92 31",
        doc_series="865734",
        reg_date=test_settings.get_date_today(),
        VIP_flag=False,
        status=status,
    )
    return deepcopy(data)


@pytest.fixture
def data():
    return client_data()


@pytest.mark.run(order=0.01_00)
class TestClientIdField:

    @pytest.mark.parametrize(
        argnames='raw_value,clean_value',
        argvalues=(
            pytest.param(1, 1, id='client_id=1'),
            pytest.param('1', 1, id='client_id=\'1\''),
            pytest.param(True, 1, id='client_id=True'),
        ),
    )
    def test_valid_values(self, data, raw_value, clean_value):
        data['client_id'] = raw_value
        obj = BaseClientModel(**data)
        assert obj.client_id == clean_value

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(0, id='client_id=0'),
            pytest.param(-1, id='client_id=-1'),
            pytest.param('0', id='client_id=\'0\''),
            pytest.param('-1', id='client_id=\'-1\''),
            pytest.param(float('inf'), id='client_id=float(\'inf\')'),
            pytest.param(float('-inf'), id='client_id=float(\'-inf\')'),
        ),
    )
    def test_must_be_positive(self, data, value):
        data['client_id'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)

        msg = 'Input should be greater than 0'
        if value in (float('inf'), float('-inf')):
            msg = 'Input should be a finite number'

        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == msg

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param('Some value', id='client_id=\'Some value\''),
            pytest.param([1], id='client_id=[1]'),
            pytest.param(None, id='client_id=None'),
        ),
    )
    def test_can_be_only_digit(self, data, value):
        data['client_id'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'].startswith('Input should be a valid integer')


@pytest.mark.run(order=0.01_01)
class TestFullNameField:
    short_valid_string = f'A{'a' * 2} V{'v' * 1} Z{'z' * 2}'
    long_valid_string = f'A{'a' * 83} V{'v' * 84} Z{'z' * 83}'
    used_pattern = r'^[A-Z][a-z]+( [A-Z][a-z]+){2}$'

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(short_valid_string, id='Name Lname Fname with len(10)'),
            pytest.param(long_valid_string, id='Name Lname Fname with len(255)'),
        ),
    )
    def test_valid_values(self, data, value):
        data['full_name'] = value
        obj = BaseClientModel(**data)
        assert obj.full_name == value

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(
                short_valid_string.lower(),
                id='3 lower strings'
            ),
            pytest.param(
                short_valid_string.upper(),
                id='3 upper strings'
            ),
            pytest.param(
                short_valid_string + '1',
                id='the string included digit'
            ),
            pytest.param(
                short_valid_string + 'ы',
                id='the string included non-latin character'
            ),
            pytest.param(
                short_valid_string + '!',
                id='the string included punctuation'
            ),
        ),
    )
    def test_must_contain_3_capitalized_string(self, data, value):
        data['full_name'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == f'String should match pattern \'{self.used_pattern}\''

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(12, id='full_name=12'),
            pytest.param(False, id='full_name=False'),
            pytest.param(['Aaa Vv Zzz'], id='full_name=[\'Aaa Vv Zzz\']'),
            pytest.param(None, id='full_name=None'),
        ),
    )
    def test_must_contain_only_string(self, data, value):
        data['full_name'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid string'


@pytest.mark.run(order=0.01_02)
class TestBirthDateField:

    @pytest.mark.parametrize(
        argnames='raw_value,clean_value',
        argvalues=(
            pytest.param(
                client_data()['reg_date'],
                client_data()['reg_date'],
                id='birth_date == reg_date'
            ),
            pytest.param(
                client_data()['reg_date'] - timedelta(days=1),
                client_data()['reg_date'] - timedelta(days=1),
                id='birth_date < reg_date'
            ),
            pytest.param(
                str(client_data()['reg_date']),
                client_data()['reg_date'],
                id='date as string'
            ),
        ),
    )
    def test_valid_values(self, freezer, data, raw_value, clean_value):
        data['birth_date'] = raw_value
        obj = BaseClientModel(**data)
        assert obj.birth_date == clean_value

    def test_cant_be_in_future(self, freezer, data):
        data['birth_date'] = test_settings.get_date_today() + timedelta(days=1)
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == (
            f'Birth date cannot be after {test_settings.get_date_today()}.'
        )

    def test_cant_be_after_registration_date(self, freezer, data):
        data['reg_date'] = (rd := data['reg_date'] - timedelta(days=1))
        data['birth_date'] = (bd := rd + timedelta(days=1))
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == (
            f'Registration date ({rd}) cannot be before the client birth date ({bd}).'
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(False, id='birth_date=False'),
            pytest.param([client_data()['birth_date']], id='birth_date=[date]'),
            pytest.param(None, id='birth_date=None'),
        ),
    )
    def test_must_be_only_date_or_compatible_to_date_string(self, data, value):
        data['birth_date'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid date'


@pytest.mark.run(order=0.01_03)
class TestSexField:

    @pytest.mark.parametrize(
        argnames='raw_value,clean_value',
        argvalues=(
            pytest.param(SexEnum.MALE, SexEnum.MALE, id='sex=SexEnum.MALE'),
            pytest.param(SexEnum.FEMALE, SexEnum.FEMALE, id='sex=SexEnum.FEMALE'),
            pytest.param('M', SexEnum.MALE, id='sex=\'M\''),
            pytest.param('F', SexEnum.FEMALE, id='sex=\'F\''),
        ),
    )
    def test_valid_values(self, data, raw_value, clean_value):
        data['sex'] = raw_value
        obj = BaseClientModel(**data)
        assert obj.sex == clean_value

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param('m', id='sex=\'m\''),
            pytest.param('f', id='sex=\'f\''),
            pytest.param(False, id='sex=False'),
            pytest.param(12, id='sex=12'),
            pytest.param([SexEnum.MALE, SexEnum.FEMALE], id='sex=[SexEnum.MALE, SexEnum.FEMALE]'),
        ),
    )
    def test_invalid_values(self, data, value):
        data['sex'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be \'M\' or \'F\''


@pytest.mark.run(order=0.01_04)
class TestPhoneField:

    def test_valid_values(self, data):
        phone = str(randint(10 ** 9, 10 ** 10 - 1))
        data['phone'] = phone
        obj = BaseClientModel(**data)
        assert obj.phone == phone

    @pytest.mark.parametrize(
        argnames='value,error_msg',
        argvalues=(
            pytest.param(
                '',
                'String should have at least 10 characters',
                id='phone=\'\''
            ),
            pytest.param(
                '1',
                'String should have at least 10 characters',
                id='phone=\'1\''
            ),
            pytest.param(
                '1' * 9,
                'String should have at least 10 characters',
                id='phone=\'1\' * 9'
            ),
            pytest.param(
                '1' * 11,
                'String should have at most 10 characters',
                id='phone=\'1\' * 11'
            ),
            pytest.param(
                '1' * 9 + 'a',
                'String should match pattern \'^[\\d]{10}$\'',
                id='phone=\'1\' * 9 + \'a\''
            ),
        ),
    )
    def test_must_contain_string_digits_length_10(self, data, value, error_msg):
        data['phone'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == error_msg

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(randint(10 ** 9, 10 ** 10 - 1), id='phone=randint(10 ** 9, 10 ** 10 - 1)'),
            pytest.param([str(randint(10 ** 9, 10 ** 10 - 1))], id='phone=[str(randint(10 ** 9, 10 ** 10 - 1))]'),
            pytest.param(False, id='phone=False'),
            pytest.param(None, id='phone=None'),
        ),
    )
    def test_must_contain_only_string(self, data, value):
        data['phone'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid string'


@pytest.mark.run(order=0.01_05)
class TestDocNumField:

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param('00 99', id='doc_num=\'00 99\''),
        ),
    )
    def test_valid_values(self, data, value):
        data['doc_num'] = value
        obj = BaseClientModel(**data)
        assert obj.doc_num == value

    @pytest.mark.parametrize(
        argnames='value,error_message',
        argvalues=(
            pytest.param(
                '0099',
                'String should have at least 5 characters',
                id='doc_num=\'0099\''
            ),
            pytest.param(
                '009a',
                'String should have at least 5 characters',
                id='doc_num=\'009a\''
            ),
            pytest.param(
                '00599',
                'String should match pattern \'^[\\d]{2} [\\d]{2}$\'',
                id='doc_num=\'00599\''
            ),
            pytest.param(
                'a0 99',
                'String should match pattern \'^[\\d]{2} [\\d]{2}$\'',
                id='doc_num=\'a0 99\''
            ),
            pytest.param(
                '00  99',
                'String should have at most 5 characters',
                id='doc_num=\'00  99\''
            ),
        ),
    )
    def test_must_be_string_with_digits_len_5_valid_format(self, data, value, error_message):
        data['doc_num'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == error_message

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(None, id='doc_num=None'),
            pytest.param(9900, id='doc_num=9900'),
            pytest.param(True, id='doc_num=True'),
            pytest.param(['00 99'], id='doc_num=[\'00 99\']'),
        ),
    )
    def test_must_contain_only_string(self, data, value):
        data['doc_num'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid string'


@pytest.mark.run(order=0.01_06)
class TestDocSeriesField:

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param('005599', id='doc_series=\'005599\''),
        ),
    )
    def test_valid_values(self, data, value):
        data['doc_series'] = value
        obj = BaseClientModel(**data)
        assert obj.doc_series == value

    @pytest.mark.parametrize(
        argnames='value,error_message',
        argvalues=(
            pytest.param(
                '00599',
                'String should have at least 6 characters',
                id='doc_series=\'00599\''),
            pytest.param(
                '00559W',
                'String should match pattern \'^[\\d]{6}$\'',
                id='doc_series=\'00559W\''),
            pytest.param(
                '005 99',
                'String should match pattern \'^[\\d]{6}$\'',
                id='doc_series=\'005 99\''),
            pytest.param(
                '005 599',
                'String should have at most 6 characters',
                id='doc_series=\'005 599\''),
        ),
    )
    def test_must_be_string_with_digits_len_6(self, data, value, error_message):
        data['doc_series'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == error_message

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(995500, id='doc_series=995500'),
            pytest.param(['005599'], id='doc_series=[\'005599\']'),
            pytest.param(None, id='doc_series=None'),
            pytest.param(True, id='doc_series=True'),
        ),
    )
    def test_must_contain_only_string(self, data, value):
        data['doc_series'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid string'


@pytest.mark.run(order=0.01_07)
class TestRegDateField:

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(test_settings.get_date_today(), id='reg_date=date.today()'),
            pytest.param(str(test_settings.get_date_today()), id='reg_date=str(date.today())'),
        ),
    )
    def test_valid_values(self, freezer, data, value):
        data['reg_date'] = value
        obj = BaseClientModel(**data)
        assert obj.reg_date == test_settings.get_date_today()

    def test_cant_be_in_future(self, freezer, data):
        data['reg_date'] = test_settings.get_date_today() + timedelta(days=1)
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == (
            f'Registration date cannot be after {test_settings.get_date_today()}.'
        )

    def test_cant_be_earlier_than_birth_date(self, freezer, data):
        data['birth_date'] = (bd := test_settings.get_date_today())
        data['reg_date'] = (rd := bd - timedelta(days=1))
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == (
            f'Registration date ({rd}) cannot be before the client birth date ({bd}).'
        )

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(False, id='reg_date=False'),
            pytest.param([client_data()['reg_date']], id='reg_date=[date]'),
            pytest.param(None, id='reg_date=None'),
        ),
    )
    def test_must_be_only_date_or_compatible_to_date_string(self, data, value):
        data['reg_date'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid date'


@pytest.mark.run(order=0.01_08)
class TestVipFlagField:

    @pytest.mark.parametrize(
        argnames='values',
        argvalues=(
            pytest.param((True, False), id='VIP_flag=True|False'),
            pytest.param(('true', 'false'), id='VIP_flag=\'true\'|\'false\''),
            pytest.param(('yes', 'no'), id='VIP_flag=\'yes\'|\'no\''),
            pytest.param(('on', 'off'), id='VIP_flag=\'on\'|\'off\''),
            pytest.param((1, 0), id='VIP_flag=1|0'),
            pytest.param(('1', '0'), id='VIP_flag=\'1\'|\'0\''),
            pytest.param(('t', 'f'), id='VIP_flag=\'t\'|\'f\''),
            pytest.param(('y', 'n'), id='VIP_flag=\'y\'|\'n\''),
        ),
    )
    def test_valid_values(self, data, values):
        for raw_value, clean_value in zip(values, (True, False)):
            data['VIP_flag'] = raw_value
            obj = BaseClientModel(**data)
            assert obj.VIP_flag is clean_value

    @pytest.mark.parametrize(
        argnames='value',
        argvalues=(
            pytest.param(None, id='VIP_flag=None'),
            pytest.param(['true'], id='VIP_flag=[\'true\']'),
        ),
    )
    def test_invalid_values(self, data, value):
        data['VIP_flag'] = value
        with pytest.raises(ValidationError) as error:
            BaseClientModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid boolean'


@pytest.mark.run(order=0.01_09)
class TestSideModels:

    @pytest.mark.parametrize(
        argnames='exclude',
        argvalues=(
            pytest.param('__not__', id='with all fields'),
            pytest.param('__all__', id='without fields'),
        ),
    )
    @pytest.mark.parametrize(
        argnames='model,required,defaults',
        argvalues=(
            pytest.param(
                ClientRetrieve,
                dict(
                    client_id='Field required',
                    full_name='Field required',
                    birth_date='Field required',
                    sex='Field required',
                    phone='Field required',
                    doc_num='Field required',
                    doc_series='Field required',
                    reg_date='Field required',
                    VIP_flag='Field required',
                    status='Field required',
                ),
                dict(),
                id='ClientRetrieve'
            ),
            pytest.param(
                ClientCreate,
                dict(
                    full_name='Field required',
                    birth_date='Field required',
                    sex='Field required',
                    phone='Field required',
                    doc_num='Field required',
                    doc_series='Field required',
                ),
                dict(
                    client_id=None,
                    reg_date=None,
                    VIP_flag=None,
                    status=None,
                ),
                id='ClientCreate'
            ),
            pytest.param(
                ClientFullUpdate,
                dict(
                    full_name='Field required',
                    birth_date='Field required',
                    sex='Field required',
                    phone='Field required',
                    doc_num='Field required',
                    doc_series='Field required',
                ),
                dict(
                    client_id=None,
                    reg_date=None,
                    VIP_flag=None,
                    status=None,
                ),
                id='ClientFullUpdate'
            ),
            pytest.param(
                ClientPartialUpdate,
                dict(),
                dict(
                    client_id=None,
                    full_name=None,
                    birth_date=None,
                    sex=None,
                    phone=None,
                    doc_num=None,
                    doc_series=None,
                    reg_date=None,
                    VIP_flag=None,
                    status=None,
                ),
                id='ClientPartialUpdate'
            ),
        ),
    )
    def test_required_fields(self, data, exclude, model, required, defaults):
        if exclude == '__not__':
            obj = model(**data)
            for f, v in data.items():
                assert getattr(obj, f) == v
            return

        # Check if an exception was raised when the required field was missed.
        if len(required) != 0:
            with pytest.raises(ValidationError) as error:
                model()
            errors = error.value.errors()
            assert len(errors) == len(required)
            for error in errors:
                assert error['msg'] == required[error['loc'][0]]

        # Check the correct assignment of default values for empty optional fields.
        if len(defaults) != 0:
            data_without, expected_data = deepcopy(data), deepcopy(data)
            for k, v in defaults.items():
                data_without.pop(k)
                expected_data[k] = v

            obj = model(**data_without)
            for k, v in expected_data.items():
                assert getattr(obj, k) == v
