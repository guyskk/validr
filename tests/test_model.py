import pytest
from validr import (
    T,
    modelclass,
    fields,
    asdict,
    Compiler,
    Invalid,
    ModelInvalid,
    ImmutableInstanceError,
)

from .helper import skipif_dict_not_ordered


@modelclass
class MyModel:

    id = T.int.min(0)

    def __post_init__(self):
        self.id_x2 = self.id * 2


class UserLabel(MyModel):
    value = T.str


class User(MyModel):

    id = T.int.min(100).default(100)
    name = T.str
    label = T.model(UserLabel).optional

    def __post_init__(self):
        self.id_x3 = self.id * 3


class LabelList(MyModel):
    labels = T.list(T.model(UserLabel))


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
    user = User(name="test", label=dict(id=1, value='cool'))
    assert user.id == 100
    assert user.name == "test"
    assert isinstance(user.label, UserLabel)
    assert user.label.value == 'cool'
    with pytest.raises(Invalid):
        user.id = -1


def test_model_list():
    label_list = LabelList(id=42, labels=[
        dict(id=1, value='cool'),
        UserLabel(id=2, value='nice'),
    ])
    assert len(label_list.labels) == 2
    assert label_list.labels[0].value == 'cool'
    assert label_list.labels[1].value == 'nice'


def test_post_init():
    user = User(id=100, name="test")
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
    assert repr(MyModel) == "MyModel<id>"
    assert repr(CustomModel) == "CustomModel<id>"
    assert repr(User) == "User<id, name, label>"
    assert repr(User.id) == "Field(name='id', schema=Schema<int.min(100).default(100)>)"
    assert repr(User.label) == "Field(name='label', schema=Schema<model(UserLabel).optional>)"
    user = User(id=100, name="test")
    assert repr(user) == "User(id=100, name='test', label=None)"


def test_schema():
    assert T(MyModel) == T.dict(id=T.int.min(0))
    assert T(User.__schema__.to_primitive()) == T.dict(
        id=T.int.min(100).default(100),
        name=T.str,
        label=T.dict(
            id=T.int.min(0),
            value=T.str,
        ).optional,
    )


def test_fields():
    assert fields(User) == {"id", "name", "label"}
    user = User(id=123, name="test")
    assert fields(user) == {"id", "name", "label"}
    assert fields(T.dict) == set()
    assert fields(T(User)) == {"id", "name", "label"}
    assert fields(T(User).__schema__) == {"id", "name", "label"}
    with pytest.raises(TypeError):
        fields(T.list(T.str))


def test_asdict():
    label = UserLabel(id=1, value="cool")
    user = User(id=123, name="test", label=label)
    assert asdict(user) == {"id": 123, "name": "test", "label": {"id": 1, "value": "cool"}}
    assert asdict(user, keys=["name"]) == {"name": "test"}


@skipif_dict_not_ordered()
def test_model_data():

    @modelclass
    class Model:
        pass

    class TaskTarget(Model):
        name = T.str
        image = T.str.optional

    class TaskStep(Model):
        command = T.str
        target = T.model(TaskTarget)

    class Task(Model):
        name = T.str
        steps = T.list(T.model(TaskStep))

    data = dict(
        name='deploy',
        steps=[
            dict(
                command='git clone',
                target=dict(
                    name='docker',
                    image='ubuntu:16.04',
                )
            ),
            dict(
                command='bash build.sh',
                target=dict(
                    name='docker',
                    image='ubuntu:16.04',
                )
            ),
        ]
    )
    task = Task(data)
    assert asdict(task) == data


def test_slice():
    expect = T.int.min(100).default(100)
    assert User["id"] == expect
    assert User["id", ] == T.dict(id=expect)
    assert T(User.id) == expect
    assert User["id", "name"] == T.dict(id=expect, name=T.str)
    assert User["label"] == T.model(UserLabel).optional
    with pytest.raises(KeyError):
        User["unknown"]
    with pytest.raises(KeyError):
        User["id", "unknown"]


def test_init():
    with pytest.raises(TypeError):
        User(1, 2)
    user = User({"id": 123, "name": "test", "unknown": "xxx"})
    assert user == User(id=123, name="test")
    u2 = User(user, id=456)
    assert u2.id == 456
    with pytest.raises(ModelInvalid) as exinfo:
        User(id=-1, name=object())
    assert len(exinfo.value.errors) == 2
    with pytest.raises(ModelInvalid) as exinfo:
        User(id=123, name="test", unknown=0)
    assert len(exinfo.value.errors) == 1
    assert 'undesired key' in str(exinfo.value)
