#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function

import six
import re
import datetime
from functools import partial


def re_validater(r):
    """return a regex validater

    :param r: regex object
    """
    def vali(v):
        try:
            if r.match(v):
                return True, v
            else:
                return False, ""
        except:
            return False, ""
    vali.__doc__ = repr(r)
    return vali


def type_validater(cls, empty=None):
    """return a type validater

    :param cls: class-or-type-or-tuple
    :param empty: a value represent empty
    """
    def vali(v):
        if isinstance(v, cls):
            return True, v
        else:
            return False, empty
    if isinstance(cls, tuple):
        name = "_".join([x.__name__ for x in cls])
    else:
        name = cls.__name__
    vali.__name__ = str(name + "_validater")
    vali.__doc__ = repr(cls)
    return vali


def datetime_validater(v, format='%Y-%m-%dT%H:%M:%S.%fZ', output=False, input=False):
    """validate datetime object or datetime string

    note::

        if both output and input is False:
            if v is datetime:
                convert to string
            else:
                convert to datetime

    :param format: datetime format
    :param output: convert value to string
    :param input: convert value to datetime
    """
    try:
        if output:
            # datetime or string -> string
            if not isinstance(v, datetime.datetime):
                v = datetime.datetime.strptime(v, format)
            return True, v.strftime(format)
        if input:
            # datetime or string -> datetime
            if isinstance(v, datetime.datetime):
                return True, v
            else:
                return True, datetime.datetime.strptime(v, format)
        else:
            # datetime -> string / string -> datetime
            if isinstance(v, datetime.datetime):
                return True, v.strftime(format)
            else:
                return True, datetime.datetime.strptime(v, format)
    except:
        return False, None


def date_validater(v, format='%Y-%m-%d', output=False, input=False):
    """validate date/datetime object or date string

    note::

        if both output and input is False:
            if v is date or datetime:
                convert to string
            else:
                convert to date

    :param format: date format
    :param output: convert value to string
    :param input: convert value to date
    """
    try:
        if output:
            # date or datetime or string -> string
            if not isinstance(v, (datetime.datetime, datetime.date)):
                v = datetime.datetime.strptime(v, format).date()
            return True, v.strftime(format)
        if input:
            # datetime or string -> date
            # note: datetime is subclass of date
            if isinstance(v, datetime.datetime):
                return True, v.date()
            elif isinstance(v, datetime.date):
                return True, v
            else:
                return True, datetime.datetime.strptime(v, format).date()
        else:
            # date or datetime -> string / string -> date
            if isinstance(v, (datetime.date, datetime.datetime)):
                return True, v.strftime(format)
            else:
                return True, datetime.datetime.strptime(v, format).date()
    except:
        return False, None


def int_validater(v, start=None, stop=None):
    """validate int string

    :param start: the min value
    :param stop: the max value
    """
    try:
        x = int(v)
        if start is not None and x < start:
            return False, None
        if stop is not None and x > stop:
            return False, None
        return True, x
    except:
        return False, None


def float_validater(v, start=None, stop=None):
    """validate float string

    :param start: the min value
    :param stop: the max value
    """
    try:
        x = float(v)
        if start is not None and x < start:
            return False, None
        if stop is not None and x > stop:
            return False, None
        return True, x
    except:
        return False, None


def safestr_validater(v):
    """escape special string ``'>', '<', "'", '"'``"""
    try:
        return (True, v.replace('&', '&amp;')
                .replace('>', '&gt;')
                .replace('<', '&lt;')
                .replace("'", '&#39;')
                .replace('"', '&#34;'))
    except:
        return False, ""

re_space = re.compile(r"\s")
re_not_ascii = re.compile(r"[^\x00-\x7f]")
re_name = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')


def password_validater(v, minlength=6, maxlength=16):
    """validate password

    :param minlength: minlength of password
    :param maxlength: maxlength of password
    """
    try:
        if minlength <= len(v) <= maxlength:
            if not ((re_not_ascii.search(v) or re_space.search(v))):
                return True, v
    except:
        pass
    return False, ""


def name_validater(v, minlength=4, maxlength=16):
    try:
        if minlength <= len(v) <= maxlength:
            if re_name.match(v):
                return True, v
    except:
        pass
    return False, ""

# see http://www.cnblogs.com/zxin/archive/2013/01/26/2877765.html
# http://daringfireball.net/2010/07/improved_regex_for_matching_urls
regexs = {
    'email': re.compile(r'^\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}$'),
    'ipv4': re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$'),
    'phone': re.compile(r'^(?:13\d|14[57]|15[^4,\D]|17[678]|18\d)(?:\d{8}|170[059]\d{7})$'),
    'idcard': re.compile(r'^\d{15}$|\d{17}[0-9Xx]$'),
    'url': re.compile(r'^\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))$')
}

default_validaters = {
    "any": lambda v, *args, **kwargs: (True, v),
    "str": type_validater(six.string_types, empty=str("")),
    "unicode": type_validater(six.text_type, empty=""),
    "bool": type_validater(bool),
    "int": int_validater,
    "+int": partial(int_validater, start=1),
    "float": float_validater,
    "datetime": datetime_validater,
    "date": date_validater,
    "safestr": safestr_validater,
    "password": password_validater,
    "name": name_validater,
}
for name, r in regexs.items():
    _vali = re_validater(r)
    _vali.__name__ = str(name + '_validater')
    default_validaters[name] = _vali


def add_validater(name, fn, validaters=None):
    """add validater

    validater::

        def validater(v, args, kwargs):
            # ok is True if v is valid, False otherwise
            # value is converted value or None(if v is not valid)
            return ok,value

    :param name: validater name
    :param fn: validater
    :param validaters: a dict contains all validaters
    """
    if validaters is None:
        validaters = default_validaters
    validaters[name] = fn


def remove_validater(name, validaters=None):
    """remove validater

    :param name: validater name
    :param validaters: a dict contains all validaters
    """
    if validaters is None:
        validaters = default_validaters
    del validaters[name]
