import json
import enum
import pytest
from validr import T, Schema, Compiler, SchemaError, modelclass

from .helper import skipif_dict_not_ordered

EXPECT = {
    '$self': "dict.optional.desc('a dict')",
    'key': [
        'list.unique',
        'int.min(0).max(9)'
    ],
    'tag': "str.desc('a tag')"
}


@skipif_dict_not_ordered()
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


def test_param_type():
    T.str.default(None)
    T.str.default("")
    T.int.default(0)
    T.bool.default(True)
    T.float.default(1.5)
    with pytest.raises(SchemaError):
        T.xxx.param([])
    with pytest.raises(SchemaError):
        T.xxx.param({})
    with pytest.raises(SchemaError):
        T.xxx.param(object)


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


def test_union_list():
    schema = T.union([
        T.str,
        T.list(T.str),
        T.dict(key1=T.str),
        T.dict(key1=T.str, key2=T.str),
    ]).optional
    assert schema.__schema__.copy() == schema.__schema__
    assert T(json.loads(str(schema))) == schema
    assert T(schema.__schema__.to_primitive()) == schema
    with pytest.raises(SchemaError):
        T.union(T.str, T.int)
    with pytest.raises(SchemaError):
        T.union([T.str, int])


def test_union_dict():
    schema = T.union(
        type1=T.dict(key1=T.str),
        type2=T.dict(key2=T.str, key3=T.list(T.int)),
    ).by('type').optional
    assert T(json.loads(str(schema))) == schema
    assert T(schema.__schema__.to_primitive()) == schema
    with pytest.raises(SchemaError):
        T.union(type1=T.dict, type2=dict)


def test_dynamic_dict():
    schema = T.dict(labels=T.list(T.str)).key(
        T.str.minlen(2)
    ).value(
        T.list(T.int)
    ).optional
    assert T(json.loads(str(schema))) == schema
    assert T(schema.__schema__.to_primitive()) == schema
    with pytest.raises(SchemaError):
        T.dict.key('abc')
    with pytest.raises(SchemaError):
        T.dict.value('abc')


def test_enum():
    schema = T.enum([123, 'xyz', True]).optional
    assert T(json.loads(str(schema))) == schema
    assert T(schema.__schema__.to_primitive()) == schema
    T.enum('A B C') == T.enum(['A', 'B', 'C'])
    with pytest.raises(SchemaError):
        T.enum([T.str])
    with pytest.raises(SchemaError):
        T.enum([object])


def test_enum_class():
    class ABC(enum.IntEnum):
        A = 1
        B = 2
    assert T.enum(ABC) == T.enum([1, 2])
    assert T.enum(enum.Enum('ABC', 'A,B')) == T.enum([1, 2])


def test_model():

    @modelclass
    class UserModel:
        name = T.str
        age = T.int.min(0)

    class ABC:
        value = 123

    T.model(UserModel).optional

    with pytest.raises(SchemaError):
        T.model(ABC)

    with pytest.raises(SchemaError):
        T.model(a=UserModel, b=UserModel)
