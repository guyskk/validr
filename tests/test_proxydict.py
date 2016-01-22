#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

import collections
from validater import ProxyDict


class User(object):

    def __init__(self, name):
        self.name = name


def test_is_dict():
    jack = ProxyDict(User('jack'))
    assert isinstance(jack, dict)
    assert isinstance(jack, collections.Iterable)


def test_dict():
    jack, tom = User('jack'), User('tom')
    jack.friend = tom
    proxyjack = ProxyDict(jack, [User])

    assert 'name' in proxyjack
    assert proxyjack['name'] == 'jack'
    assert 'friend' in proxyjack
    assert 'name' in proxyjack.keys()
    assert ('name', 'jack') in proxyjack.items()

    proxytom = proxyjack['friend']
    assert 'name' in proxytom
    assert proxytom['name'] == 'tom'
    assert proxytom.get('friend') is None

    proxytom['friend'] = jack
    assert tom.friend == jack


def test_setdefault():
    jack = User("jack")
    proxyjack = ProxyDict(jack, [User])
    assert "nickname" not in proxyjack
    assert None == proxyjack.setdefault("nickname")
    assert "nickname" in proxyjack
    assert None == proxyjack.setdefault("nickname", "jack_nickname")
    assert None == proxyjack["nickname"]
    assert "jack_nick" == proxyjack.setdefault("nick", "jack_nick")
    assert "jack_nick" == proxyjack["nick"]


def test_attrs():
    jack = User("jack")
    proxyjack = ProxyDict(jack, [User])
    assert 'ProxyDict' in repr(proxyjack)
    assert 'ProxyDict' in str(proxyjack)
    assert list(proxyjack) == dir(jack)
    assert len(proxyjack) == len(dir(jack))
