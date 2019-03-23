from datetime import date

import pytest
from validr import Invalid, SchemaError, Compiler, T

from .helper import schema_error_position

_ = Compiler().compile


def test_optional():
    assert _(T.int.optional)(None) is None
    assert _(T.int.optional)('') is None
    assert _(T.str.optional)(None) == ''
    assert _(T.str.optional)('') == ''
    assert _(T.list(T.int).optional)(None) is None
    assert _(T.dict(key=T.int).optional)(None) is None

    with pytest.raises(Invalid):
        assert _(T.dict(key=T.int).optional)('')

    with pytest.raises(Invalid):
        assert _(T.int)(None)
    with pytest.raises(Invalid):
        assert _(T.str)(None)
    with pytest.raises(Invalid):
        assert _(T.dict(key=T.int))(None)
    with pytest.raises(Invalid):
        assert _(T.list(T.int))(None)


def test_default():
    assert _(T.int.default(0))(None) == 0
    assert _(T.str.default('x'))(None) == 'x'
    assert _(T.int.optional.default(0))(None) == 0
    assert _(T.str.optional.default('x'))(None) == 'x'


def test_invalid_to():
    assert _(T.int.invalid_to(1))('x') == 1
    assert _(T.int.default(1).invalid_to_default)('x') == 1
    assert _(T.int.optional.invalid_to_default)('x') is None
    assert _(T.date.optional.invalid_to_default)('x') == ''
    assert _(T.date.object.optional.invalid_to_default)('x') is None
    assert _(T.date.invalid_to('2019-01-01'))('x') == '2019-01-01'
    assert _(T.date.object.invalid_to('2019-01-01'))('x') == date(2019, 1, 1)


@pytest.mark.parametrize('schema', [
    T.int.invalid_to_default,
    T.int.invalid_to(0).invalid_to_default,
    T.int.invalid_to('x'),
])
def test_invalid_to_schema_error(schema):
    with pytest.raises(SchemaError):
        _(schema)


@pytest.mark.parametrize('schema,value,expect', [
    (T.int, 'x', 'x'),
    (T.dict(key=T.int), {'key': 'x'}, 'x'),
    (T.list(T.int), [1, 'x'], 'x'),
])
def test_exception_value(schema, value, expect):
    with pytest.raises(Invalid) as exinfo:
        _(schema)(value)
    assert exinfo.value.value == expect


@schema_error_position(
    (T.unknown, ''),
    (T.str.unknown, ''),
    (T.dict(key=T.list(T.dict(key=T.unknown))), 'key[].key'),
)
def test_schema_error_position():
    pass
