import pytest
from validr import Invalid, SchemaError, SchemaParser


@pytest.mark.parametrize("schema,value", [
    ("@userid", 1),
    (["@userid"], [0, 1]),
    ({"userid@userid": "UserID"}, {"userid": 1}),
])
def test_refer_scalar(schema, value):
    sp = SchemaParser(shared={"userid": "int"})
    f = sp.parse(schema)
    assert f(value) == value


@pytest.mark.parametrize("schema,value", [
    ("@user", {"userid": 1}),
    (["@user"], [{"userid": 0}, {"userid": 1}]),
    ({"group@user": "User"}, {"group": {"userid": 1}}),
])
def test_refer_dict(schema, value):
    sp = SchemaParser(shared={"user": {"userid?int": "UserID"}})
    f = sp.parse(schema)
    assert f(value) == value


@pytest.mark.parametrize("schema,value", [
    ("@tags", [1, 2, 3]),
    (["@tags"], [[1, 2], [1, 2, 3]]),
    ({"tags@tags": "Tags"}, {"tags": [1, 2, 3]}),
])
def test_refer_list(schema, value):
    sp = SchemaParser(shared={"tags": ["int"]})
    f = sp.parse(schema)
    assert f(value) == value


@pytest.mark.parametrize("value,expect", [
    (None, ""),
    ({"tags": []}, "user"),
    ({"tags": [], "user":{"userid": "x"}}, "user.userid"),
    ({"tags": ["x"], "user":{"userid": 0}}, "tags[0]"),
])
def test_error_position(value, expect):
    sp = SchemaParser(shared={
        "the_tags": ["int"],
        "user": {"userid?int": "UserID"}
    })
    f = sp.parse({
        "user@user": "User",
        "tags@the_tags": "Tags"
    })
    with pytest.raises(Invalid) as exinfo:
        f(value)
    assert exinfo.value.position == expect


@pytest.mark.parametrize("schema", [
    "@number@text",
    {"key@number@text": "desc"}
])
def test_multi_refer_error(schema):
    sp = SchemaParser(shared={"number": "int", "text": "str"})
    with pytest.raises(SchemaError):
        sp.parse(schema)


@pytest.mark.parametrize("schema,value", [
    ({"userid@userid&optional": "ID"}, {"userid": None}),
    ("@userid&optional", None),
    ("@userid&optional", 123),
])
def test_optional(schema, value):
    sp = SchemaParser(shared={"userid": "int"})
    f = sp.parse(schema)
    assert f(value) == value


def test_shared_not_found():
    sp = SchemaParser()
    with pytest.raises(SchemaError):
        sp.parse({"user@user": "User"})
