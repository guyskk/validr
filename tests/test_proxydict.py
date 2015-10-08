# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import

import collections
from validater import ProxyDict


class My(object):

    """docstring for My"""
    mymy = "mymy"

    def __init__(self, my):
        self.my = my
        self._perivate = "perivate"

    def func(self):
        pass


class XX(object):

    """docstring for XX"""

    def __init__(self, xx):
        self.xx = xx


def test_is_dict():
    out = ProxyDict(My("my"))
    assert isinstance(out, dict)
    assert isinstance(out, collections.Iterable)


def test_dict():
    xx = XX("haha")
    my = My(xx)
    out = ProxyDict(my, [XX])

    assert "my" in out
    assert "xx" in out["my"]
    assert out["my"]["xx"] == "haha"
    assert "my" in out.keys()
    out.items()
    out.values()

    out["yy"] = "yyyy"

    assert "yy" in out
    assert out.proxy_obj.yy == "yyyy"
    assert out["yy"] == "yyyy"

    out["_zz"] = "zzzz"

    assert "_zz" in out
    assert out.proxy_obj._zz == "zzzz"
    assert out["_zz"] == "zzzz"
