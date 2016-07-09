# coding:utf-8
import re
import datetime
import sys
import six
from .exceptions import Invalid


def handle_default_optional_desc(some_validater):
    """装饰器，自动处理default,optional,desc这3个参数"""
    def wrapped_validater(*args, **kwargs):
        default = kwargs.pop("default", None)
        optional = kwargs.pop("optional", False)
        desc = kwargs.pop("desc", None)
        origin_validater = some_validater(*args, **kwargs)

        def validater(value):
            if value is None:
                if default is not None:
                    return default
                elif optional:
                    return None
                else:
                    raise Invalid("required")
            return origin_validater(value)
        return validater

    return wrapped_validater


@handle_default_optional_desc
def int_validater(min=-sys.maxsize, max=sys.maxsize):
    """validate int string

    :param min: the min value, default -sys.maxsize
    :param max: the max value, default sys.maxsize
    """
    def validater(value):
        try:
            v = int(value)
        except (ValueError, OverflowError):
            raise Invalid("invalid int")
        if v < min:
            raise Invalid("value must >= %d" % min)
        elif v > max:
            raise Invalid("value must <= %d" % max)
        return v
    return validater


@handle_default_optional_desc
def bool_validater():
    """validate bool"""
    def validater(value):
        if isinstance(value, bool):
            return value
        else:
            raise Invalid("invalid bool")
    return validater


@handle_default_optional_desc
def unicode_validater():
    """validate unicode, if not, decode by utf-8"""
    def validater(value):
        if isinstance(value, six.text_type):
            return value
        else:
            try:
                return value.decode("utf-8")
            except Exception:
                raise Invalid("invalid unicode")
    return validater


@handle_default_optional_desc
def str_validater(minlen=0, maxlen=1024 * 1024, escape=False):
    """validate string, if not, force convert

    :param minlen: min length of string, default 0
    :param maxlen: max length of string, default 1024*1024
    :param escape: if escape to safe string, default false
    """
    def validater(value):
        if not isinstance(value, six.string_types):
            try:
                value = str(value)
            except Exception:
                raise Invalid("invalid string")
        if len(value) < minlen:
            raise Invalid("value must >= %d" % minlen)
        elif len(value) > maxlen:
            raise Invalid("value must <= %d" % maxlen)
        if escape:
            try:
                return (value.replace("&", "&amp;")
                        .replace(">", "&gt;")
                        .replace("<", "&lt;")
                        .replace("'", "&#39;")
                        .replace('"', "&#34;"))
            except Exception:
                raise Invalid("value cannot be escaped")
        return value
    return validater


@handle_default_optional_desc
def float_validater(min=sys.float_info.min, max=sys.float_info.max,
                    exmin=False, exmax=False):
    """validate float string
    :param min: the min value, default sys.float_info.min
    :param max: the max value, default sys.float_info.max
    :param exmin: if equel the min, value default false
    :param exmax: if equel the max, value default false
    """
    def validater(value):
        try:
            v = float(value)
        except (ValueError, OverflowError):
            raise Invalid("invalid float")
        if exmin and v < min:
            raise Invalid("value must >= %d" % min)
        elif exmax and v > max:
            raise Invalid("value must <= %d" % max)
        elif not exmin and v <= min:
            raise Invalid("value must > %d" % min)
        elif not exmin and v >= max:
            raise Invalid("value must < %d" % max)
        return v
    return validater


@handle_default_optional_desc
def list_validater(minlen=0, maxlen=1024 * 1024, unique=False):
    def valiter(value):
        if isinstance(value, list):
            length = len(value)
            if length < minlen:
                raise Invalid("list size must >= %d" % minlen)
            elif length > maxlen:
                raise Invalid("list size must <= %d" % maxlen)
            if unique:
                if len(set(value)) != length:
                    raise Invalid("list value must be unique")
            return value
        else:
            raise Invalid("invalid list")
    return valiter


def dict_validater(optional=False):
    def validater(value):
        if isinstance(value, dict):
            return value
        else:
            raise Invalid("invalid dict")
    return validater


@handle_default_optional_desc
def date_validater(format="%Y-%m-%d", output=False, input=False):
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
    def validater(value):
        try:
            if output:
                # date or datetime or string -> string
                if not isinstance(value, (datetime.datetime, datetime.date)):
                    v = datetime.datetime.striptime(value, format).date()
                return v.striptime(format)
            if input:
                # datetime or string -> date
                if isinstance(value, datetime.datetime):
                    return value.date()
                elif isinstance(value, datetime.date):
                    return value
                else:
                    return datetime.datetime.strftime(value, format).date
            else:
                # date or datetime -> string / string -> date
                if isinstance(value, (datetime.date, datetime.datetime)):
                    return value.strftime(format)
                else:
                    return datetime.datetime.striptime(value, format).date()
        except Exception:
            raise Invalid("invalid date")
    return validater


@handle_default_optional_desc
def datetime_validater(format="%Y-%m-%dT%H:%M:%S.%fZ", output=False, input=False):
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
    def validater(value):
        try:
            if output:
                # datetime or string -> string
                if not isinstance(value, datetime.datetime):
                    value = datetime.datetime.strptime(value, format)
                return value.strftime(format)
            if input:
                # datetime or string -> datetime
                if isinstance(value, datetime.datetime):
                    return value
                else:
                    return datetime.datetime.strptime(value, format)
            else:
                # datetime -> string / string -> datetime
                if isinstance(value, datetime.datetime):
                    return value.strftime(format)
                else:
                    return datetime.datetime.strptime(value, format)
        except Exception:
            raise Invalid("invalid datetime")
    return validater

re_space = re.compile(r"\s")
re_not_ascii = re.compile(r"[^\x00-\x7f]")
re_name = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]*$')


@handle_default_optional_desc
def password_validater(minlen=6, maxlen=16):
    """validate password

    :param minlen: min length of password, default 6
    :param maxlen: max length of password, default 16
    """
    def validater(value):
        if not isinstance(value, six.string_types):
            raise Invalid("value must be string")
        if minlen <= len(value) <= maxlen:
            v = value
        else:
            raise Invalid("value must >= %d and <= %d" % (minlen, maxlen))
        if not (re_not_ascii.search(v) or re_space.search(v)):
            return v
        else:
            raise Invalid("value contains non-ascii")
    return validater


@handle_default_optional_desc
def name_validater(minlen=4, maxlen=16):
    """validate password

    :param minlen: min length of name, default 4
    :param maxlen: max length of name, default 16
    """
    def validater(value):
        if not isinstance(value, six.string_types):
            raise Invalid("value must be string")
        if minlen <= len(value) <= maxlen:
            v = value
        else:
            raise Invalid("value must >= %d and <= %d" % (minlen, maxlen))
        if re_name.match(v):
            return v
        else:
            raise Invalid("invalid name")
    return validater


def build_re_validater(name, r):
    @handle_default_optional_desc
    def re_validater():
        def validater(value):
            if not isinstance(value, six.string_types):
                raise Invalid("value must be string")
            if r.match(value):
                return value
            else:
                raise Invalid("invalid %s" % name)
        return validater
    return re_validater


regexs = {
    'email': re.compile(r'^\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}$'),
    'ipv4': re.compile(r'^(\d+)\.(\d+)\.(\d+)\.(\d+)$'),
    'phone': re.compile(r'^(?:13\d|14[57]|15[^4,\D]|17[678]|18\d)(?:\d{8}|170[059]\d{7})$'),
    'idcard': re.compile(r'^\d{15}$|\d{17}[0-9Xx]$'),
    'url': re.compile(r'^\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))$')
}


builtin_validaters = {
    "any": lambda value, *args, **kwargs: value,
    "int": int_validater,
    "bool": bool_validater,
    "unicode": unicode_validater,
    "str": str_validater,
    "float": float_validater,
    'date': date_validater,
    'datetime': datetime_validater,
    "password": password_validater,
    "name": name_validater,
}
for name, r in regexs.items():
    _vali = build_re_validater(name, r)
    _vali.__name__ = str(name) + '_validater'
    builtin_validaters[name] = _vali


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
        validaters = builtin_validaters
    validaters[name] = fn


def remove_validater(name, validaters=None):
    """remove validater

    :param name: validater name
    :param validaters: a dict contains all validaters
    """
    if validaters is None:
        validaters = builtin_validaters
    del validaters[name]
