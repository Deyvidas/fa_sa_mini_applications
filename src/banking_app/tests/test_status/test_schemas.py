import pytest

from pydantic import ValidationError

from src.banking_app.schemas.status import DescriptionOptional
from src.banking_app.schemas.status import DescriptionRequired
from src.banking_app.schemas.status import StatusRequired


@pytest.mark.run(order=0.00_00)
class TestStatusField:

    @pytest.mark.parametrize(
        argnames='raw_status,clean_status',
        argvalues=(
            pytest.param(1, 1, id='status=1'),
            pytest.param('1', 1, id='status="1"'),
            pytest.param(True, 1, id='status=True'),
        ),
    )
    def test_valid_values(self, raw_status, clean_status):
        try:
            obj = StatusRequired(status=raw_status)
            assert obj.status == clean_status
        except Exception:
            assert False

    @pytest.mark.parametrize(
        argnames='status',
        argvalues=(
            pytest.param(0, id='status=0'),
            pytest.param(-1, id='status=-1'),
            pytest.param('0', id='status="0"'),
            pytest.param('-1', id='status="-1"'),
            pytest.param(float('inf'), id='status=float("inf")'),
            pytest.param(float('-inf'), id='status=float("-inf")'),
        ),
    )
    def test_must_be_positive(self, status):
        with pytest.raises(ValidationError) as error:
            StatusRequired(status=status)

        msg = 'Input should be greater than 0'
        if status in (float('inf'), float('-inf')):
            msg = 'Input should be a finite number'

        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == msg

    @pytest.mark.parametrize(
        argnames='status',
        argvalues=(
            pytest.param('Some status', id='status="Some status"'),
            pytest.param([1], id='status=[1]'),
            pytest.param(None, id='status=None'),
        ),
    )
    def test_can_be_only_digit(self, status):
        with pytest.raises(ValidationError) as error:
            StatusRequired(status=status)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'].startswith('Input should be a valid integer')


@pytest.mark.run(order=0.00_01)
class TestDescriptionField:

    @pytest.mark.parametrize(
        argnames='field',
        argvalues=(
            pytest.param(DescriptionOptional, id='optional'),
            pytest.param(DescriptionRequired, id='required'),
        ),
    )
    @pytest.mark.parametrize(
        argnames='raw_description,clean_description',
        argvalues=(
            pytest.param('s', 's', id="description='s'"),
            pytest.param('s' * 100, 's' * 100, id="description='s' * 100"),
        ),
    )
    def test_valid_values(self, field, raw_description, clean_description):
        try:
            obj = field(description=raw_description)
            assert obj.description == clean_description
        except Exception:
            assert False

    @pytest.mark.parametrize(
        argnames='field',
        argvalues=(
            pytest.param(DescriptionOptional, id='optional'),
            pytest.param(DescriptionRequired, id='required'),
        ),
    )
    @pytest.mark.parametrize(
        argnames='description,message',
        argvalues=(
            pytest.param(
                '',
                'String should have at least 1 character',
                id='description=""',
            ),
            pytest.param(
                's' * 101,
                'String should have at most 100 characters',
                id='description="s" * 101',
            ),
        ),
    )
    def test_length_must_be_between_1_and_100(self, field, description, message):
        with pytest.raises(ValidationError) as error:
            field(description=description)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == message

    @pytest.mark.parametrize(
        argnames='field',
        argvalues=(
            pytest.param(DescriptionOptional, id='optional'),
            pytest.param(DescriptionRequired, id='required'),
        ),
    )
    @pytest.mark.parametrize(
        argnames='description',
        argvalues=(
            pytest.param(False, id='description=False'),
            pytest.param(['s'], id='description=["s"]'),
        ),
    )
    def test_can_be_only_string(self, field, description):
        with pytest.raises(ValidationError) as error:
            field(description=description)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == 'Input should be a valid string'

    @pytest.mark.parametrize(
        argnames='kwargs,message',
        argvalues=(
            pytest.param(
                dict(),
                'Field required',
                id='without arguments'
            ),
            pytest.param(
                dict(description=None),
                'Input should be a valid string',
                id='with None value'
            ),
        ),
    )
    def test_required_field(self, kwargs, message):
        with pytest.raises(ValidationError) as error:
            DescriptionRequired(**kwargs)
        errors = error.value.errors()
        assert len(errors) == 1
        assert errors[0]['msg'] == message

    @pytest.mark.parametrize(
        argnames='kwargs',
        argvalues=(
            pytest.param(dict(), id='without arguments'),
            pytest.param(dict(description=None), id='with None value'),
        ),
    )
    def test_optional_field(self, kwargs):
        dump = DescriptionOptional(**kwargs).model_dump()
        assert dump == {'description': None}
