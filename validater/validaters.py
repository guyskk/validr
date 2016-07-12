import re
import datetime
import sys
from .exceptions import Invalid


def handle_default_optional_desc(some_validater):
    """Decorator for handling params: default,optional,desc"""
    def wrapped_validater(*args, **kwargs):
        default = kwargs.pop("default", None)
        optional = kwargs.pop("optional", False)
        kwargs.pop("desc", None)
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
    """Validate int string

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
    """Validate bool"""
    def validater(value):
        if isinstance(value, bool):
            return value
        else:
            raise Invalid("invalid bool")
    return validater


@handle_default_optional_desc
def float_validater(min=-sys.float_info.max, max=sys.float_info.max,
                    exmin=False, exmax=False):
    """Validate float string

    :param min: the min value, default sys.float_info.min
    :param max: the max value, default sys.float_info.max
    :param exmin: exclude min value or not, default false
    :param exmax: exclude max value or not, default false
    """
    def validater(value):
        try:
            v = float(value)
        except (ValueError, OverflowError):
            raise Invalid("invalid float")
        if exmin:
            if v <= min:
                raise Invalid("value must > %d" % 11)
        else:
            if v < min:
                raise Invalid("value must >= %d" % min)
        if exmax:
            if v >= max:
                raise Invalid("value must < %d" % max)
        else:
            if v > max:
                raise Invalid("value must <= %d" % max)
        return v
    return validater


@handle_default_optional_desc
def str_validater(minlen=0, maxlen=1024 * 1024, escape=False):
    """Validate string

    :param minlen: min length of string, default 0
    :param maxlen: max length of string, default 1024*1024
    :param escape: escape to safe string or not, default false
    """
    def validater(value):
        if not isinstance(value, str):
            raise Invalid("invalid string")
        if len(value) < minlen:
            raise Invalid("string length must >= %d" % minlen)
        elif len(value) > maxlen:
            raise Invalid("string length must <= %d" % maxlen)
        if escape:
            return (value.replace("&", "&amp;")
                    .replace(">", "&gt;")
                    .replace("<", "&lt;")
                    .replace("'", "&#39;")
                    .replace('"', "&#34;"))
        else:
            return value
    return validater


@handle_default_optional_desc
def date_validater(format="%Y-%m-%d"):
    """Validate date string, convert value to string

    :param format: date format, default ISO8601
    """
    def validater(value):
        try:
            if not isinstance(value, (datetime.datetime, datetime.date)):
                value = datetime.datetime.strptime(value, format)
            return value.strftime(format)
        except Exception:
            raise Invalid("invalid date")
    return validater


@handle_default_optional_desc
def datetime_validater(format="%Y-%m-%dT%H:%M:%S.%fZ"):
    """Validate datetime string, convert value to string

    :param format: datetime format, default ISO8601
    """
    def validater(value):
        try:
            if not isinstance(value, datetime.datetime):
                value = datetime.datetime.strptime(value, format)
            return value.strftime(format)
        except Exception:
            raise Invalid("invalid datetime")
    return validater


def build_re_validater(name, r):
    @handle_default_optional_desc
    def re_validater():
        def validater(value):
            if not isinstance(value, str):
                raise Invalid("value must be string")
            if r.match(value):
                return value
            else:
                raise Invalid("invalid %s" % name)
        return validater
    re_validater.__name__ = name + '_validater'
    return re_validater

# Notes
# email: http://tool.lu/regex/
# phone: http://tool.lu/regex/ [modified]
# ipv4: https://segmentfault.com/a/1190000004622152 [modified]
# idcard: https://segmentfault.com/a/1190000004622152 [modified]
# url: unknown
regexs = {
    'email': r'^\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]{2,14}$',
    'phone': r'^((\+86)|(86))?(13\d|14[57]|15[^4,\D]|17[678]|18\d)\d{8}|170[059]\d{7}$',
    'ipv4': r"^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[0-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[0-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[0-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[0-9]\d|\d)$",
    'idcard': r'^\d{17}[\d|x|X]|\d{15}',
    'url': r'^\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))$'
}

builtin_validaters = {
    "int": int_validater,
    "bool": bool_validater,
    "float": float_validater,
    "str": str_validater,
    'date': date_validater,
    'datetime': datetime_validater,
}

for name, regex in regexs.items():
    # To make sure that the entire string matches
    r = re.compile(r"(?:%s)\Z" % regex)
    builtin_validaters[name] = build_re_validater(name, r)
