import pytest

from copy import deepcopy

from pydantic import TypeAdapter
from pydantic import ValidationError

from random import choice
from typing import Sequence

from src.banking_app.schemas import BaseStatusModel
from src.banking_app.schemas import StatusModelWithRelations
from src.banking_app.schemas import StatusCreate
from src.banking_app.schemas import StatusFullUpdate
from src.banking_app.schemas import StatusPartialUpdate
from src.banking_app.schemas import StatusRetrieve


get_dto_from_dict = TypeAdapter(BaseStatusModel).validate_python


@pytest.fixture
def data_status(statuses_dto: Sequence[StatusModelWithRelations]):
    return choice(statuses_dto).model_dump()


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
    def test_valid_values(self, data_status, raw_status, clean_status):
        data_status['status'] = raw_status
        try:
            obj = get_dto_from_dict(data_status)
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
    def test_must_be_positive(self, data_status, status):
        data_status['status'] = status
        with pytest.raises(ValidationError) as error:
            get_dto_from_dict(data_status)

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
    def test_can_be_only_digit(self, data_status, status):
        data_status['status'] = status
        with pytest.raises(ValidationError) as error:
            get_dto_from_dict(data_status)
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
    def test_valid_values(self, data_status, raw_description, clean_description):
        data_status['description'] = raw_description
        try:
            obj = get_dto_from_dict(data_status)
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
    def test_length_must_be_between_1_and_100(self, data_status, description, message):
        data_status['description'] = description
        with pytest.raises(ValidationError) as error:
            get_dto_from_dict(data_status)
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
    def test_can_be_only_string(self, data_status, description):
        data_status['description'] = description
        with pytest.raises(ValidationError) as error:
            get_dto_from_dict(data_status)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid string'


@pytest.mark.run(order=0.00_02)
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
                BaseStatusModel,
                dict(
                    status='Field required',
                    description='Field required',
                ),
                dict(),
                id='BaseStatusModel'
            ),
            pytest.param(
                StatusModelWithRelations,
                dict(
                    status='Field required',
                    description='Field required',
                    clients='Field required',
                ),
                dict(),
                id='StatusModelWithRelations'
            ),
            pytest.param(
                StatusRetrieve,
                dict(
                    status='Field required',
                    description='Field required',
                    clients='Field required',
                ),
                dict(),
                id='StatusRetrieve'
            ),
            pytest.param(
                StatusCreate,
                dict(
                    status='Field required',
                    description='Field required',
                ),
                dict(),
                id='StatusCreate'
            ),
            pytest.param(
                StatusFullUpdate,
                dict(
                    status='Field required',
                    description='Field required',
                ),
                dict(
                ),
                id='StatusFullUpdate'
            ),
            pytest.param(
                StatusPartialUpdate,
                dict(),
                dict(
                    status=None,
                    description=None,
                ),
                id='StatusPartialUpdate'
            ),
        ),
    )
    def test_required_fields(self, data_status, exclude, model, required, defaults):
        get_dto_from_dict = TypeAdapter(model).validate_python
        all_fields = set(required.keys()) | set(defaults.keys())

        if exclude == '__not__':
            obj = get_dto_from_dict(data_status)
            for f in all_fields:
                assert getattr(obj, f) == data_status[f]
            return

        # Check if an exception was raised when the required field was missed.
        if len(required) != 0:
            with pytest.raises(ValidationError) as error:
                get_dto_from_dict(dict())
            errors = error.value.errors()
            assert len(errors) == len(required)
            for error in errors:
                assert error['msg'] == required[error['loc'][0]]

        # Check the correct assignment of default values for empty optional fields.
        if len(defaults) != 0:
            data_without, expected_data = deepcopy(data_status), deepcopy(data_status)
            for k, v in defaults.items():
                data_without.pop(k)
                expected_data[k] = v

            obj = get_dto_from_dict(data_without)
            for f in all_fields:
                assert getattr(obj, f) == expected_data[f]
