import pytest
from validr import T, SchemaError, Invalid
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
    T.union([T.list(T.str)]).optional: [
        (['xxx', 'yyy'], ['xxx', 'yyy']),
        (None, None),
        ['xxx', '', 123],
    ],
    T.union([
        T.str,
        T.list(T.str),
        T.dict(key=T.str),
    ]): [
        ('xxx', 'xxx'),
        (['xxx', 'yyy'], ['xxx', 'yyy']),
        ({'key': 'vvv'}, {'key': 'vvv'}),
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
    ],
    T.union(
        type1=T.dict(key=T.str),
    ).by('type').optional: [
        ({'type': 'type1', 'key': 'xxx'}, {'type': 'type1', 'key': 'xxx'}),
        (None, None),
        [
            {'type': 'xxx', 'key': 'xxx'},
        ]
    ]
})
def test_union_dict():
    pass


def test_compile_union():
    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union)
    assert 'union schemas not provided' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union([T.str]).default('xxx'))
    assert 'default' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union([T.str]).by('type'))
    assert 'by' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union(t1=T.dict(k1=T.str), t2=T.dict(k2=T.str)))
    assert 'by' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union(t1=T.dict(k1=T.str)).by(123))
    assert 'by' in exinfo.value.message


def test_compile_union_list():
    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union([T.union([T.str])]))
    assert 'ambiguous' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union([T.str.optional]))
    assert 'optional' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union([T.str.default('xxx')]))
    assert 'default' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union([T.int, T.str]))
    assert 'ambiguous' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union([T.list(T.int), T.list(T.int)]))
    assert 'ambiguous' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union([T.dict(k1=T.str), T.dict(k2=T.int)]))
    assert 'ambiguous' in exinfo.value.message


def test_compile_union_dict():
    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union(k1=T.str).by('type'))
    assert 'dict' in exinfo.value.message

    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.union(k1=T.dict.optional).by('type'))
    assert 'optional' in exinfo.value.message


def test_union_list_error_position():
    f = compiler.compile(T.list(T.union([
        T.int,
        T.list(T.int),
        T.dict(k=T.int),
    ])))

    with pytest.raises(Invalid) as exinfo:
        f([123, 'xxx'])
    assert exinfo.value.position == '[1]'

    with pytest.raises(Invalid) as exinfo:
        f([123, [456, 'xxx']])
    assert exinfo.value.position == '[1][1]'

    with pytest.raises(Invalid) as exinfo:
        f([123, {'k': 'xxx'}])
    assert exinfo.value.position == '[1].k'


def test_union_dict_error_position():
    f = compiler.compile(T.union(
        t1=T.dict(k1=T.int),
        t2=T.dict(k2=T.list(T.int)),
    ).by('type'))

    with pytest.raises(Invalid) as exinfo:
        f({'k1': 123})
    assert exinfo.value.position == 'type'

    with pytest.raises(Invalid) as exinfo:
        f({'k1': 'xxx', 'type': 'txxx'})
    assert exinfo.value.position == 'type'

    with pytest.raises(Invalid) as exinfo:
        f({'k1': 'xxx', 'type': 't1'})
    assert exinfo.value.position == 'k1'

    with pytest.raises(Invalid) as exinfo:
        f({'k2': ['xxx'], 'type': 't2'})
    assert exinfo.value.position == 'k2[0]'
