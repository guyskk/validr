# coding:utf-8
from __future__ import unicode_literals


from validater import validate, add_validater

# support py3
try:
    basestring
    unicode
except NameError:
    basestring = unicode = str


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
