from validater import SchemaError, Invalid, SchemaParser
import pytest
import sys

sp = SchemaParser()


class User:

    def __init__(self, userid):
        self.userid = userid


scalar_schemas = {
    "int(0,9)": (
        [(0, 0), (9, 9), ("3", 3), (True, 1), (False, 0)],
        ["a", "-1", "10", "", None]),
    "int&default=5": (
        [(None, 5)],
        [""]),
    "int&optional": (
        [(None, None)],
        [""]),
    "int&default=5&optional": (
        [(None, 5)],
        [""]),
    "int&desc=\"a number\"": (
        [(sys.maxsize, sys.maxsize), (-sys.maxsize, -sys.maxsize)],
        [sys.maxsize + 1, -sys.maxsize - 1, float('INF'), float('NAN')])
}

scalar_params = []
scalar_params_fail = []
for schema, (success, fail) in scalar_schemas.items():
    for value, expect in success:
        scalar_params.append((schema, value, expect))
    for value in fail:
        scalar_params_fail.append((schema, value))


@pytest.mark.parametrize("schema,value,expect", scalar_params)
def test_scalar(schema, value, expect):
    f = sp.parse(schema)
    assert f(value) == expect


@pytest.mark.parametrize("schema,value", scalar_params_fail)
def test_scalar_fail(schema, value):
    f = sp.parse(schema)
    with pytest.raises(Invalid):
        print("value is: %s" % f(value))


def test_default_invalid():
    with pytest.raises(SchemaError):
        sp.parse("int(0,9)&default=10")


@pytest.mark.parametrize("value", [{"userid": 5}, User(5)])
def test_dict(value):
    expect = {"userid": 5}
    f = sp.parse({"userid?int(0,9)": "用户ID"})
    assert f(value) == expect


@pytest.mark.parametrize("value", [{"user": {"userid": 5}}, {"user": User(5)}])
def test_dict_inner(value):
    expect = {"user": {"userid": 5}}
    f = sp.parse({"user": {"userid?int(0,9)": "用户ID"}})
    assert f(value) == expect


def test_dict_optional():
    f = sp.parse({"$self&optional": "User"})
    assert f(None) is None
    assert f({"userid": 5}) == {}


def test_dict_inner_optional():
    f = sp.parse({"user": {"$self&optional": "User"}})
    assert f({"user": None}) == {"user": None}
    assert f({"user": {"userid": 5}}) == {"user": {}}


def test_list_length_0_error():
    with pytest.raises(SchemaError):
        sp.parse([])


def test_list_length_3_error():
    with pytest.raises(SchemaError):
        sp.parse(["&unique", "int(0,9)", "xxxx"])


@pytest.mark.parametrize("value,expect", [
    ([1], [1]),
    ([1, 2, "3"], [1, 2, 3])])
def test_list(value, expect):
    f = sp.parse(["(1,3)&unique", "int(0,9)"])
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [
    ([], []),
    ([1, 2, "2", 3], [1, 2, 2, 3])])
def test_list_length_1(value, expect):
    f = sp.parse(["int(0,9)"])
    assert f(value) == expect


@pytest.mark.parametrize("value", [None, [], [1, 2, "3", 4], [1, 2, 2]])
def test_list_fail(value):
    f = sp.parse(["(1,3)&unique", "int(0,9)"])
    with pytest.raises(Invalid):
        f(value)


@pytest.mark.parametrize("value", [
    [User(0), User(0)],
    [User(1), User(2), {"userid": 2}]])
def test_list_unique(value):
    f = sp.parse(["&unique", {"userid?int": "UserID"}])
    with pytest.raises(Invalid):
        f(value)


def test_list_optional():
    f = sp.parse(["&optional", "int"])
    assert f(None) is None
    assert f([]) == []


def test_list_dict():
    f = sp.parse([{"userid?int(0,9)": "UserID"}])
    assert f([User(0), {"userid": 1}]) == [{"userid": 0}, {"userid": 1}]


def test_dict_list():
    f = sp.parse({"group": ["&unique", "int"]})
    assert f({"group": [1, "2"]}) == {"group": [1, 2]}


@pytest.mark.parametrize("schema,expect", [
    ("int(0,9)&desc='number'", ""),
    ({"user?&optional": {}}, "user"),
    ({"user?&optional": []}, "user"),
    ({"userid@userid&optional": "UserID"}, "userid"),
    ({"user": {"userid": "int"}}, "user.userid"),
    ({"user": {"tags?&uniqie": ["int"]}}, "user.tags"),
    ({"user": {"tags": ["&uniqie", "int("]}}, "user.tags[]"),
    (["int("], "[]"),
    ([{"userid": "int"}], "[].userid"),
])
def test_schema_error_position(schema, expect):
    with pytest.raises(SchemaError) as exinfo:
        sp.parse(schema)
    assert exinfo.value.position == expect


@pytest.mark.parametrize("schema,expect", [
    ("int&required", ""),
    ({"userid": "int&required"}, "userid"),
    ({"friends": [{"userid": "int&required"}]}, "friends[].userid"),
])
def test_invalid_validater_params_error_position(schema, expect):
    with pytest.raises(SchemaError) as exinfo:
        sp.parse(schema)
    assert exinfo.value.position == expect


@pytest.mark.parametrize("value,expect", [
    (None, ""),
    ({"user": None}, "user"),
    ({"user": {"userid": "abc", "tags": [1]}}, "user.userid"),
    ({"user": {"userid": 1, "tags": []}}, "user.tags"),
    ({"user": {"userid": 1, "tags": [0, 0]}}, "user.tags[1]"),
])
def test_dict_invalid_position(value, expect):
    f = sp.parse({
        "user": {
            "userid?int": "UserID",
            "tags": ["(1,2)&unique", "int"]
        }
    })
    with pytest.raises(Invalid) as exinfo:
        f(value)
    assert exinfo.value.position == expect


@pytest.mark.parametrize("value,expect", [
    (None, ""),
    (0, ""),
    ([[User(0)], None], "[1]"),
    ([[User(0)], [User(0)]], "[1]"),
    ([[User(0), User(0)]], "[0][1]"),
    ([[User("a")]], "[0][0].userid"),
])
def test_list_invalid_position(value, expect):
    f = sp.parse(["&unique", ["&unique", {"userid?int": "UserID"}]])
    with pytest.raises(Invalid) as exinfo:
        f(value)
    assert exinfo.value.position == expect
