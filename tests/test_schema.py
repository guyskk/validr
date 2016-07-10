from validater import SchemaError, Invalid, SchemaParser
from validater.schema import ValidaterString
import pytest
import sys

sp = SchemaParser()


class User:

    def __init__(self, userid):
        self.userid = userid


validater_string = {
    "int": {"name": "int"},
    "int()": {"name": "int"},
    "int(0)": {"name": "int", "args": tuple([0])},
    "int(0,10)": {"name": "int", "args": tuple([0, 10])},
    "int(0, 10)": {"name": "int", "args": tuple([0, 10])},
    "int&default=5": {"name": "int", "kwargs": {"default": 5}},
    "int&optional": {"name": "int", "kwargs": {"optional": True}},
    "int&desc=\"a number\"": {"name": "int", "kwargs": {"desc": "a number"}},
    "int(0,10)&optional&default=5&desc=\"a number\"": {
        "name": "int",
        "args": tuple([0, 10]),
        "kwargs": {"default": 5, "optional": True, "desc": "a number"}
    },
    "()": {},
    "(0)": {"args": tuple([0])},
    "(0,10)": {"args": tuple([0, 10])},
    "&optional": {"kwargs": {"optional": True}},
    "&default=5&optional": {"kwargs": {"default": 5, "optional": True}},
    "(0,10)&minlen=1": {"args": tuple([0, 10]), "kwargs": {"minlen": 1}},
    "key?int(0,10)&optional": {
        "key": "key",
        "name": "int",
        "args": tuple([0, 10]),
        "kwargs": {"optional": True}
    },
    "key@shared": {"key": "key", "is_refer": True, "name": "shared"},
    "$self@shared": {"key": "$self", "is_refer": True, "name": "shared"},
    "@shared": {"is_refer": True, "name": "shared"},
    "": {},
}

validater_string_fail = [
    "int(0,10",
    "int(0 10)"
    "int&default=abc",
    "int&desc='a number'",
    "(0,10",
    "@user(0,9)",
    "@user&optional",
    "@user(0,9)",
    "key@user(0,9)&optional",
    "key@user&optional",
]
default_vs = {
    "key": None,
    "is_refer": False,
    "name": "",
    "args": tuple(),
    "kwargs": {}
}


@pytest.mark.parametrize("string, expect", validater_string.items())
def test_validater_string(string, expect):
    vs = ValidaterString(string)
    for k in default_vs:
        if k in expect:
            assert getattr(vs, k) == expect[k]
        else:
            assert getattr(vs, k) == default_vs[k]


@pytest.mark.parametrize("string", validater_string_fail)
def test_validater_string_fail(string):
    with pytest.raises(SchemaError):
        ValidaterString(string)

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


@pytest.mark.parametrize("schema", [{"userid": "int(0,9)"}])
def test_dict_pre_described_error(schema):
    # should be pre-described
    with pytest.raises(SchemaError):
        sp.parse(schema)


@pytest.mark.parametrize("schema", [
    {"user&optional": {}},
    {"user?&optional": {}},
    {"user(1,3)": []},
])
def test_dict_self_described_error(schema):
    # should be self-described
    with pytest.raises(SchemaError):
        sp.parse(schema)


def test_dict_self_optional_error():
    # 'optional' is treated as desc
    f = sp.parse({"$self": "optional"})
    with pytest.raises(Invalid):
        f(None)


def test_list_preposition_optional_error():
    # should be self-described
    with pytest.raises(SchemaError):
        sp.parse({"user?&optional": ["int(0,9)"]})


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
    f = sp.parse({"$self?&optional": "User"})
    assert f(None) is None
    assert f({"userid": 5}) == {}


def test_dict_inner_optional():
    f = sp.parse({"user": {"$self?&optional": "User"}})
    assert f({"user": None}) == {"user": None}
    assert f({"user": {"userid": 5}}) == {"user": {}}


def test_list_length_0_error():
    with pytest.raises(SchemaError):
        sp.parse([])


def test_list_length_3_error():
    with pytest.raises(SchemaError):
        sp.parse(["&unique", "int(0,9)", "xxxx"])


def test_list_pre_described_error():
    with pytest.raises(SchemaError):
        sp.parse({"items?&unique": ["int(0,9)"]})


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


@pytest.mark.parametrize("value,expect", [
    (User(0), {"userid": 0}),
    ({"userid": 1}, {"userid": 1})])
def test_shared_scalar(value, expect):
    sp = SchemaParser(shared={"userid": "int(0,9)"})
    f = sp.parse({"userid@userid": "UserID"})
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [
    (User(0), {"userid": 0}),
    ({"userid": 1}, {"userid": 1})])
def test_shared_dict(value, expect):
    sp = SchemaParser(shared={"user": {"userid?int(0,9)": "UserID"}})
    f = sp.parse({"group@user": "User"})
    value = {"group": value}
    expect = {"group": expect}
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [
    (User(0), {"userid": 0, "age": 18}),
    ({"userid": 1, "age": 20}, {"userid": 1, "age": 20})
])
def test_shared_dict_addition(value, expect):
    sp = SchemaParser(shared={"user": {"userid?int(0,9)": "UserID"}})
    f = sp.parse({"group": {
        "$self@user": "User",
        "age?int(0,100)&default=18": "Age"
    }})
    value = {"group": value}
    expect = {"group": expect}
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [
    ({"userid": 1, "age": 20}, {"userid": 1, "age": 20})
])
def test_shared_2(value, expect):
    shared = {
        "userid": "int(0,9)",
        "age": "int(10,99)"
    }
    sp = SchemaParser(shared=shared)
    f = sp.parse({
        "userid@userid": "UserID",
        "age@age": "Age"
    })
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [
    ([User(0), {"userid": 1}], [{"userid": 0}, {"userid": 1}])])
def test_shared_list(value, expect):
    sp = SchemaParser(shared={"user": {"userid?int(0,9)": "UserID"}})
    f = sp.parse(["@user"])
    assert f(value) == expect


@pytest.mark.parametrize("value,expect", [([0], [0]), ([1, "2"], [1, 2])])
def test_list_shared(value, expect):
    sp = SchemaParser(shared={"numbers": ["(1,3)&unique", "int(0,9)"]})
    f = sp.parse("@numbers")
    assert f(value) == expect


@pytest.mark.parametrize("value", [
    [],
    [-1],
    [1, 2, 3, 4],
    [1, 2, 2, 3]])
def test_list_shared_fail(value):
    sp = SchemaParser(shared={"numbers": ["(1,3)&unique", "int(0,9)"]})
    f = sp.parse("@numbers")
    with pytest.raises(Invalid):
        f(value)


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
    ({}, ""),
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


def test_exception_message():
    assert Invalid("invalid").message == "invalid"
    assert Invalid().message is None


def test_exception_position():
    ex = Invalid("invalid").mark_index(0).mark_key("key")
    assert ex.position == "key[0]"
    assert ex.position in str(ex)
    assert ex.message in str(ex)
    ex = Invalid("invalid").mark_key("key").mark_index(0)
    assert ex.position == "[0].key"
    assert ex.position in str(ex)
    assert ex.message in str(ex)
