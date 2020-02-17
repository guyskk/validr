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
