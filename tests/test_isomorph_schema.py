import pytest
from validr import SchemaError, Schema, T

from .helper import schema_error_position

isomorph_schema = Schema.parse_isomorph_schema


def test_list():
    schema = isomorph_schema([
        'list.unique.maxlen(10).desc("a list")',
        'int'
    ])
    assert schema == T.list(T.int).unique.maxlen(10).desc('a list')

    schema = isomorph_schema(['int'])
    assert schema == T.list(T.int)

    with pytest.raises(SchemaError):
        isomorph_schema([
            'list',
            'int',
            'str'
        ])


def test_invalid_list():
    with pytest.raises(SchemaError):
        isomorph_schema([])
    with pytest.raises(SchemaError):
        isomorph_schema(['unknown', 1, 2, 3])


def test_dict():
    schema = isomorph_schema({
        '$self': 'dict.optional.desc("a dict")',
        'key': 'str',
    })
    assert schema == T.dict(key=T.str).optional.desc('a dict')

    schema = isomorph_schema({'key': 'str'})
    assert schema == T.dict(key=T.str)

    with pytest.raises(SchemaError):
        isomorph_schema({'$self': ''})


@schema_error_position(
    (isomorph_schema({'key': 'unknown'}), 'key'),
    (isomorph_schema([{'key': 'unknown'}]), '[].key'),
    (isomorph_schema({'key': [{'key': 'unknown'}]}), 'key[].key'),
)
def test_schema_error_position():
    pass
