# coding:utf-8
from __future__ import unicode_literals

from datetime import datetime
from validater import validate, validaters, add_validater


def test_1():
    list(validaters)


def test_2():
    add_validater("haha", lambda v: (True, v))
    assert "haha" in validaters

data_ok = {
    "any": [
        123,
        "哈哈",
        "*^^&}}::",
        object(),
        [{}],
        {},
        {"haha": []}
    ],
    "str": [
        str("哈哈".encode("utf-8")),
        str("123213".encode("utf-8")),
        str(">?<*&".encode("utf-8")),
    ],
    "unicode": [
        "哈哈",
        ">?<*&",
        "123213"
    ],
    "bool": [
        True,
        False,
    ],
    "int": [
        -1,
        2,
        0,
        1,
        999999999999999999999999999999999999999999999999999999999999999999999999999,
        -99999999999999999999999999999999999999999999999999999999999999999999999999999,
        564678597,
        12434,
        "-1",
        "2",
        "0",
        "1",
        "999999999999999999999999999999999999999999999999999999999999999999999999999",
        "-99999999999999999999999999999999999999999999999999999999999999999999999999999",
        "564678597",
        "12434",
    ],
    "+int": [
        1,
        2,
        5437658,
        999999999999999999999,
        "1",
        "2",
        6.6,
        "5437658",
        "999999999999999999999",
    ],
    "float": [
        1,
        0,
        -1,
        0.0,
        -0.0,
        -1.0,
        1.2,
        99999999999999999999999999999999.9999999999999999999999,
        "0.0",
        "-0.0",
        "-1.0",
        "1.2",
        "99999999999999999999999999999999.9999999999999999999999",
    ],
    "datetime": [
        datetime.now(),
        datetime.utcnow(),
        "2015-08-09 15:50:49"
    ],
    "email": [
        "1316792450@qq.com",
        "haha@gmail.com"
    ],
    "ipv4": [
        "192.168.191.1",
        "127.0.0.1"
    ],
    "phone": [
        "15083766985"
    ],
    "idcard": [
        "36178319950616383x",
        "36178319950616383X",
        "361783199506163830"
    ],
    "url": [
        "http://tool.lu/regex/",
        "https://github.com/guyskk/kkblog",
        "https://avatars3.githubusercontent.com/u/6367792?v=3&s=40",
    ],
    "name": [
        "guyskk",
        "a1424546",
        "z5436757",
        "GUYSKK",
        "A1424546",
        "Z5436757",
    ],
    "password": [
        "guyskk",
        "a1424546",
        "z5436757",
        "123456",
        "!@#$%^&*()",
        "~!{}|:?><",
    ],
    "safestr": [
        "ASDFGHJKMHJGHFGFFRdrvasdjfks<>{}'''",
        '""""""""""""<>>&*%#@@$^&'
    ],
}

data_err = {
    "str": [
        213,
        0,
        0.1,
        None,
    ],
    "unicode": [
        1232,
        0,
        None
    ],
    "bool": [
        0,
        1,
        None,
        ""
    ],
    "int": [
        "adf",
        "fff",
        "a22",
        "0x00",
    ],
    "+int": [
        -1,
        0,
        0.0,
        -435,
        "-414"
    ],
    "float": [
        None,
        "0x00"
    ],
    "datetime": [
        1435425,
        "14234",
        "a123456789123456x",
        "123",
        "aaa",
        "a12",
        "中文"
    ],
    "email": [
        "qq.com",
        "fsfsdf",
        123546,
    ],
    "ipv4": [
        "127.0.0.x"
    ],
    "phone": [
        "1316793456"
        "1316793456x"
    ],
    "idcard": [
        "36178319950616383y",
        "3617831995061638xX",
        "36178319950616383"
    ],
    "url": [
        "1316792450@qq.com"
    ],
    "name": [
        "14234",
        "a123456789123456x",
        "123",
        "aaa",
        "a12",
        "中文"
    ],
    "password": [
        "14234",
        "a123456789123456x",
        "123",
        "aaa",
        "a12",
        "中文"
    ],
    "safestr": [
        datetime.now(),
        {},
        None
    ]
}


def test_validate_ok():
    for k, v in data_ok.items():
        schema = {"validate": k, "required": True}
        for x in v:
            err, val = validate(x, schema)
            assert not err, "%s: %s" % (k, x)


def test_validate_err():
    for k, v in data_err.items():
        schema = {"validate": k, "required": True}
        for x in v:
            err, val = validate(x, schema)
            assert err, "%s: %s" % (k, x)
