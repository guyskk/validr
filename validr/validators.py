import re
import datetime
import sys
from .exceptions import Invalid


def handle_default_optional_desc(string=False):
    """
    Decorator for handling params: default,optional,desc

    :param string: if the value to be validated is string or not
    """
    def handler(some_validator):
        def wrapped_validator(*args, **kwargs):
            default = kwargs.pop("default", None)
            optional = kwargs.pop("optional", False)
            kwargs.pop("desc", None)
            origin_validator = some_validator(*args, **kwargs)
            if string:
                def validator(value):
                    if value is None or value == "":
                        if not (default is None or default == ""):
                            return default
                        elif optional:
                            return ""
                        else:
                            raise Invalid("required")
                    return origin_validator(value)
            else:
                def validator(value):
                    if value is None:
                        if default is not None:
                            return default
                        elif optional:
                            return None
                        else:
                            raise Invalid("required")
                    return origin_validator(value)
            return validator
        return wrapped_validator
    return handler


@handle_default_optional_desc()
def int_validator(min=-sys.maxsize, max=sys.maxsize):
    """Validate int string

    :param min: the min value, default -sys.maxsize
    :param max: the max value, default sys.maxsize
    """
    def validator(value):
        try:
            v = int(value)
        except Exception:
            raise Invalid("invalid int")
        if v < min:
            raise Invalid("value must >= %d" % min)
        elif v > max:
            raise Invalid("value must <= %d" % max)
        return v
    return validator


@handle_default_optional_desc()
def bool_validator():
    """Validate bool"""
    def validator(value):
        if isinstance(value, bool):
            return value
        else:
            raise Invalid("invalid bool")
    return validator


@handle_default_optional_desc()
def float_validator(min=-sys.float_info.max, max=sys.float_info.max,
                    exmin=False, exmax=False):
    """Validate float string

    :param min: the min value, default -sys.float_info.max
    :param max: the max value, default sys.float_info.max
    :param exmin: exclude min value or not, default false
    :param exmax: exclude max value or not, default false
    """
    def validator(value):
        try:
            v = float(value)
        except Exception:
            raise Invalid("invalid float")
        if exmin:
            if v <= min:
                raise Invalid("value must > %d" % min)
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
    return validator


@handle_default_optional_desc(string=True)
def str_validator(minlen=0, maxlen=1024 * 1024, escape=False):
    """Validate string

    :param minlen: min length of string, default 0
    :param maxlen: max length of string, default 1024*1024
    :param escape: escape to safe string or not, default false
    """
    def validator(value):
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
    return validator


@handle_default_optional_desc(string=True)
def date_validator(format="%Y-%m-%d"):
    """Validate date string, convert value to string

    :param format: date format, default ISO8601
    """
    def validator(value):
        try:
            if not isinstance(value, (datetime.datetime, datetime.date)):
                value = datetime.datetime.strptime(value, format)
            return value.strftime(format)
        except Exception:
            raise Invalid("invalid date")
    return validator


@handle_default_optional_desc(string=True)
def time_validator(format="%H:%M:%S"):
    """Validate time string, convert value to string

    :param format: time format, default ISO8601
    """
    def validator(value):
        try:
            if not isinstance(value, (datetime.datetime, datetime.time)):
                value = datetime.datetime.strptime(value, format)
            return value.strftime(format)
        except Exception:
            raise Invalid("invalid time")
    return validator


@handle_default_optional_desc(string=True)
def datetime_validator(format="%Y-%m-%dT%H:%M:%S.%fZ"):
    """Validate datetime string, convert value to string

    :param format: datetime format, default ISO8601
    """
    def validator(value):
        try:
            if not isinstance(value, datetime.datetime):
                value = datetime.datetime.strptime(value, format)
            return value.strftime(format)
        except Exception:
            raise Invalid("invalid datetime")
    return validator


def build_re_validator(name, r):
    """Build validator by regex string

    The regex string will be compiled make sure that the entire string matches

    :param name: validator name, used in error message
    :param r: regex string
    """
    # To make sure that the entire string matches
    r = re.compile(r"(?:%s)\Z" % r)

    @handle_default_optional_desc(string=True)
    def re_validator():
        def validator(value):
            if not isinstance(value, str):
                raise Invalid("value must be string")
            if r.match(value):
                return value
            else:
                raise Invalid("invalid %s" % name)
        return validator
    re_validator.__name__ = name + '_validator'
    return re_validator


"""
email: https://github.com/jzaefferer/jquery-validation/blob/master/src/core.js#L1333
url: https://github.com/jzaefferer/jquery-validation/blob/master/src/core.js#L1349
ipv4: https://segmentfault.com/a/1190000004622152
ipv6: https://github.com/jzaefferer/jquery-validation/blob/master/src/additional/ipv6.js
phone: http://tool.lu/regex/ [modified]
idcard: https://segmentfault.com/a/1190000004622152 [modified]
"""  # noqa
regexs = {
    "email": r"[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",  # noqa
    "url": r"(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})).?)(?::\d{2,5})?(?:[/?#]\S*)?",  # noqa
    "ipv4": r"(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)",  # noqa
    "ipv6": r"((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(([0-9A-Fa-f]{1,4}:){0,5}:((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(::([0-9A-Fa-f]{1,4}:){0,5}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))",  # noqa
    "phone": r"((\+86)|(86))?(13\d|14[57]|15[^4,\D]|17[678]|18\d)\d{8}|170[059]\d{7}",  # noqa
    "idcard": r"\d{17}[\d|x|X]|\d{15}",
}

builtin_validators = {
    "int": int_validator,
    "bool": bool_validator,
    "float": float_validator,
    "str": str_validator,
    "date": date_validator,
    "time": time_validator,
    "datetime": datetime_validator,
}

for name, r in regexs.items():
    builtin_validators[name] = build_re_validator(name, r)
