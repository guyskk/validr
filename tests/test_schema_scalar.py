import pytest
from validr import Invalid, SchemaError, SchemaParser


def validate(schema, value):
    f = SchemaParser().parse(schema)
    return f(value)


def test_basic():
    schema = "int(0,9)"
    assert validate(schema, 3) == 3
    with pytest.raises(Invalid):
        validate(schema, -1)


def test_optional_int():
    schema = "int&optional"
    assert validate(schema, None) is None
    with pytest.raises(Invalid):
        validate(schema, "")


def test_optional_str():
    schema = "str&optional"
    assert validate(schema, None) == ""
    assert validate(schema, "") == ""


@pytest.mark.parametrize("schema", [
    "int&default=5",
    "int&default=5&optional"
])
def test_default_int(schema):
    assert validate(schema, None) == 5
    with pytest.raises(Invalid):
        validate(schema, "")


@pytest.mark.parametrize("schema", [
    'str&default="x"',
    'str&default="x"&optional'
])
def test_default_str(schema):
    assert validate(schema, None) == "x"
    assert validate(schema, "") == "x"


def test_desc():
    schema = 'int&desc="数字"'
    assert validate(schema, 3) == 3


def test_invalid_default_value():
    schema = "int(0,9)&default=-1"
    with pytest.raises(SchemaError):
        SchemaParser().parse(schema)


def test_validator_not_found():
    schema = "unknown(0,9)"
    with pytest.raises(SchemaError):
        SchemaParser().parse(schema)
