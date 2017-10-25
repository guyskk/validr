import pytest
from validr import SchemaError, IsomorphSchema, T
from . import schema_error_position


def test_list():
    schema = IsomorphSchema([
        'list.unique.maxlen(10).desc("a list")',
        'int'
    ])
    assert schema == T.list(T.int).unique.maxlen(10).desc('a list')

    schema = IsomorphSchema(['int'])
    assert schema == T.list(T.int)

    with pytest.raises(SchemaError):
        IsomorphSchema([
            'list',
            'int',
            'str'
        ])


def test_dict():
    schema = IsomorphSchema({
        '$self': 'dict.optional.desc("a dict")',
        'key': 'str',
    })
    assert schema == T.dict(key=T.str).optional.desc('a dict')

    schema = IsomorphSchema({'key': 'str'})
    assert schema == T.dict(key=T.str)

    with pytest.raises(SchemaError):
        IsomorphSchema({
            '$self': ''
        })


@schema_error_position(
    (IsomorphSchema({'key': 'unknown'}), 'key'),
    (IsomorphSchema([{'key': 'unknown'}]), '[].key'),
    (IsomorphSchema({'key': [{'key': 'unknown'}]}), 'key[].key'),

)
def test_schema_error_position():
    pass

# (IsomorphSchema({'key': int}), 'key'),
# (IsomorphSchema({'key': '...'}), 'key'),
# (IsomorphSchema(['list', 'int', 'str']), ''),
