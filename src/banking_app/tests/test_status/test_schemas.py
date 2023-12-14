import pytest

from pydantic import ValidationError

from src.banking_app.schemas.status import BaseStatusModel
from src.banking_app.schemas.status import StatusCreate
from src.banking_app.schemas.status import StatusFullUpdate
from src.banking_app.schemas.status import StatusPartialUpdate
from src.banking_app.schemas.status import StatusRetrieve


@pytest.fixture
def data():
    default_data = dict(status=100, description='Test description')
    return default_data


@pytest.mark.run(order=0.00_00)
class TestStatusField:

    @pytest.mark.parametrize(
        argnames='raw_status,clean_status',
        argvalues=(
            pytest.param(1, 1, id='status=1'),
            pytest.param('1', 1, id='status=\'1\''),
            pytest.param(True, 1, id='status=True'),
        ),
    )
    def test_valid_values(self, data, raw_status, clean_status):
        data['status'] = raw_status
        try:
            obj = BaseStatusModel(**data)
            assert obj.status == clean_status
        except Exception:
            assert False

    @pytest.mark.parametrize(
        argnames='status',
        argvalues=(
            pytest.param(0, id='status=0'),
            pytest.param(-1, id='status=-1'),
            pytest.param('0', id='status=\'0\''),
            pytest.param('-1', id='status=\'-1\''),
            pytest.param(float('inf'), id='status=float(\'inf\')'),
            pytest.param(float('-inf'), id='status=float(\'-inf\')'),
        ),
    )
    def test_must_be_positive(self, data, status):
        data['status'] = status
        with pytest.raises(ValidationError) as error:
            BaseStatusModel(**data)

        msg = 'Input should be greater than 0'
        if status in (float('inf'), float('-inf')):
            msg = 'Input should be a finite number'

        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == msg

    @pytest.mark.parametrize(
        argnames='status',
        argvalues=(
            pytest.param('Some status', id='status=\'Some status\''),
            pytest.param([1], id='status=[1]'),
            pytest.param(None, id='status=None'),
        ),
    )
    def test_can_be_only_digit(self, data, status):
        data['status'] = status
        with pytest.raises(ValidationError) as error:
            BaseStatusModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'].startswith('Input should be a valid integer')


@pytest.mark.run(order=0.00_01)
class TestDescriptionField:

    @pytest.mark.parametrize(
        argnames='raw_description,clean_description',
        argvalues=(
            pytest.param('s', 's', id='description=\'s\''),
            pytest.param('s' * 100, 's' * 100, id='description=\'s\' * 100'),
        ),
    )
    def test_valid_values(self, data, raw_description, clean_description):
        data['description'] = raw_description
        try:
            obj = BaseStatusModel(**data)
            assert obj.description == clean_description
        except Exception:
            assert False

    @pytest.mark.parametrize(
        argnames='description,message',
        argvalues=(
            pytest.param(
                '',
                'String should have at least 1 character',
                id='description=\'\'',
            ),
            pytest.param(
                's' * 101,
                'String should have at most 100 characters',
                id='description=\'s\' * 101',
            ),
        ),
    )
    def test_length_must_be_between_1_and_100(self, data, description, message):
        data['description'] = description
        with pytest.raises(ValidationError) as error:
            BaseStatusModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == message

    @pytest.mark.parametrize(
        argnames='description',
        argvalues=(
            pytest.param(False, id='description=False'),
            pytest.param(['s'], id='description=[\'s\']'),
            pytest.param(None, id='description=None'),
        ),
    )
    def test_can_be_only_string(self, data, description):
        data['description'] = description
        with pytest.raises(ValidationError) as error:
            BaseStatusModel(**data)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid string'


@pytest.mark.run(order=0.00_02)
class TestSideModels:

    @pytest.mark.parametrize(
        argnames='data,messages',
        argvalues=(
            pytest.param(
                dict(status=200, description='Test description'),
                None,
                id='with valid data'
            ),
            pytest.param(
                dict(),
                dict(status='Field required', description='Field required'),
                id='without required fields'
            ),
        ),
    )
    def test_StatusRetrieve(self, data, messages):
        if messages is None:
            obj = StatusRetrieve(**data)
            for k, v in data.items():
                assert getattr(obj, k) == v
                return

        with pytest.raises(ValidationError) as error:
            StatusRetrieve(**data)
        errors = error.value.errors()
        assert len(errors) == len(messages)
        for error in errors:
            assert error['msg'] == messages[error['loc'][0]]

    @pytest.mark.parametrize(
        argnames='data,messages',
        argvalues=(
            pytest.param(
                dict(status=200, description='Test description'),
                None,
                id='with valid data'
            ),
            pytest.param(
                dict(),
                dict(status='Field required', description='Field required'),
                id='without required fields'
            ),
        ),
    )
    def test_StatusCreate(self, data, messages):
        if messages is None:
            obj = StatusCreate(**data)
            for k, v in data.items():
                assert getattr(obj, k) == v
                return

        with pytest.raises(ValidationError) as error:
            StatusCreate(**data)
        errors = error.value.errors()
        assert len(errors) == len(messages)
        for error in errors:
            assert error['msg'] == messages[error['loc'][0]]

    @pytest.mark.parametrize(
        argnames='data,messages',
        argvalues=(
            pytest.param(
                dict(description='Test description'),
                None,
                id='with valid data'
            ),
            pytest.param(
                dict(),
                dict(description='Field required'),
                id='without required fields'
            ),
        ),
    )
    def test_StatusFullUpdate(self, data, messages):
        if messages is None:
            obj = StatusFullUpdate(**data)
            for k, v in data.items():
                assert getattr(obj, k) == v
                return

        with pytest.raises(ValidationError) as error:
            StatusFullUpdate(**data)
        errors = error.value.errors()
        assert len(errors) == len(messages)
        for error in errors:
            assert error['msg'] == messages[error['loc'][0]]

    @pytest.mark.parametrize(
        argnames='raw_data,clean_data',
        argvalues=(
            pytest.param(
                dict(description='Test description'),
                dict(description='Test description'),
                id='with valid data'
            ),
            pytest.param(
                dict(),
                dict(description=None),
                id='without optionals fields'
            ),
        ),
    )
    def test_StatusPartialUpdate(self, raw_data, clean_data):
        obj = StatusPartialUpdate(**raw_data)
        for k, v in clean_data.items():
            assert getattr(obj, k) == v
