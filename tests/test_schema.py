#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

from validater import validate, parse, parse_snippet, Schema, SchemaError
import pytest
import copy


def test_parse_snippet():
    assert parse_snippet('int') == {
        'validater': 'int',
    }
    assert parse_snippet('int(1,10)') == {
        'validater': 'int',
        'args': (1, 10),
    }
    assert parse_snippet('int&required&default=5') == {
        'validater': 'int',
        'required': True,
        'default': 5
    }
    assert parse_snippet('int(1,10)&required&default=5') == {
        'validater': 'int',
        'args': (1, 10),
        'required': True,
        'default': 5
    }
    assert parse_snippet(('int(1,10)&required&default=5', 'desc')) == {
        'validater': 'int',
        'args': (1, 10),
        'required': True,
        'default': 5,
        'desc': 'desc'
    }


def test_parse():

    snippet = parse_snippet("int&required")
    sche = parse({'userid': "int&required"})
    assert sche['userid'].data == snippet

    sche = parse({'userid': ["int&required"]})
    assert sche['userid'][0].data == snippet

    sche = parse({'userid': {'userid': "int&required"}})
    assert sche['userid']['userid'].data == snippet

    sche = parse({'userid': [{'userid': "int&required"}]})
    assert sche['userid'][0]['userid'].data == snippet

    sche = parse({'email': ("email&required", "邮箱地址")})
    assert sche['email'].data == parse_snippet(("email&required", "邮箱地址"))

    sche = parse([{'userid': "int&required"}])
    assert sche[0]['userid'].data == snippet

    sche = parse("int&required")
    assert sche.data == snippet

    sche = parse(["int&required"])
    assert sche[0].data == snippet

    sche = parse([[["int&required"]]])
    assert sche[0][0][0].data == snippet

    sche = parse({'validater': 'int'})
    assert sche.data == {'validater': 'int'}

    sche = parse([{'validater': 'int'}])
    assert sche[0].data == {'validater': 'int'}

    sche = parse({'userid': {'validater': 'int'}})
    assert sche['userid'].data == {'validater': 'int'}


def test_parse_error():
    with pytest.raises(SchemaError):
        parse({'vali': 'int', 'required': True})
    with pytest.raises(SchemaError):
        parse("&required")
    with pytest.raises(SchemaError):
        parse("int&")
    with pytest.raises(SchemaError):
        parse("_unknown_validater")
    with pytest.raises(SchemaError):
        parse("int(abc)")
    with pytest.raises(SchemaError):
        parse("int&default=abc")
    with pytest.raises(SchemaError):
        parse("int&required=true")
    # note: sche is a tuple
    sche = {"userid": "int&required=true"},
    with pytest.raises(SchemaError):
        parse(sche)


def test_schema_will_not_modified():
    sche = {'data': ("int&required", "input a number")}
    origin = copy.deepcopy(sche)
    parsed = parse(sche)
    assert sche == origin
    assert parsed != origin

    sche = [("int&required", "input a number")]
    origin = copy.deepcopy(sche)
    parsed = parse(sche)
    assert sche == origin
    assert parsed != origin


def test_schema():
    data = {
        'validater': 'int',
        'args': (0, 5),
        'required': True,
        'default': 0,
        'desc': 'desc',
        'somekey': 'somevalue'
    }
    sche = Schema(data)
    assert sche.validater('123') == (True, 123)
    assert sche.required
    assert sche.default == 0
    assert sche.args == (0, 5)
    assert sche.kwargs == {'somekey': 'somevalue'}
    assert 'desc' in sche.error
    assert 'int' in sche.error
    # test eq and ne
    assert Schema(data) == Schema(data)
    assert not (Schema(data) != Schema(data))
    assert Schema(data) != object()


def test_reuse_schema_snippet():
    snippet = {"name": "str"}
    schema = {
        "user1": snippet,
        "user2": snippet,
    }
    sche = parse(schema)
    assert sche['user1']['name'] == parse("str")
    assert sche['user2']['name'] == parse("str")
    # parse a parsed schema shouldn't cause exception
    assert parse(parse(schema)) == parse(schema)


def test_validate_single_schema():
    sche = parse('int&required')
    err, val = validate('123', sche)
    assert not err
    assert val == 123
    err, val = validate(None, sche)
    assert err and 'required' in dict(err)['']
    assert val is None
    err, val = validate('abc', sche)
    assert err and 'int' in dict(err)['']
    assert val is None


def test_validate_simple_schema():
    sche = parse({'userid': 'int&required'})
    err, val = validate({'userid': '123'}, sche)
    assert not err
    assert val['userid'] == 123

    err, val = validate({'userid': None}, sche)
    assert err and 'required' in dict(err)['userid']
    assert val == {'userid': None}

    err, val = validate({}, sche)
    assert err and 'required' in dict(err)['userid']
    assert val == {'userid': None}

    err, val = validate(None, sche)
    assert err and 'must be dict' in dict(err)['']
    assert val == {}


def test_validate_deep_schema():
    sche = parse({"user": {'userid': 'int&required'}})
    err, val = validate({"user": {"userid": "123"}}, sche)
    assert not err
    assert val == {"user": {"userid": 123}}

    err, val = validate({"user": {"userid": None}}, sche)
    assert err and "required" in dict(err)["user.userid"]
    assert val == {"user": {"userid": None}}


def test_validate_simple_schema_has_default_value():
    sche = parse({'userid': 'int&required&default=0'})
    err, val = validate({'userid': None}, sche)
    assert not err
    assert val == {'userid': 0}
    err, val = validate({}, sche)
    assert not err
    assert val == {'userid': 0}

    sche = parse({'userid': 'int&default=0'})
    err, val = validate({'userid': None}, sche)
    assert not err
    assert val == {'userid': 0}
    err, val = validate({}, sche)
    assert not err
    assert val == {'userid': 0}

    sche = parse({'userid': 'int&default=None'})
    err, val = validate({'userid': None}, sche)
    assert not err
    assert val == {'userid': None}
    err, val = validate({}, sche)
    assert not err
    assert val == {'userid': None}


def test_validate_schema_callable_default():
    import random
    num = random.randint(0, 1)
    sche = parse({'validater': 'int', 'args': (0, 1), 'default': lambda: num})
    err, val = validate(None, sche)
    assert not err
    assert val == num


def test_validate_list_schema():
    sche = parse({'userid': ['int&required']})
    err, val = validate({'userid': []}, sche)
    assert not err
    assert val == {'userid': []}

    err, val = validate({'userid': ['123', '456']}, sche)
    assert not err
    assert val == {'userid': [123, 456]}

    err, val = validate({'userid': ['x123', 'x456']}, sche)
    assert err and set(['userid[0]', 'userid[1]']) == set(dict(err))
    assert val == {'userid': [None, None]}

    err, val = validate({}, sche)
    assert err and 'must be list' in dict(err)['userid']
    assert val == {'userid': []}

    err, val = validate({'userid': '123'}, sche)
    assert err and 'must be list' in dict(err)['userid']
    assert val == {'userid': []}


def test_validate_deep_list_schema_error():
    sche = parse([{'nums': ['int']}])
    err, val = validate([{'nums': ['x123', 'x456']}, {'nums': 'x'}, 'x'], sche)
    expect = set(['[0].nums[0]', '[0].nums[1]', '[1].nums', '[2]'])
    assert expect == set(dict(err))


def test_validate_custom_types():
    class User(object):

        def __init__(self, userid):
            self.userid = userid

    sche = parse({
        'userid': "int&required",
        'friends': [{'userid': "int&required"}]})
    jack, f1, f2 = User(0), User(1), User(2)
    jack.friends = [f1, f2]
    err, val = validate(jack, sche, proxy_types=[User])
    assert not err
    assert val == {'userid': 0,
                   'friends': [{'userid': 1}, {'userid': 2}]}


def test_validate_empty_value():
    # empty value is not always None, depends on validater
    # string type's empty value is ""
    err, val = validate(None, parse('str'))
    assert not err
    assert val == str("")

    err, val = validate(None, parse('unicode'))
    assert not err
    assert val == ""

    err, val = validate(None, parse('url'))
    assert not err
    assert val == ""
