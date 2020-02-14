import pytest
from validr import T, SchemaError
from . import case, compiler


@case({
    T.union([T.str, T.list(T.str)]): [
        ('xxx', 'xxx'),
        (['xxx', 'yyy'], ['xxx', 'yyy']),
        ([], []),
        [None, '', 123],
    ],
    T.union([T.str, T.list(T.str)]).optional: [
        ('xxx', 'xxx'),
        (['xxx', 'yyy'], ['xxx', 'yyy']),
        ([], []),
        ('', ''),
        (None, ''),
        [123],
    ],
    T.union([T.str, T.list(T.str)]).default('ddd'): [
        ('xxx', 'xxx'),
        (['xxx', 'yyy'], ['xxx', 'yyy']),
        ([], []),
        ('', 'ddd'),
        (None, 'ddd'),
        [123],
    ],
    T.union([
        T.str,
        T.list(T.str),
        T.dict(key1=T.str, key2=T.str, key4=T.str),
        T.dict(key1=T.str, key2=T.str, key3=T.str),
        T.dict(key1=T.str, key2=T.str),
        T.dict(key1=T.str),
        T.dict,
    ]): [
        ('xxx', 'xxx'),
        (['xxx', 'yyy'], ['xxx', 'yyy']),
        ({}, {}),
        ({'xxx': 'vvv'}, {'xxx': 'vvv'}),
        ({'key1': 'v1', 'xxx': 'vvv'}, {'key1': 'v1'}),
        (
            {'key1': 'v1', 'key2': 'v2', 'xxx': 'vvv'},
            {'key1': 'v1', 'key2': 'v2'}
        ),
        (
            {'key1': 'v1', 'key2': 'v2', 'key3': 'v3', 'xxx': 'vvv'},
            {'key1': 'v1', 'key2': 'v2', 'key3': 'v3'}
        ),
        (
            {'key1': 'v1', 'key2': 'v2', 'key4': 'v4', 'xxx': 'vvv'},
            {'key1': 'v1', 'key2': 'v2', 'key4': 'v4'}
        ),
        (
            {'key1': 'v1', 'key2': 'v2', 'key3': 'v3', 'key4': 'v4', 'xxx': 'vvv'},
            {'key1': 'v1', 'key2': 'v2', 'key4': 'v4'}
        ),
    ]
})
def test_union_list():
    pass


@case({
    T.union(
        type1=T.dict(key=T.str),
        type2=T.dict(key=T.list(T.int)),
    ).by('type'): [
        ({'type': 'type1', 'key': 'xxx'}, {'type': 'type1', 'key': 'xxx'}),
        ({'type': 'type2', 'key': [1, 2, 3]}, {'type': 'type2', 'key': [1, 2, 3]}),
        [
            {'type': 'xxx', 'key': 'xxx'},
            {'key': 'xxx'},
            'xxx',
            None,
        ]
    ]
})
def test_union_dict():
    pass


def test_compile_union():
    with pytest.raises(SchemaError):
        compiler.compile(T.union)
    with pytest.raises(SchemaError):
        compiler.compile(T.union([T.str]).by('type'))
    with pytest.raises(SchemaError):
        compiler.compile(T.union(t1=T.dict(k1=T.str), t2=T.dict(k2=T.str)))
    with pytest.raises(SchemaError):
        compiler.compile(T.union(t1=T.dict(k1=T.str)).by(123))


def test_compile_union_list():
    with pytest.raises(SchemaError):
        compiler.compile(T.union([T.union([T.str])]))
    with pytest.raises(SchemaError):
        compiler.compile(T.union([T.str.optional]))
    with pytest.raises(SchemaError):
        compiler.compile(T.union([T.int, T.str]))
    with pytest.raises(SchemaError):
        compiler.compile(T.union([T.list(T.int), T.list(T.int)]))
    with pytest.raises(SchemaError):
        compiler.compile(T.union([T.dict(k=T.str), T.dict(k=T.int)]))
    with pytest.raises(SchemaError):
        compiler.compile(T.union([T.dict(k=T.str), T.dict(k=T.str, k2=T.int.optional)]))


def test_compile_union_dict():
    with pytest.raises(SchemaError):
        compiler.compile(T.union(k1=T.str).by('type'))
    with pytest.raises(SchemaError):
        compiler.compile(T.union(k1=T.dict.optional).by('type'))
