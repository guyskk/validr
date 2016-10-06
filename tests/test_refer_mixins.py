from collections import OrderedDict
from validr import SchemaError, Invalid, SchemaParser
import pytest

sp = SchemaParser()


class User:

    def __init__(self, userid):
        self.userid = userid


@pytest.mark.parametrize("schema", [
    {"items&unique": ["int(0,9)"]},
    {"user&optional": {}},
    {"user&optional": {}},
    {"user(1,3)": []},
    {"items&unique": ["int(0,9)"]},
    {"user&optional": ["int(0,9)"]},
])
def test_refer_invalid_key(schema):
    with pytest.raises(SchemaError):
        sp.parse(schema)


@pytest.mark.parametrize("schema", [
    {"userid": "int(0,9)"},  # missing validator or refer
    {"userid?": "comment"},  # invalid syntax
    {"userid@": "comment"},  # invalid syntax
])
def test_missing_refer_or_validator(schema):
    with pytest.raises(SchemaError):
        sp.parse(schema)


def test_shared_orderd():
    """shared should keep ordered"""
    shared = OrderedDict([
        ("user_id", "int"),
        ("user", {"user_id@user_id": "desc"}),
        ("group", {"user@user": "desc"}),
        ("team", {"group@group": "desc"}),
    ])
    for i in range(100):
        SchemaParser(shared=shared)


def test_shared_error_position():
    shared = {"name": [{"key?xxx": "value"}]}
    with pytest.raises(SchemaError) as exinfo:
        SchemaParser(shared=shared)
    assert exinfo.value.position == "name[].key"


def test_dict_self_optional():
    # 'optional' is treated as desc
    f = sp.parse({"$self": "optional"})
    with pytest.raises(Invalid):
        f(None)


@pytest.mark.parametrize("value,expect", [
    (User(0), {"userid": 0}),
    ({"userid": 1}, {"userid": 1})])
def test_refer_scalar(value, expect):
    sp = SchemaParser(shared={"userid": "int(0,9)"})
    f = sp.parse({"userid@userid": "UserID"})
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [
    (User(0), {"userid": 0}),
    ({"userid": 1}, {"userid": 1})])
def test_refer_dict(value, expect):
    sp = SchemaParser(shared={"user": {"userid?int(0,9)": "UserID"}})
    f = sp.parse({"group@user": "User"})
    value = {"group": value}
    expect = {"group": expect}
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [
    ([User(0), {"userid": 1}], [{"userid": 0}, {"userid": 1}])])
def test_refer_list(value, expect):
    sp = SchemaParser(shared={"user": {"userid?int(0,9)": "UserID"}})
    f = sp.parse(["@user"])
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [([0], [0]), ([1, "2"], [1, 2])])
def test_list_refer(value, expect):
    sp = SchemaParser(shared={"numbers": ["(1,3)&unique", "int(0,9)"]})
    f = sp.parse("@numbers")
    assert f(value) == expect


@pytest.mark.parametrize("value", [
    [],
    [-1],
    [1, 2, 3, 4],
    [1, 2, 2, 3]])
def test_list_refer_fail(value):
    sp = SchemaParser(shared={"numbers": ["(1,3)&unique", "int(0,9)"]})
    f = sp.parse("@numbers")
    with pytest.raises(Invalid):
        f(value)


@pytest.mark.parametrize("schema", [
    "@number@text",
    {"key@number@text": "desc"}
])
def test_multi_refer_error(schema):
    sp = SchemaParser(shared={"number": "int", "text": "str"})
    with pytest.raises(SchemaError):
        sp.parse(schema)


@pytest.mark.parametrize("schema,value,expect", [
    ({"user@user&optional": "desc"}, {"user": None}, {"user": None}),
    ({"user@user&optional": "desc"},
     {"user": {"userid": "123"}}, {"user": {"userid": 123}}),
    ("@user&optional", None, None),
    (["@user&optional"], [None, {"userid": "123"}], [None, {"userid": 123}]),
])
def test_optional_refer(schema, value, expect):
    sp = SchemaParser(shared={
        "user": {"userid?int": "userid"},
    })
    assert sp.parse(schema)(value) == expect


@pytest.mark.parametrize("schema", [
    {"$self": "desc", "$self&optional": "desc"},
    {"": "desc", "$self&optional": "desc"},
    {"": "desc", "&optional": "desc"},
    {"@user": "desc", "&optional": "desc"},
])
def test_multi_self_described_error(schema):
    sp = SchemaParser(shared={"user": {"userid?int": "desc"}})
    with pytest.raises(SchemaError):
        sp.parse(schema)


@pytest.mark.parametrize("schema,value,expect", [
    ({"$self@user1": "desc"}, {"userid": "123"}, {"userid": 123}),
    ({"$self@user1": "desc"}, User(123), {"userid": 123}),
    ({"$self@user1&optional": "desc"}, {"userid": "123"}, {"userid": 123}),
    ({"$self@user1&optional": "desc"}, None, None),
    ({"$self@user1@user2&optional": "desc"}, None, None),
    (
        {"$self@user1@user2&optional": "desc"},
        {"userid": "123", "name": "kk", "age": 0, "xxx": "abc"},
        {"userid": 123, "name": "kk", "age": 0}
    ),
    (
        {"$self@user2@user1": "desc"},
        {"userid": "123", "name": "kk", "age": 0, "xxx": "abc"},
        {"userid": 123, "name": "kk", "age": 0}
    ),
])
def test_mixins(schema, value, expect):
    sp = SchemaParser(shared={
        "user1": {"userid?int": "userid"},
        "user2": {"name?str": "name", "age?int": "age"},
    })
    assert sp.parse(schema)(value) == expect


def test_mixin_shared_not_found():
    sp = SchemaParser(shared={
        "user1": {"userid?int": "userid"}
    })
    with pytest.raises(SchemaError):
        sp.parse({"$self@user2@user1": "desc"})


def test_merge_non_dict_value_error():
    sp = SchemaParser(shared={"a": "int", "b": "str"})
    f = sp.parse({"key": {"$self@a@b": "invalid mixins"}})
    with pytest.raises(SchemaError) as exinfo:
        f({"key": "123"})
    assert exinfo.value.position == "key"


def test_merge_required():
    sp = SchemaParser(shared={"a": {"x?int": "x"}, "b": {"y?int": "y"}})
    f = sp.parse({"$self@a@b": "required"})
    assert f({"x": 1, "y": 2}) == {"x": 1, "y": 2}
    with pytest.raises(Invalid) as exinfo:
        f(None)
    assert "required" in exinfo.value.message
