import json
from validr import T, Schema, Compiler

EXPECT = {
    '$self': "dict.optional.desc('a dict')",
    'key': [
        'list.unique',
        'int.min(0).max(9)'
    ],
    'tag': "str.desc('a tag')"
}


def test_str_copy_and_to_primitive():
    schema = T.dict(
        key=T.list(T.int.min(0).max(9)).unique.optional(False),
        tag=T.str.desc('a tag'),
    ).optional.desc('a dict').__schema__
    assert schema.to_primitive() == EXPECT
    assert json.loads(str(schema)) == EXPECT
    copy = schema.copy()
    assert copy.to_primitive() == EXPECT
    # verify copy is deep copy
    schema.items['key'].items = T.int
    assert copy.to_primitive() == EXPECT


def test_repr():
    schema = T.dict(
        key=T.list(T.int).unique,
    ).optional.desc('a dict')
    assert repr(schema) == "T.dict({key}).optional.desc('a dict')"
    schema = T.list(T.int.min(0)).unique
    assert repr(schema) == 'T.list(int).unique'
    schema = T.str.minlen(10).optional(False)
    assert repr(schema) == 'T.str.minlen(10)'
    assert repr(Schema()) == 'Schema<>'


def test_compiled_items():
    compiler = Compiler()
    value = compiler.compile(T.int.min(0))
    assert repr(T.dict(key=value)) == 'T.dict({key})'
    assert repr(T.list(value)) == 'T.list(int)'


def test_load_schema():
    compiler = Compiler()
    schema = T.list(T.int.min(0))
    assert T(schema) == schema
    assert T(compiler.compile(schema)) == schema
    assert T(['int.min(0)']) == schema


def test_slice():
    schema = T.dict(
        id=T.int,
        age=T.int.min(0),
        name=T.str,
    ).optional
    assert schema['id'] == T.dict(id=T.int).optional
    assert schema['age', 'name'] == T.dict(
        age=T.int.min(0),
        name=T.str,
    ).optional
