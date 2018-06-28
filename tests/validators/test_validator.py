import pytest
from validr import T, SchemaError, Compiler


def test_invalid_default():
    with pytest.raises(SchemaError):
        Compiler().compile(T.int.default('abc'))
