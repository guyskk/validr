from validr import T, modelclass

from . import case, compiler


@modelclass
class User:
    name = T.str
    age = T.int.min(0)


@case({
    T.model(User): [
        (dict(name='kk', age=12), User(name='kk', age=12)),
        (User(name='kk', age=12), User(name='kk', age=12)),
        [dict(name='kk', age=-1), "", 123]
    ],
    T.model(User).optional: [
        (None, None),
        ["", 123]
    ]
})
def test_model():
    pass


def test_union_list_model():
    schema = T.union([T.model(User), T.int])
    f = compiler.compile(schema)
    assert f(123) == 123
    data = dict(name='kk', age=12)
    assert f(data) == User(**data)
    assert f(User(**data)) == User(**data)


def test_union_dict_model():
    schema = T.union(user=T.model(User), dict=T.dict(label=T.str)).by('name')
    f = compiler.compile(schema)
    data = dict(name='user', age=12)
    assert f(data) == User(**data)
    assert f(User(**data)) == User(**data)
    data = dict(name='dict', label='test')
    assert f(data) == data
