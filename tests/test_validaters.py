#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

import datetime
import re
from validater import (validate, parse, re_validater, type_validater,
                       add_validater, remove_validater)
import pytest

my_validaters = {}


@pytest.fixture(scope='session', autouse=True)
def custom_validaters():
    year_validater = re_validater(re.compile(r"^\d{4}$"))
    add_validater("year", year_validater, my_validaters)
    add_validater("list", type_validater(list, empty=[]), my_validaters)

    def abs_validater(v, debug=False):
        try:
            return True, abs(v)
        except:
            if debug:
                raise
            return False, None
    add_validater('abs', abs_validater, my_validaters)


def test_custom_validaters():
    assert "year" in my_validaters
    assert "list" in my_validaters
    assert "abs" in my_validaters

    # parse schema with custom_validaters
    parse([{"year": "year&required"}], my_validaters)

    data = {
        'year': ['2016', '1984'],
        'list': [[], [None], [123, 456]],
        'abs': [1, -1, 0, -100]
    }
    expect = {
        'year': ['2016', '1984'],
        'list': [[], [None], [123, 456]],
        'abs': [1, 1, 0, 100]
    }
    for sche, objs in data.items():
        schema = parse(sche, my_validaters)
        for i, obj in enumerate(objs):
            err, val = validate(obj, schema)
            assert not err
            assert val == expect[sche][i]

    with pytest.raises(Exception):
        sche = parse('abs&required&debug', my_validaters)
        validate(object(), sche)

    remove_validater("year", my_validaters)
    remove_validater("list", my_validaters)
    remove_validater("abs", my_validaters)
    assert "year" not in my_validaters
    assert "list" not in my_validaters
    assert "abs" not in my_validaters


def test_datetime():
    d = datetime.datetime(2016, 1, 1)
    s = "2016-01-01T00:00:00.000000Z"
    err, val = validate(d, parse("datetime&output"))
    assert not err
    assert val == s
    err, val = validate(s, parse("datetime&output"))
    assert not err
    assert val == s

    err, val = validate(d, parse("datetime&input"))
    assert not err
    assert val == d
    err, val = validate(s, parse("datetime&input"))
    assert not err
    assert val == d

    err, val = validate(d, parse("datetime"))
    assert not err
    assert val == s
    err, val = validate(s, parse("datetime"))
    assert not err
    assert val == d


def test_date():
    dt = datetime.datetime(2016, 1, 1)
    d = datetime.datetime(2016, 1, 1).date()
    s = "2016-01-01"
    err, val = validate(d, parse("date&output"))
    assert not err
    assert val == s
    err, val = validate(dt, parse("date&output"))
    assert not err
    assert val == s
    err, val = validate(s, parse("date&output"))
    assert not err
    assert val == s

    err, val = validate(d, parse("date&input"))
    assert not err
    assert val == d
    err, val = validate(dt, parse("date&input"))
    assert not err
    assert val == d
    err, val = validate(s, parse("date&input"))
    assert not err
    assert val == d

    err, val = validate(d, parse("date"))
    assert not err
    assert val == s
    err, val = validate(dt, parse("date"))
    assert not err
    assert val == s
    err, val = validate(s, parse("date"))
    assert not err
    assert val == d

data_ok = {
    "any": [123, object(), [{}]],
    "str": ["哈哈", str("123213"), str(">?<*&")],
    "unicode": ["哈哈", ">?<*&", "123213"],
    "bool": [True, False],
    "int": [-1, 2, 0, "-1", "2", "0", "12434",
            0.1, -1.1, 6.6, 1.0,
            "9" * 20, "-" + "9" * 20],
    "+int": [1, 2, 5437658, "9" * 20,
             "1", "2", 6.6, "5437658"],
    "float": [1, 0, -1, 0.0, -0.0, -1.0, 1.2,
              "9" * 20 + "." + "9" * 20,
              "0.0", "-0.0", "-1.0", "1.2"],
    "datetime&output": [datetime.datetime.now(), datetime.datetime.utcnow()],
    "datetime": ["2015-08-09T15:50:49.0Z",
                 "2013-05-07T05:59:59.999999Z",
                 "2013-05-27T23:35:35.533160Z"],
    "email": ["12345678@qq.com",
              "haha@gmail.com"],
    "ipv4": ["192.168.191.1",
             "127.0.0.1"],
    "phone": ["15083766985"],
    "idcard": ["36178319950616383x",
               "36178319950616383X",
               "361783199506163830"],
    "url": ["http://tool.lu/regex/",
            "https://github.com/guyskk/kkblog",
            "https://avatars3.githubusercontent.com/u/6367792?v=3&s=40", ],
    "name": ["guyskk", "a1424546", "z5436757",
             "GUYSKK", "A1424546", "Z5436757"],
    "password": ["guyskk", "xxx123", "123xyz", "123456",
                 "!@#$%^&*()", "~!{}|:?><"],
    "safestr": ["ASDFGHJKMHJGHFGFFRdrvasdjfks<>{}'''",
                '""""""""""""<>>&*%#@@$^&'],
}

data_err = {
    "str": [213, 0, 0.1, None],
    "unicode": [1232, 0, None],
    "bool": [0, 1, None, ""],
    "int": ["adf", "fff", "a22", "0x00"],
    "+int": [-1, 0, 0.0, -435, "-414"],
    "float": [None, "0x00"],
    "datetime": [1435425, "14234", "中文",
                 "2015-08-09T15:50:49.0",
                 "2015-08-09 15:50:49.0Z",
                 "2015-08-09T15:50:49Z"],
    "date": [1435425, "14234", "中文",
             "2015-08-09T15:50:49.0Z",
             "08-09", "2015/08/09 ",
             "15:50:49", "20150809"],
    "email": ["qq.com", "fsfsdf", 123546],
    "ipv4": ["127.0.0.x"],
    "phone": ["1316793456"
              "1316793456x"],
    "idcard": ["36178319950616383y",
               "3617831995061638xX",
               "36178319950616383"],
    "url": ["1316792450@qq.com"],
    "name": ["14234",
             "a123456789123456x",
             "123",
             "aaa",
             "a12",
             "中文"],
    "password": ["14234",
                 "a123456789123456x",
                 "123",
                 "aa a",
                 "a1\t2",
                 "asdfg123\n"
                 "中文"],
    "safestr": [datetime.datetime.now(),
                {},
                None]
}


def test_validate_ok():
    for sche, v in data_ok.items():
        sche = parse(sche + "&required")
        for x in v:
            err, val = validate(x, sche)
            assert not err, "%s: %s" % (sche, x)


def test_validate_err():
    for sche, v in data_err.items():
        sche = parse(sche + "&required")
        for x in v:
            err, val = validate(x, sche)
            assert err, "%s: %s" % (sche, x)
