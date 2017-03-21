from collections import OrderedDict

import pytest
from validr import Invalid, SchemaError, SchemaParser

sp = SchemaParser()


class User:

    def __init__(self, userid):
        self.userid = userid


@pytest.mark.parametrize('value', [
    {'userid': 5},
    OrderedDict([('userid', 5)]),
    User(5),
])
def test_basic(value):
    f = sp.parse({'userid?int': 'UserID'})
    assert f(value) == {'userid': 5}


def test_required():
    f = sp.parse({'userid?int': 'UserID'})
    with pytest.raises(Invalid):
        f(None)


def test_optional():
    f = sp.parse({'$self&optional': 'User'})
    assert f(None) is None
    assert f({'userid': 5}) == {}


@pytest.mark.parametrize('value', [
    {'user': {'userid': 5}},
    {'user': User(5)}
])
def test_dict_dict(value):
    expect = {'user': {'userid': 5}}
    f = sp.parse({'user': {'userid?int': '用户ID'}})
    assert f(value) == expect


def test_list_dict():
    f = sp.parse([{'userid?int': 'UserID'}])
    assert f([User(0), {'userid': 1}]) == [{'userid': 0}, {'userid': 1}]


def test_dict_list():
    f = sp.parse({'group': ['int']})
    assert f({'group': [1, '2']}) == {'group': [1, 2]}


def test_multi_self():
    schema = {
        '$self': 'User',
        '$self&optional': 'User'
    }
    with pytest.raises(SchemaError):
        sp.parse(schema)


@pytest.mark.parametrize('schema', [
    {'user&optional': {'userid?int': 'ID'}},
    {'group&optional': ['int']},
    {'user@user': {'userid?int': 'ID'}},
])
def test_invalid_key(schema):
    with pytest.raises(SchemaError):
        sp.parse(schema)


@pytest.mark.parametrize('schema', [
    {'userid': 'ID'},
    {'user': 'User'},
])
def test_missing_validator_or_refer(schema):
    with pytest.raises(SchemaError):
        sp.parse(schema)
