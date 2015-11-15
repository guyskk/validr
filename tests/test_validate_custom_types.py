# coding:utf-8
from __future__ import unicode_literals
from validater import validate


class User(object):
    """docstring for User"""

    def __init__(self, user_id, role, userinfo):
        self.user_id = user_id
        self.role = role
        self.userinfo = userinfo


class UserInfo(object):
    """docstring for UserInfo"""

    def __init__(self, name, age):
        self.name = name
        self.age = age

sche = {
    "user_id": {
        "required": True,
        "validate": "int"
    },
    "role": {
        "required": True,
        "validate": "unicode"
    },
    "userinfo": {
        "name": {
            "required": True,
            "validate": "unicode"
        },
        "age": {
            "required": True,
            "validate": "int"
        }
    }
}

expect = {
    "user_id": 1,
    "role": "admin",
    "userinfo": {
            "name": "kk",
            "age": 20
    }
}


def test_validate_base():

    info = UserInfo("kk", 20)
    user = User(1, "admin", info)
    err, val = validate(user, sche, proxy_types=[User, UserInfo])
    assert not err
    assert val == expect


def test_validate_dict():

    info = UserInfo("kk", 20)
    user = User(1, "admin", info)
    err, val = validate({"user": user}, {"user": sche}, proxy_types=[User, UserInfo])
    assert not err
    assert val["user"] == expect


def test_validate_list():
    info = UserInfo("kk", 20)
    user = User(1, "admin", info)
    userlist = [user] * 10
    err, val = validate(userlist, [sche], proxy_types=[User, UserInfo])
    assert not err
    assert len(val) == 10
    for u in val:
        assert u == expect
