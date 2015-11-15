# coding:utf-8
from __future__ import unicode_literals


from validater import validate, add_validater


def test_obj_list_schema_not_list():
    schema_outputs = {
        "name": {
            "desc": "标签名称",
            "validate": "unicode",
            "required": True
        },
        "count": {
            "desc": "文章数量",
            "validate": "int",
            "required": True
        },
    }

    obj = [{"name": "name123", "count": 1}] * 5
    (error, value) = validate(obj, schema_outputs)
    assert error
    assert "must be dict" in error[0]


def test_list_schema_and_string_obj():
    s = [{u'validate': u'+int', u'required': True}]
    obj = [1, 2, 3, 4]
    err, val = validate(obj, s)
    assert not err
    assert obj == val
    obj = "[1, 2, 3, 4]"
    err, val = validate(obj, s)
    assert err
    assert "must be list" in err[0][1]
    err, val = validate(None, s)
    assert err
    assert "must be list" in err[0][1]
