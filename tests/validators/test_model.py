from validr import T, modelclass

from . import case


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
