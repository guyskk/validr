# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
import six

import re
from datetime import datetime
from dateutil.parser import parse as date_parse

# remove it because objectid_validater is not common used
#
# from bson.objectid import ObjectId


# def objectid_validater(v):
#     """validater for bson.objectid.ObjectId or string"""
#     try:
#         return (True, ObjectId(v))
#     except:
#         return (False, None)


def re_validater(r):
    """Return a regex validater

    :param r: regex object
    """
    def vali(v):
        if isinstance(v, six.string_types) and r.match(v):
            return (True, v)
        return (False, "")
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


def string_type_validater(cls):
    """Return a string type validater, convert None to ""

    :param cls: valid class of value
    """
    def vali(v):
        if isinstance(v, cls):
            return (True, v)
        else:
            return (False, "")
    return vali


def datetime_validater(v):
    """validater for datetime object or datetime string"""
    if isinstance(v, datetime):
        return (True, v)
    else:
        if isinstance(v, six.string_types) and re_datetime.match(v):
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


def plus_int_validater(v):
    try:
        i = int(v)
        if i > 0:
            return (True, i)
    except:
        pass
    return (False, None)


def float_validater(v):
    """validater for float object or string"""
    try:
        return (True, float(v))
    except:
        return (False, None)


def safestr_validater(v):
    """validater for string, escape ``'>', '<', "'", '"'``"""
    if isinstance(v, six.string_types):
        return (True, v.replace('&', '&amp;')
                .replace('>', '&gt;')
                .replace('<', '&lt;')
                .replace("'", '&#39;')
                .replace('"', '&#34;'))
    else:
        return (False, "")


def password_validater(v):
    re_not_space = re.compile(r"^\S{6,16}$")
    re_ascii = re.compile(r"^[\x00-\x7f]{6,16}$")
    if isinstance(v, six.string_types) and re_ascii.match(v) and re_not_space.match(v):
        return (True, v)
    else:
        return (False, "")


# more http://www.cnblogs.com/zxin/archive/2013/01/26/2877765.html
re_datetime = re.compile(r'^(\d{4})-(\d{1,2})-(\d{1,2})[ T](\d{1,2}):(\d{1,2}):(\d{1,2})(\.\d+.*)?$')
re_email = re.compile(r'^\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}$')
re_ipv4 = re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$')
re_phone = re.compile(r'^(?:13\d|14[57]|15[^4,\D]|17[678]|18\d)(?:\d{8}|170[059]\d{7})$')
re_idcard = re.compile(r'^\d{15}$|\d{17}[0-9Xx]$')
re_name = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{3,15}$')
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
re_url = re.compile(
    r'^\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))$')


validaters = {
    "any": lambda v: (True, v),
    "str": string_type_validater(six.string_types),
    "unicode": string_type_validater(six.text_type),
    "bool": bool_validater,
    "int": int_validater,
    "+int": plus_int_validater,
    "float": float_validater,
    "datetime": datetime_validater,
    # "objectid": objectid_validater,
    "email": re_validater(re_email),
    "ipv4": re_validater(re_ipv4),
    "phone": re_validater(re_phone),
    "idcard": re_validater(re_idcard),
    "url": re_validater(re_url),
    "name": re_validater(re_name),
    "password": password_validater,
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
