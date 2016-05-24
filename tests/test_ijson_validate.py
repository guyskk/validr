#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
from validater import parse, validate
from six import BytesIO
import json


def create_file(obj):
    data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
    return BytesIO(data)


def test_base():
    sche = parse({
        "array": ["int&required"],
        "map": {
            "key": "str&required"
        }
    })
    obj = create_file({
        "array": ["123", "456"],
        "map": {"key": "value"}
    })
    err, val = validate(obj, sche)
    assert not err
    assert val == {
        "array": [123, 456],
        "map": {"key": "value"}
    }


def test_deep_list():
    sche = parse(["int&required"])
    data = '[' * 8000 + ']' * 8000
    obj = BytesIO(data.encode('utf-8'))
    err, val = validate(obj, sche)
    assert err
    key, reason = err[0]
    assert key == '[0]'
    assert 'int' in reason
