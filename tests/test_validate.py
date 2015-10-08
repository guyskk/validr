# coding:utf-8
from __future__ import unicode_literals


from datetime import datetime
from validater import validate, add_validater, re_validater
from dateutil import parser
import re


def test_1():

    s1 = {
        "desc": "desc of the key",
        "required": True,
        "validate": "int",
        "default": "321",
    }
    obj1 = "sda"
    (error, value) = validate(obj1, s1)
    assert error
    assert value is None
    obj2 = "111"
    (error, value) = validate(obj2, s1)
    assert not error
    assert value == 111


def test_2():

    s2 = [{
        "desc": "desc of the key",
        "required": True,
        "validate": "int",
        "default": "321",
    }]
    obj2 = ["sda", 1, 2, 3]

    (error, value) = validate(obj2, s2)
    assert error[0][0] == "[0]"
    assert "desc of the key" in error[0][1]
    assert sorted(value) == sorted([None, 1, 2, 3])


def test_6():
    s6 = [{
        "key1": {
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
            "default": "321",
        }
    }]
    obj6 = [{
        "key1": "123"
    }, {
        "key": "123"
    }, {
        "key1": "asd"
    }, {
        "kkk": "1234"
    }]

    (error, value) = validate(obj6, s6)
    assert len(error) == 1
    assert error[0][0] == "[2].key1"
    assert sorted(value) == sorted([{"key1": 123}, {"key1": 321},
                                    {"key1": None}, {"key1": 321}, ])


def test_3():
    schema3 = {
        "key1": {
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
            "default": "321",
        },
        "key2": {
            "desc": "desc of the key",
            "required": True,
            "validate": "+int",
        },
        "key3": {
            "desc": "desc of the key",
            "required": True,
            "validate": "datetime",
            "default": "",
        }
    }
    obj3 = {
        "key1": "123",
        "key2": "haha",
        "key3": "2015-09-01 14:42:35"
    }

    (error, value) = validate(obj3, schema3)
    assert len(error) == 1
    assert error[0][0] == "key2"
    assert "desc of the key" in error[0][1]
    assert value == {
        "key1": 123,
        "key2": None,
        "key3": parser.parse("2015-09-01 14:42:35")
    }


def test_4():
    schema4 = {
        "key1": [{
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
            "default": "321",
        }]
    }
    obj4 = {
        "key1": ["123", "32", "asd"]
    }
    (error, value) = validate(obj4, schema4)
    assert len(error) == 1
    assert error[0][0] == "key1.[2]"
    assert "desc of the key" in error[0][1]
    assert sorted(value["key1"]) == sorted([123, 32, None])


def test_5():
    schema5 = {
        "key1": {
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
            "default": "321",
        },
        "key2": [{
            "desc": "desc of the key",
            "required": True,
            "validate": "int",
        }],
        "key3": {
            "key1": {
                "desc": "desc of the key",
                "required": True,
                "validate": "int",
            },
            "key2": [{
                "desc": "desc of the key",
                "required": True,
                "validate": "int",
            }],
            "key3": {
                "desc": "desc of the key",
                "required": True,
                "validate": "int",
            },
            "key4": {
                "desc": "desc of the key",
                "validate": "int",
            },
        }
    }
    obj5 = {
        "key1": "123",
        "key2": ["123", "32", "asd"],
        "key3": {
            "key1": "123",
            "key2": ["123", "32", "asd"],
        }
    }

    (error, value) = validate(obj5, schema5)
    assert len(error) == 3
    error = dict(error)
    assert "int" in error["key2.[2]"]
    assert "int" in error["key3.key2.[2]"]
    assert "required" in error["key3.key3"]
    assert value["key1"] == 123
    assert sorted(value["key2"]) == sorted([123, 32, None])
    assert value["key3"]["key1"] == 123
    assert sorted(value["key3"]["key2"]) == sorted([123, 32, None])
    assert value["key3"]["key3"] is None
    assert value["key3"]["key4"] is None


def test_addvalidater():

    re_http = re.compile(r'^(get|post|put|delete|head|options|trace|patch)$')
    add_validater("http_method", re_validater(re_http))

    s = {
        "key": [{
            "desc": "accept http method name",
            "required": True,
            "validate": "http_method"
        }]
    }
    obj = {"key": ["123", "get", "post", object()]}
    (error, value) = validate(obj, s)
    assert len(error) == 2
    error = dict(error)
    assert "key.[0]" in error
    assert "accept http method name" in error["key.[0]"]
    assert "key.[3]" in error
    assert "accept http method name" in error["key.[3]"]
    assert sorted(value["key"]) == sorted([None, "get", "post", None])


def test_default():
    s = {
        "key": {
            "desc": "datetime",
            "required": True,
            "validate": "datetime",
            "default": datetime.utcnow
        }
    }
    obj = {"key": None}
    (error, value) = validate(obj, s)
    assert not error
    assert isinstance(value["key"], datetime)


def test_validate_lamada():
    s = {
        "key": {
            "desc": "datetime",
            "required": True,
            "validate": lambda v: (True, v.isoformat()),
        },
        "key2": {
            "desc": "desc key2",
            "required": True,
            "validate": lambda v: (False, v.isoformat()),
        }
    }
    obj = {
        "key": parser.parse("2015-09-06 09:50:50"),
        "key2": parser.parse("2015-09-06 08:50:50")
    }
    (error, value) = validate(obj, s)
    assert "desc key2" in dict(error)["key2"]
    assert isinstance(value["key"], basestring)
    assert value["key2"] is None
