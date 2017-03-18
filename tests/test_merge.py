import pytest
from validr import Invalid, SchemaError, SchemaParser


@pytest.mark.parametrize("schema,value", [
    (
        {"$self@user_name": "User"},
        {"name": "kk"}
    ),
    (
        {"$self@user_name@user_age": "User"},
        {"name": "kk", "age": 1}
    ),
    (
        {"$self@user_name": "User", "userid?int": "ID"},
        {"name": "kk", "userid": 0}
    )
])
def test_basic(schema, value):
    sp = SchemaParser(shared={
        "user_name": {"name?str": "name"},
        "user_age": {"age?int": "age"},
    })
    f = sp.parse(schema)
    assert f(value) == value


@pytest.mark.parametrize("schema", [
    {"$self@user_name&optional": "User"},
    {"$self@user_name&optional": "User", "userid?int": "ID"},
    {"$self@user_name@user_age&optional": "User"},
])
def test_optional(schema):
    sp = SchemaParser(shared={
        "user_name": {"name?str": "name"},
        "user_age": {"age?int": "age"},
    })
    f = sp.parse(schema)
    assert f(None) is None


def test_shared_not_found():
    sp = SchemaParser(shared={"user": {"userid?int": "userid"}})
    with pytest.raises(SchemaError):
        sp.parse({"$self@unknown@user": "desc"})


def test_merge_non_dict_value_error():
    sp = SchemaParser(shared={
        "a": "int",
        "b": {"k?str": "v"}
    })
    with pytest.raises(SchemaError) as exinfo:
        sp.parse({"key": {"$self@a@b": "invalid merges"}})
    assert exinfo.value.position == "key"
    assert '@a' in exinfo.value.message


def test_required():
    sp = SchemaParser(shared={"a": {"x?int": "x"}, "b": {"y?int": "y"}})
    f = sp.parse({"$self@a@b": "required"})
    assert f({"x": 1, "y": 2}) == {"x": 1, "y": 2}
    with pytest.raises(Invalid) as exinfo:
        f(None)
    assert "required" in exinfo.value.message


@pytest.mark.parametrize("value,expect", [
    (None, ""),
    ({"name": "kk"}, "age"),
    ({"age": 1}, "name"),
    ({"name": "kk", "age": "xxx"}, "age"),
])
def test_error_position(value, expect):
    sp = SchemaParser(shared={
        "user_name": {"name?str": "name"},
        "user_age": {"age?int": "age"},
    })
    f = sp.parse({"$self@user_name@user_age": "User"})
    with pytest.raises(Invalid) as exinfo:
        f(value)
    assert exinfo.value.position == expect
