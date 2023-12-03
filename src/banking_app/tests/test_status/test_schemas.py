import pytest

from pydantic import ValidationError

from src.banking_app.schemas.status import StatusDescDTO


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
            obj = StatusDescDTO(status=raw_status, description='Description.')
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
            StatusDescDTO(status=status, description='Some description.')

        msg = 'Input should be greater than 0'
        if status in (float('inf'), float('-inf')):
            msg = 'Input should be a finite number'

        error = list(filter(
            lambda e: e.get('msg') == msg, error.value.errors()
        ))
        assert len(error) == 1

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
            StatusDescDTO(status=status, description='Some description')
        msg = 'Input should be a valid integer'
        error = list(filter(
            lambda e: e.get('msg', '').startswith(msg), error.value.errors()
        ))
        assert len(error) == 1


class TestDescriptionField:

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
    def test_length_must_be_between_1_and_100(self, description, message):
        with pytest.raises(ValidationError) as error:
            StatusDescDTO(status=100, description=description)
        error = list(filter(
            lambda e: e.get('msg') == message, error.value.errors()
        ))
        assert len(error) == 1

    @pytest.mark.parametrize(
        argnames='description',
        argvalues=(
            pytest.param(False, id='description=False'),
            pytest.param(None, id='description=None'),
            pytest.param(['s'], id='description=["s"]'),
        ),
    )
    def test_can_be_only_string(self, description):
        with pytest.raises(ValidationError) as error:
            StatusDescDTO(status=100, description=description)
        error = list(filter(
            lambda e: e.get('msg') == 'Input should be a valid string',
            error.value.errors()
        ))
        assert len(error) == 1
