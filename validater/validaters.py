# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import

from bson.objectid import ObjectId
import re
from datetime import datetime
from dateutil.parser import parse as date_parse


def re_validater(r):
    """Return a regex validater

    :param r: regex object
    """
    def vali(v):
        if isinstance(v, basestring) and r.match(v):
            return (True, v)
        return (False, None)
    return vali


def type_validater(cls):
    """Return a type validater

    :param cls: valid class of value
    """
    def vali(v):
        if isinstance(v, cls):
            return (True, v)
        else:
            return (False, None)
    return vali


def datetime_validater(v):
    """validater for datetime object or datetime string"""
    if isinstance(v, datetime):
        return (True, v)
    else:
        if isinstance(v, basestring) and re_datetime.match(v):
            try:
                return (True, date_parse(v))
            except:
                pass
        return (False, None)


def bool_validater(v):
    """validater for bool object"""
    if isinstance(v, bool):
        return (True, v)
    return (False, None)


def int_validater(v):
    """validater for int object or string"""
    try:
        return (True, int(v))
    except:
        return (False, None)


def long_validater(v):
    """validater for long object or string"""
    try:
        return (True, long(v))
    except:
        return (False, None)


def float_validater(v):
    """validater for float object or string"""
    try:
        return (True, float(v))
    except:
        return (False, None)


def basestring_validater(v):
    """working in both Py2 and Py3"""
    try:
        if isinstance(obj, basestring):
            return (True, v)
        else:
            return (False, None)
    except NameError:
        if isinstance(v, str):
            return (True, v)
        else:
            return (False, None)


def objectid_validater(v):
    """validater for bson.objectid.ObjectId or string"""
    try:
        return (True, ObjectId(v))
    except:
        return (False, None)


def safestr_validater(v):
    """validater for string, escape ``'>', '<', "'", '"'``"""
    if isinstance(v, basestring):
        return (True, v.replace('&', '&amp;')
                .replace('>', '&gt;')
                .replace('<', '&lt;')
                .replace("'", '&#39;')
                .replace('"', '&#34;'))
    else:
        return (False, None)

# more http://www.cnblogs.com/zxin/archive/2013/01/26/2877765.html
re_datetime = re.compile(r'^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})(.\d+\w?)?$')
re_email = re.compile(r'^\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}$')
re_ipv4 = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$')
re_phone = re.compile(r'^(13\d|14[57]|15[^4,\D]|17[678]|18\d)\d{8}|170[059]\d{7}$')
re_idcard = re.compile(r'^\d{15}|\d{17}[0-9Xx]$')
re_name = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{3,15}$')
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
re_url = re.compile(
    r'^\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))$')


validaters = {
    "any": lambda v: (True, v),
    "basestring": basestring_validater,
    "unicode": type_validater(unicode),
    "str": type_validater(str),
    "list": type_validater(list),
    "dict": type_validater(dict),
    "bool": bool_validater,
    "int": int_validater,
    "long": long_validater,
    "float": float_validater,
    "datetime": datetime_validater,
    "objectid": objectid_validater,
    "re_email": re_validater(re_email),
    "re_ipv4": re_validater(re_ipv4),
    "re_phone": re_validater(re_phone),
    "re_idcard": re_validater(re_idcard),
    "re_url": re_validater(re_url),
    "re_name": re_validater(re_name),
    "safestr": safestr_validater,
}


def add_validater(name, fn):
    """add validater

    :param name: validater name
    :param fn: ``validater(v) -> tuple(ok, value)``

        - ok is True or False, indicate valid
        - value is converted value or None(if ok is False)
    """
    validaters[name] = fn
