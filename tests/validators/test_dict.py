import pytest
from validr import Compiler, T, Invalid, SchemaError

from ..helper import expect_position
from . import case


class User:

    def __init__(self, userid):
        self.userid = userid


@case({
    T.dict(userid=T.int): [
        ({'userid': 1}, {'userid': 1}),
        (User(1), {'userid': 1}),
        ({'userid': 1, 'extra': 'xxx'}, {'userid': 1}),
    ],
    T.dict(userid=T.int).optional: {
        'valid': [
            None,
        ],
        'invalid': [
            {},
            {'extra': 1}
        ]
    },
    T.dict: {
        'valid': [
            {},
            {'key': 'value'},
        ],
        'invalid': [
            None,
            123,
        ]
    }
})
def test_dict():
    pass


compiler = Compiler()


@expect_position('key[0].key')
def test_dict_error_position():
    validate = compiler.compile(T.dict(key=T.list(T.dict(key=T.int))))
    validate({
        'key': [
            {'key': 'x'}
        ]
    })


@case({
    T.dict(userid=T.int).key(T.str.minlen(4)).value(T.int): [
        ({'userid': 1}, {'userid': 1}),
        ({'userid': 1, 'extra': 123}, {'userid': 1, 'extra': 123}),
        [
            User(1),
            {'userid': 1, 'xx': 123},
            {'userid': 1, 'extra': 'xx'},
            {'userid': 1, 123: 123},
        ]
    ],
    T.dict(userid=T.int).key(T.str.minlen(4)): [
        ({'userid': 1, 'extra': 123}, {'userid': 1, 'extra': 123}),
        ({'userid': 1, 'extra': 'abc'}, {'userid': 1, 'extra': 'abc'}),
    ],
    T.dict(userid=T.int).value(T.int): [
        ({'userid': 1, 'yy': 123}, {'userid': 1, 'yy': 123}),
    ],
})
def test_dynamic_dict():
    pass


def test_dynamic_dict_error():
    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.dict.key(T.int.default('xxx')))
    assert exinfo.value.position == '$self_key'

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.dict.value(T.int.default('xxx')))
    assert exinfo.value.position == '$self_value'

    f = compiler.compile(T.dict.key(T.str.minlen(4)).value(T.int))

    with pytest.raises(Invalid) as exinfo:
        f({'xx': 123})
    assert exinfo.value.position == '$self_key'
    assert exinfo.value.value == 'xx'

    with pytest.raises(Invalid) as exinfo:
        f({'yyyy': 'xx'})
    assert exinfo.value.position == 'yyyy'
    assert exinfo.value.value == 'xx'


@pytest.mark.parametrize('schema', [
    T.dict.minlen(2).maxlen(3),
    T.dict.key(T.str).value(T.int).minlen(2).maxlen(3),
])
def test_dict_length(schema):
    f = compiler.compile(schema)
    assert f({'xxx': 123, 'yyy': 123})
    assert f({'xxx': 123, 'yyy': 123, 'zzz': 123})
    with pytest.raises(Invalid) as exinfo:
        f({'xxx': 123})
    assert 'must >=' in exinfo.value.message
    with pytest.raises(Invalid) as exinfo:
        assert f({'xxx': 123, 'yyy': 123, 'zzz': 123, 'kkk': 123})
    assert 'must <=' in exinfo.value.message
