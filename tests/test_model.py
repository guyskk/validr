import pytest
from validr import (
    T, modelclass, fields, asdict, Compiler,
    Invalid, ImmutableInstanceError,
)

from .helper import skipif_dict_not_ordered


@modelclass
class MyModel:

    id = T.int.min(0)

    def __post_init__(self):
        self.id_x2 = self.id * 2


class User(MyModel):

    id = T.int.min(100).default(100)
    name = T.str

    def __post_init__(self):
        self.id_x3 = self.id * 3


class CustomModel(MyModel):

    def __eq__(self, other):
        return id(self) == id(other)

    def get_id(self):
        return self.id


@modelclass(compiler=Compiler(), immutable=True)
class ImmutableModel:
    id = T.int.min(0)

    def __init__(self, id=None):
        self.id = id


def test_model():
    with pytest.raises(Invalid):
        User(name='test', xxx=123)
    user = User(name='test')
    assert user.id == 100
    assert user.name == 'test'
    with pytest.raises(Invalid):
        user.id = -1


def test_post_init():
    user = User(id=100, name='test')
    assert user.id == 100
    assert user.id_x2 == 200
    assert user.id_x3 == 300


def test_immutable():
    m = ImmutableModel(id=1)
    assert m.id == 1
    with pytest.raises(ImmutableInstanceError):
        m.id = 2
    with pytest.raises(ImmutableInstanceError):
        del m.id


def test_custom_method():
    m1 = MyModel(id=1)
    m2 = MyModel(id=1)
    assert m1 == m2
    x1 = CustomModel(id=1)
    x2 = CustomModel(id=1)
    assert x1.get_id() == x2.get_id()
    assert x1 != x2


@skipif_dict_not_ordered()
def test_repr():
    assert repr(MyModel) == 'MyModel<id>'
    assert repr(CustomModel) == 'CustomModel<id>'
    assert repr(User) == 'User<id, name>'
    user = User(id=100, name='test')
    assert repr(user) == "User(id=100, name='test')"


def test_schema():
    assert T(MyModel) == T.dict(
        id=T.int.min(0),
    )
    assert T(User) == T.dict(
        id=T.int.min(100).default(100),
        name=T.str,
    )


def test_fields():
    assert fields(User) == {'id', 'name'}
    user = User(id=123, name='test')
    assert fields(user) == {'id', 'name'}


def test_asdict():
    user = User(id=123, name='test')
    assert asdict(user) == {'id': 123, 'name': 'test'}
    assert asdict(user, keys=['name']) == {'name': 'test'}


def test_slice():
    assert User['id'] == T.dict(id=T.int.min(100).default(100))
    assert User['id', 'name'] == T.dict(
        id=T.int.min(100).default(100),
        name=T.str
    )


def test_init():
    with pytest.raises(TypeError):
        User({'name': 'text'})
    with pytest.raises(TypeError):
        User(1, 2)
    user = User(id=123, name='test')
    u2 = User(user, id=456)
    assert u2.id == 456
    with pytest.raises(Invalid):
        User(id=123, name='test', unknown=0)
