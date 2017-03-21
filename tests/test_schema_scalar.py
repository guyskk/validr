import pytest
from validr import Invalid, SchemaError, SchemaParser

sp = SchemaParser()


def test_basic():
    f = sp.parse('int(0,9)')
    assert f(3) == 3
    with pytest.raises(Invalid):
        f(-1)


def test_optional_int():
    f = sp.parse('int&optional')
    assert f(None) is None
    with pytest.raises(Invalid):
        f('')


def test_optional_str():
    f = sp.parse('str&optional')
    assert f(None) == ''
    assert f('') == ''


@pytest.mark.parametrize('schema', [
    'int&default=5',
    'int&default=5&optional'
])
def test_default_int(schema):
    f = sp.parse(schema)
    assert f(None) == 5
    with pytest.raises(Invalid):
        f('')


@pytest.mark.parametrize('schema', [
    'str&default="x"',
    'str&default="x"&optional'
])
def test_default_str(schema):
    f = sp.parse(schema)
    assert f(None) == 'x'
    assert f('') == 'x'


def test_desc():
    f = sp.parse('int&desc="数字"')
    assert f(3) == 3


def test_invalid_default_value():
    schema = 'int(0,9)&default=-1'
    with pytest.raises(SchemaError):
        sp.parse(schema)


def test_validator_not_found():
    schema = 'unknown(0,9)'
    with pytest.raises(SchemaError):
        sp.parse(schema)
