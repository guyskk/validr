# coding:utf-8

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
    assert out["my"] == {"xx": "haha"}
    assert out["my"]["xx"] == "haha"
    assert list(out.items()) == [("my", {"xx": "haha"})]
    assert list(out.keys()) == ["my"]
    assert list(out.values()) == [{"xx": "haha"}]

    out["yy"] = "yyyy"

    assert "yy" in out
    assert out.obj.yy == "yyyy"
    assert out["yy"] == "yyyy"
    assert sorted(list(out.items())) == sorted([("my", {"xx": "haha"}), ("yy", "yyyy")])
    assert sorted(list(out.keys())) == sorted(["my", "yy"])
    assert sorted(list(out.values())) == sorted([{"xx": "haha"}, "yyyy"])

    out["_zz"] = "zzzz"

    assert "_zz" not in out
    assert out.obj._zz == "zzzz"
    assert out["_zz"] == "zzzz"
    assert sorted(list(out.items())) == sorted([("my", {"xx": "haha"}), ("yy", "yyyy")])
    assert sorted(list(out.keys())) == sorted(["my", "yy"])
    assert sorted(list(out.values())) == sorted([{"xx": "haha"}, "yyyy"])