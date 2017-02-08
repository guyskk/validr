import sys

import pytest
from validr import Invalid
from validr.validators import int_validator


def test_basic():
    validate = int_validator(0, 9)
    assert validate(0) == 0
    assert validate(9) == 9
    with pytest.raises(Invalid):
        assert validate(-1)
    with pytest.raises(Invalid):
        assert validate(10)


@pytest.mark.parametrize("value", [sys.maxsize, -sys.maxsize, 0])
def test_min_max(value):
    validate = int_validator()
    assert validate(value) == value


@pytest.mark.parametrize("value", [
    sys.maxsize + 1, -sys.maxsize - 1,
    float('INF'), float('NAN')
])
def test_min_max_invalid(value):
    validate = int_validator()
    with pytest.raises(Invalid):
        validate(value)
