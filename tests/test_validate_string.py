# coding:utf-8
from __future__ import unicode_literals
from validater import validate


def test_validate_unicode():
    """treat "" as NULL, and convert NULL to ""
    """
    # test unicode
    schem = {
        "validate": "unicode",
        "required": True
    }
    err, val = validate("haha", schem)
    assert not err
    assert val == "haha"
    err, val = validate(None, schem)
    assert err
    assert val == ""
    err, val = validate("", schem)
    assert err
    assert val == ""
    schem = {
        "validate": "unicode",
    }
    err, val = validate(None, schem)
    assert not err
    assert val == ""
    err, val = validate("", schem)
    assert not err
    assert val == ""


def test_validate_str():
    """treat "" as NULL, and convert NULL to ""
    """
    # test str
    schem = {
        "validate": "str",
        "required": True
    }
    err, val = validate(b"haha", schem)
    assert not err
    assert val == b"haha"
    err, val = validate(None, schem)
    assert err
    assert val == b""
    err, val = validate(b"", schem)
    assert err
    assert val == b""
    schem = {
        "validate": "str",
    }
    err, val = validate(None, schem)
    assert not err
    assert val == b""
    err, val = validate(b"", schem)
    assert not err
    assert val == b""
