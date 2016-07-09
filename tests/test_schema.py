from validater import SchemaError, Invalid, SchemaParser
from validater.schema import ValidaterString
import pytest
import sys

sp = SchemaParser()

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


class User:

    def __init__(self, userid):
        self.userid = userid


def test_dict_pre_described_error():
    # validater string should preposition
    with pytest.raises(SchemaError):
        sp.parse({"userid": "int(0,9)"})


def test_dict_self_optional_error():
    # 'optional' is treated as desc
    f = sp.parse({"$self": "optional"})
    with pytest.raises(Invalid):
        f(None)


def test_dict_preposition_optional_error():
    # should self-described
    with pytest.raises(SchemaError):
        sp.parse({"user?&optional": {"userid?int(0,9)": "UserID"}})


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
