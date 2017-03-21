import re
import datetime
import sys

from ._exception import Invalid, SchemaError


def validator(bint string=False):
    """Decorator for create validator

    It will handle params default,optional,desc automatically.

    Usage:

        @validator(string=False)
        def xxx_validator(value, args..., kwargs...):
            try:
                return value  # validate/convert the value
            except:
                raise Invalid('invalid xxx')

    Args:
        string (bool): treat empty string as None or not
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            cdef bint optional = kwargs.pop('optional', False)
            default = kwargs.pop('default', None)
            desc = kwargs.pop('desc', None)

            # check arguments mismatch error before do validation
            try:
                f(None, *args, **kwargs)
            except TypeError as ex:
                raise SchemaError(str(ex)) from None
            except:
                pass

            cdef bint has_default
            if string:
                has_default = not (default is None or default == '')
            else:
                has_default = not (default is None)

            # check default value
            if has_default:
                try:
                    f(default, *args, **kwargs)
                except Invalid:
                    msg = 'invalid default value {}'.format(repr(default))
                    raise SchemaError(msg) from None

            # optimize, speedup 5%
            if string:
                def _validator(value):
                    if value is None or value == '':
                        if has_default:
                            return default
                        elif optional:
                            return ''
                        else:
                            raise Invalid('required')
                    return f(value, *args, **kwargs)
            else:
                def _validator(value):
                    if value is None:
                        if has_default:
                            return default
                        elif optional:
                            return None
                        else:
                            raise Invalid('required')
                    return f(value, *args, **kwargs)

            # make friendly validator representation
            params = [repr(x) for x in args]
            if has_default:
                params.extend(['default={}'.format(repr(default))])
            else:
                params.extend(['optional={}'.format(repr(optional))])
            params.extend(['{}={}'.format(k, repr(v)) for k, v in kwargs.items()])
            params = ', '.join(params)
            _validator.__module__ = f.__module__
            _validator.__name__ = '{}({})'.format(f.__name__, params)
            _validator.__qualname__ = '{}({})'.format(f.__qualname__, params)
            _validator.__doc__ = desc
            return _validator
        wrapper.__module__ = f.__module__
        wrapper.__name__ = f.__name__
        wrapper.__qualname__ = f.__qualname__
        wrapper.__doc__ = f.__doc__
        return wrapper
    return decorator


@validator(string=False)
def int_validator(value, min=-sys.maxsize, max=sys.maxsize):
    """Validate int or convert string to int

    Args:
        min (int): the min value, default -sys.maxsize
        max (int): the max value, default sys.maxsize
    """
    try:
        v = int(value)
    except:
        raise Invalid('invalid int') from None
    if v < min:
        raise Invalid('value must >= %d' % min)
    elif v > max:
        raise Invalid('value must <= %d' % max)
    return v


@validator(string=False)
def bool_validator(value):
    """Validate bool"""
    if isinstance(value, bool):
        return value
    else:
        raise Invalid('invalid bool')


@validator(string=False)
def float_validator(value, min=-sys.float_info.max, max=sys.float_info.max,
                    bint exmin=False, bint exmax=False):
    """Validate float string

    Args:
        min (float): the min value, default -sys.float_info.max
        max (float): the max value, default sys.float_info.max
        exmin (bool): exclude min value or not, default false
        exmax (bool): exclude max value or not, default false
    """
    try:
        v = float(value)
    except:
        raise Invalid('invalid float') from None
    if exmin:
        if v <= min:
            raise Invalid('value must > %d' % min)
    else:
        if v < min:
            raise Invalid('value must >= %d' % min)
    if exmax:
        if v >= max:
            raise Invalid('value must < %d' % max)
    else:
        if v > max:
            raise Invalid('value must <= %d' % max)
    return v


@validator(string=True)
def str_validator(value, int minlen=0, int maxlen=1024 * 1024, bint escape=False):
    """Validate string

    Args:
        minlen (int): min length of string, default 0
        maxlen (int): max length of string, default 1024*1024
        escape (bool): escape to safe string or not, default false
    """
    if not isinstance(value, str):
        raise Invalid('invalid string')
    cdef int length = len(value)
    if length < minlen:
        raise Invalid('string length must >= %d' % minlen)
    elif length > maxlen:
        raise Invalid('string length must <= %d' % maxlen)
    if escape:
        return (value.replace('&', '&amp;')
                .replace('>', '&gt;')
                .replace('<', '&lt;')
                .replace("'", '&#39;')
                .replace('"', '&#34;'))
    else:
        return value


@validator(string=True)
def date_validator(value, format='%Y-%m-%d'):
    """Validate date string or convert date to string

    Args:
        format (str): date format, default ISO8601 format
    """
    try:
        if not isinstance(value, (datetime.datetime, datetime.date)):
            value = datetime.datetime.strptime(value, format)
        return value.strftime(format)
    except:
        raise Invalid('invalid date') from None


@validator(string=True)
def time_validator(value, format='%H:%M:%S'):
    """Validate time string or convert time to string

    Args:
        format (str): time format, default ISO8601 format
    """
    try:
        if not isinstance(value, (datetime.datetime, datetime.time)):
            value = datetime.datetime.strptime(value, format)
        return value.strftime(format)
    except:
        raise Invalid('invalid time') from None


@validator(string=True)
def datetime_validator(value, format='%Y-%m-%dT%H:%M:%S.%fZ'):
    """Validate datetime string or convert datetime to string

    Args:
        format (str): datetime format, default ISO8601 format
    """
    try:
        if not isinstance(value, datetime.datetime):
            value = datetime.datetime.strptime(value, format)
        return value.strftime(format)
    except:
        raise Invalid('invalid datetime') from None


def build_re_validator(str name, r):
    """Build validator by regex string

    It will make sure that the entire string matches, so needn't
    add `^`,`$` to regex string.

    Args:
        name (str): validator name, used in error message
        r (str): regex string
    """
    # To make sure that the entire string matches
    match = re.compile(r'(?:%s)\Z' % r).match
    message = 'invalid %s' % name

    def re_validator(value):
        if not isinstance(value, str):
            raise Invalid('value must be string')
        if match(value):
            return value
        else:
            raise Invalid(message)
    re_validator.__name__ = name + '_validator'
    re_validator.__qualname__ = name + '_validator'
    return validator(string=True)(re_validator)


# email: https://github.com/jzaefferer/jquery-validation/blob/master/src/core.js#L1333
# url: https://github.com/jzaefferer/jquery-validation/blob/master/src/core.js#L1349
# ipv4: https://segmentfault.com/a/1190000004622152
# ipv6: https://github.com/jzaefferer/jquery-validation/blob/master/src/additional/ipv6.js
# phone: http://tool.lu/regex/ [modified]
# idcard: https://segmentfault.com/a/1190000004622152 [modified]
regexs = {
    'email': r"[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",  # noqa
    'url': r'(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})).?)(?::\d{2,5})?(?:[/?#]\S*)?',  # noqa
    'ipv4': r'(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)',  # noqa
    'ipv6': r'((([0-9A-Fa-f]{1,4}:){7}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}:[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){5}:([0-9A-Fa-f]{1,4}:)?[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){4}:([0-9A-Fa-f]{1,4}:){0,2}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){3}:([0-9A-Fa-f]{1,4}:){0,3}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){2}:([0-9A-Fa-f]{1,4}:){0,4}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){6}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(([0-9A-Fa-f]{1,4}:){0,5}:((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|(::([0-9A-Fa-f]{1,4}:){0,5}((\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b)\.){3}(\b((25[0-5])|(1\d{2})|(2[0-4]\d)|(\d{1,2}))\b))|([0-9A-Fa-f]{1,4}::([0-9A-Fa-f]{1,4}:){0,5}[0-9A-Fa-f]{1,4})|(::([0-9A-Fa-f]{1,4}:){0,6}[0-9A-Fa-f]{1,4})|(([0-9A-Fa-f]{1,4}:){1,7}:))',  # noqa
    'phone': r'((\+86)|(86))?(13\d|14[57]|15[^4,\D]|17[678]|18\d)\d{8}|170[059]\d{7}',  # noqa
    'idcard': r'\d{17}[\d|x|X]|\d{15}',
}

builtin_validators = {
    'int': int_validator,
    'bool': bool_validator,
    'float': float_validator,
    'str': str_validator,
    'date': date_validator,
    'time': time_validator,
    'datetime': datetime_validator,
}

for name, r in regexs.items():
    builtin_validators[name] = build_re_validator(name, r)
