import pytest
from validr import Invalid, Compiler, T

from .helper import schema_error_position

_ = Compiler().compile


def test_optional():
    assert _(T.int.optional)(None) is None
    assert _(T.str.optional)(None) == ''
    assert _(T.str.optional)('') == ''
    assert _(T.list(T.int).optional)(None) is None
    assert _(T.dict(key=T.int).optional)(None) is None

    with pytest.raises(Invalid):
        assert _(T.int.optional)('')
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


@schema_error_position(
    (T.unknown, ''),
    (T.str.unknown, ''),
    (T.dict(key=T.list(T.dict(key=T.unknown))), 'key[].key'),
)
def test_schema_error_position():
    pass
