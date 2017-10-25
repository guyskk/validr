import json
from validr import T, Schema

EXPECT = {
    '$self': "dict.optional.desc('a dict')",
    'key': [
        'list.unique',
        'int.min(0).max(9)'
    ],
    'tag': "str.desc('a tag')"
}


def test_str_and_to_primitive():
    schema = T.dict(
        key=T.list(T.int.min(0).max(9)).unique,
        tag=T.str.desc('a tag'),
    ).optional.desc('a dict')
    assert schema.to_primitive() == EXPECT
    assert json.loads(str(schema)) == EXPECT


def test_repr():
    schema = T.dict(
        key=T.list(T.int).unique,
    ).optional.desc('a dict')
    assert repr(schema) == "T.dict({'key'}).optional.desc('a dict')"
    schema = T.list(T.int.min(0)).unique
    assert repr(schema) == 'T.list(int).unique'
    schema = T.str.minlen(10).optional
    assert repr(schema) == 'T.str.minlen(10).optional'
    assert repr(Schema()) == 'T'
