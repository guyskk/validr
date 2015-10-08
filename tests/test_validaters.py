# coding:utf-8
from __future__ import unicode_literals

from validater import validaters, add_validater

# support py3
try:
    basestring
    unicode
except NameError:
    basestring = unicode = str


def test_1():
    list(validaters)


def test_2():
    add_validater("haha", lambda v: (True, v))
    assert "haha" in validaters
