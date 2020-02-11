import re
import sys
import uuid
import time
import datetime
import ipaddress
from copy import copy
from functools import partial
from urllib.parse import urlparse, urlunparse
from email_validator import validate_email, EmailNotValidError

from .exception import Invalid, SchemaError, mark_key, mark_index


cpdef is_dict(obj):
    # use isinstance(obj, Mapping) is slow,
    # hasattr check can speed up about 30%
    return hasattr(obj, '__getitem__') and hasattr(obj, 'get')


cpdef get_dict_value(obj, str key):
    return obj.get(key, None)


cpdef get_object_value(obj, str key):
    return getattr(obj, key, None)


def validator(string=None, *, accept=None, output=None):
    """Decorator for create validator

    It will handle params default,optional,desc automatically.

    Usage:

        @validator(accept=(str,object), output=(str, object))
        def xxx_validator(compiler, output_object, **params):
            def validate(value):
                try:
                    # validate/convert the value
                except Exception:
                    # raise Invalid('invalid xxx')
                if output_object:
                    # return python object
                else:
                    # return string
            return validate

    Args:
        accept (str | object | (str,object)):
            str: the validator accept only string, treat both None and empty string as None
            object: the validator accept only object
            (str,object): (default) the validator accept both string and object,
                treat both None and empty string as None
        output (str | object | (str,object)):
            str: (default) the validator always output string, convert None to empty string
            object: the validator always output object
            (str, object): the validator can output both string and object,
                and has an `object` parameter to control which to output
        string (bool): deprecated in v1.1.0.
            string=True equal to accept=(str, object), output=str
            string=False equal to accept=(str, object), output=object
    """
    cdef bint accept_string, accept_object, output_string, output_object
    if isinstance(accept, (tuple, set, list)):
        accept_string = str in accept
        accept_object = object in accept
    elif accept is not None:
        accept_string = str is accept
        accept_object = object is accept
    else:
        accept_string = True
        accept_object = True
    if not (accept_string or accept_object):
        raise ValueError('invalid accept argument {}'.format(accept))
    if isinstance(output, (tuple, set, list)):
        output_string = str in output
        output_object = object in output
    elif output is not None:
        output_string = str is output
        output_object = object is output
    else:
        output_string = string
        output_object = not string
    if not (output_string or output_object):
        raise ValueError('invalid output argument {}'.format(output))
    del string, accept, output

    def decorator(f):

        def _m_validator(compiler, schema):
            params = schema.params.copy()
            if schema.items is not None:
                params['items'] = schema.items
            cdef bint local_output_object = output_object
            if output_string and output_object:
                local_output_object = bool(params.pop('object', None))
                params['output_object'] = local_output_object
            if local_output_object:
                null_output = None
            else:
                null_output = ''
            cdef bint optional = params.pop('optional', False)
            default = params.pop('default', None)
            desc = params.pop('desc', None)
            cdef bint invalid_to_default = params.pop('invalid_to_default', False)
            cdef bint has_invalid_to = 'invalid_to' in params
            invalid_to = params.pop('invalid_to', None)
            cdef bint has_default
            if accept_string:
                has_default = not (default is None or default == '')
            else:
                has_default = not (default is None)
            if has_invalid_to and invalid_to_default:
                raise SchemaError('can not set both invalid_to and invalid_to_default')
            if invalid_to_default and (not has_default) and (not optional):
                raise SchemaError('default or optional must be set when set invalid_to_default')
            try:
                validate = f(compiler, **params)
            except TypeError as e:
                raise SchemaError(str(e)) from None
            # check default value
            if has_default:
                try:
                    default = validate(default)
                except Invalid:
                    msg = 'invalid default value {!r}'.format(default)
                    raise SchemaError(msg) from None
                if invalid_to_default:
                    invalid_to = default
            else:
                if invalid_to_default:
                    invalid_to = null_output
            # check invalid_to value
            if has_invalid_to:
                try:
                    invalid_to = validate(invalid_to)
                except Invalid:
                    msg = 'invalid invalid_to value {!r}'.format(invalid_to)
                    raise SchemaError(msg) from None

            # optimize, speedup 15%
            if accept_string:
                def _m_validate(value):
                    if value is None or value == '':
                        if has_default:
                            return default
                        elif optional:
                            return null_output
                        else:
                            raise Invalid('required')
                    if not accept_object and not isinstance(value, str):
                        raise Invalid('require string value')
                    return validate(value)
            else:
                def _m_validate(value):
                    if value is None:
                        if has_default:
                            return default
                        elif optional:
                            return null_output
                        else:
                            raise Invalid('required')
                    return validate(value)

            supress_invalid = has_invalid_to or invalid_to_default

            def m_validate(value):
                try:
                    return _m_validate(value)
                except Invalid as ex:
                    ex.set_value(value)
                    if supress_invalid:
                        return invalid_to
                    else:
                        raise

            # make friendly validate func representation
            m_repr = schema.repr(prefix=False, desc=False)
            m_validate.__schema__ = schema
            m_validate.__module__ = f.__module__
            m_validate.__name__ = '{}<{}>'.format(f.__name__, m_repr)
            if hasattr(f, '__qualname__'):
                m_validate.__qualname__ = '{}<{}>'.format(f.__qualname__, m_repr)
            m_validate.__doc__ = f.__doc__ if f.__doc__ else desc
            return m_validate

        def m_validator(compiler, schema):
            try:
                return _m_validator(compiler, schema)
            except SchemaError as ex:
                ex.set_value(schema)
                raise

        m_validator.is_string = output_string
        m_validator.accept_string = accept_string
        m_validator.accept_object = accept_object
        m_validator.output_string = output_string
        m_validator.output_object = output_object
        m_validator.validator = f
        m_validator.__module__ = f.__module__
        m_validator.__name__ = f.__name__
        if hasattr(f, '__qualname__'):
            m_validator.__qualname__ = f.__qualname__
        m_validator.__doc__ = f.__doc__
        return m_validator
    return decorator


cdef str _UNIQUE_CHECK_ERROR_MESSAGE = "unable to check unique for non-hashable types"


cdef _key_of_scalar(v):
    return v


def _key_func_of_schema(schema):
    if schema is None:
        raise SchemaError(_UNIQUE_CHECK_ERROR_MESSAGE)

    if schema.validator == 'dict':
        if schema.items is None:
            raise SchemaError(_UNIQUE_CHECK_ERROR_MESSAGE)
        keys = []
        for k, v in schema.items.items():
            keys.append((k, _key_func_of_schema(v)))

        def key_of(dict v):
            cdef str k
            return tuple(key_of_value(v[k]) for k, key_of_value in keys)

    elif schema.validator == 'list':
        if schema.items is None:
            raise SchemaError(_UNIQUE_CHECK_ERROR_MESSAGE)
        key_of_value = _key_func_of_schema(schema.items)

        def key_of(list v):
            return tuple(key_of_value(x) for x in v)

    else:
        key_of = _key_of_scalar

    return key_of


@validator(accept=object, output=object)
def list_validator(compiler, items=None, int minlen=0, int maxlen=1024,
                   bint unique=False, bint optional=False):
    if items is None:
        inner = None
    else:
        with mark_index():
            inner = compiler.compile(items)
    if unique:
        key_of = _key_func_of_schema(items)

    def validate(value):
        try:
            value = enumerate(value)
        except TypeError:
            raise Invalid('not list')
        result = []
        if unique:
            keys = set()
        cdef int i = -1
        for i, x in value:
            if i >= maxlen:
                raise Invalid('list length must <= %d' % maxlen)
            with mark_index(i):
                v = inner(x) if inner is not None else copy(x)
                if unique:
                    k = key_of(v)
                    if k in keys:
                        raise Invalid('not unique')
                    keys.add(k)
            result.append(v)
        if i + 1 < minlen:
            raise Invalid('list length must >= %d' % minlen)
        return result
    return validate


@validator(accept=object, output=object)
def dict_validator(compiler, items=None, bint optional=False):
    if items is None:
        inners = None
    else:
        inners = []
        for k, v in items.items():
            with mark_key(k):
                inners.append((k, compiler.compile(v)))

    def validate(value):
        if inners is None:
            if not is_dict(value):
                raise Invalid('must be dict')
            return copy(value)
        if is_dict(value):
            getter = get_dict_value
        else:
            getter = get_object_value
        result = {}
        cdef str k
        for k, inner in inners:
            with mark_key(k):
                result[k] = inner(getter(value, k))
        return result
    return validate


cpdef any_validate(value):
    return copy(value)


@validator(accept=object, output=object)
def any_validator(compiler, **ignore_kwargs):
    """Accept any value"""
    return any_validate


@validator(output=object)
def int_validator(compiler, min=-sys.maxsize, max=sys.maxsize):
    """Validate int or convert string to int

    Args:
        min (int): the min value, default -sys.maxsize
        max (int): the max value, default sys.maxsize
    """
    def validate(value):
        try:
            v = int(value)
        except Exception:
            raise Invalid('invalid int') from None
        if v < min:
            raise Invalid('value must >= %d' % min)
        elif v > max:
            raise Invalid('value must <= %d' % max)
        return v
    return validate


_TRUE_VALUES = {
    True, 1, '1',
    'True', 'true', 'TRUE',
    'Yes', 'yes', 'YES', 'y', 'Y',
    'On', 'on', 'ON',
}
_FALSE_VALUES = {
    False, 0, '0',
    'False', 'false', 'FALSE',
    'No', 'no', 'NO', 'n', 'N',
    'Off', 'off', 'OFF',
}


@validator(output=object)
def bool_validator(compiler):
    """Validate bool"""
    def validate(value):
        if value in _TRUE_VALUES:
            return True
        elif value in _FALSE_VALUES:
            return False
        else:
            raise Invalid('invalid bool')
    return validate


@validator(output=object)
def float_validator(compiler, min=-sys.float_info.max, max=sys.float_info.max,
                    bint exmin=False, bint exmax=False):
    """Validate float string

    Args:
        min (float): the min value, default -sys.float_info.max
        max (float): the max value, default sys.float_info.max
        exmin (bool): exclude min value or not, default false
        exmax (bool): exclude max value or not, default false
    """
    def validate(value):
        try:
            v = float(value)
        except Exception:
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
    return validate


@validator(output=str)
def str_validator(compiler, int minlen=0, int maxlen=1024 * 1024,
                  bint strip=False, bint escape=False, bint accept_object=False):
    """Validate string

    Args:
        minlen (int): min length of string, default 0
        maxlen (int): max length of string, default 1024*1024
        escape (bool): escape to html safe string or not, default false
    """
    def validate(value):
        if not isinstance(value, str):
            if accept_object:
                value = str(value)
            else:
                raise Invalid('invalid string')
        if strip:
            value = value.strip()
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
    return validate


@validator(output=(str, object))
def date_validator(compiler, format='%Y-%m-%d', bint output_object=False):
    """Validate date string or convert date to string

    Args:
        format (str): date format, default ISO8601 format
    """
    def validate(value):
        try:
            if not isinstance(value, (datetime.datetime, datetime.date)):
                value = datetime.datetime.strptime(value, format)
            if isinstance(value, datetime.datetime):
                value = value.date()
            if output_object:
                return value
            else:
                return value.strftime(format)
        except Exception:
            raise Invalid('invalid date') from None
    return validate


@validator(output=(str, object))
def time_validator(compiler, format='%H:%M:%S', bint output_object=False):
    """Validate time string or convert time to string

    Args:
        format (str): time format, default ISO8601 format
    """
    def validate(value):
        try:
            if not isinstance(value, (datetime.datetime, datetime.time)):
                value = datetime.datetime.strptime(value, format)
            if isinstance(value, datetime.datetime):
                value = value.time()
            if output_object:
                return value
            else:
                return value.strftime(format)
        except Exception:
            raise Invalid('invalid time') from None
    return validate


@validator(output=(str, object))
def datetime_validator(compiler, format='%Y-%m-%dT%H:%M:%S.%fZ', bint output_object=False):
    """Validate datetime string or convert datetime to string

    Args:
        format (str): datetime format, default ISO8601 format
    """
    def validate(value):
        try:
            if isinstance(value, tuple):
                value = datetime.datetime.fromtimestamp(time.mktime(value))
            elif not isinstance(value, datetime.datetime):
                value = datetime.datetime.strptime(value, format)
            if output_object:
                return value
            else:
                return value.strftime(format)
        except Exception:
            raise Invalid('invalid datetime') from None
    return validate


@validator(output=(str, object))
def ipv4_validator(compiler, bint output_object=False):
    def validate(value):
        try:
            value = ipaddress.IPv4Address(value.strip())
        except ipaddress.AddressValueError as ex:
            raise Invalid(str(ex)) from None
        except Exception:
            raise Invalid('invalid ipv4 address') from None
        if output_object:
            return value
        else:
            return value.compressed
    return validate


@validator(output=(str, object))
def ipv6_validator(compiler, bint output_object=False):
    def validate(value):
        try:
            value = ipaddress.IPv6Address(value.strip())
        except ipaddress.AddressValueError as ex:
            raise Invalid(str(ex)) from None
        except Exception:
            raise Invalid('invalid ipv6 address') from None
        if output_object:
            return value
        else:
            return value.compressed
    return validate


@validator(accept=str, output=str)
def email_validator(compiler):
    # https://stackoverflow.com/questions/201323/using-a-regular-expression-to-validate-an-email-address
    # http://emailregex.com/
    # https://github.com/JoshData/python-email-validator
    _validate = partial(
        validate_email,
        allow_smtputf8=False,
        check_deliverability=False,
        allow_empty_local=False,
    )

    def validate(value):
        try:
            value = _validate(value.strip())
        except EmailNotValidError as ex:
            raise Invalid(str(ex)) from None
        except Exception:
            raise Invalid('invalid email address') from None
        return value['email']
    return validate


@validator(output=(str, object))
def url_validator(compiler, scheme='http https', maxlen=256, bint output_object=False):
    # https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    # https://stackoverflow.com/questions/827557/how-do-you-validate-a-url-with-a-regular-expression-in-python
    # https://github.com/python-hyper/rfc3986
    # https://github.com/dgerber/rfc3987
    # https://github.com/tkem/uritools
    allow_scheme = set(scheme.split())

    def validate(value):
        try:
            value = value.strip()
        except Exception:
            raise Invalid('invalid url') from None
        if len(value) > maxlen:
            raise Invalid('url length must <= {}'.format(maxlen))
        try:
            parsed = urlparse(value)
        except Exception:
            raise Invalid('invalid url') from None
        if not parsed.scheme or parsed.scheme not in allow_scheme:
            raise Invalid('invalid url scheme, expect {}'.format(allow_scheme))
        if output_object:
            return parsed
        else:
            return urlunparse(parsed)
    return validate


@validator(output=(str, object))
def uuid_validator(compiler, version=None, bint output_object=False):
    if version is None:
        msg = 'invalid uuid'
    else:
        if not 1 <= version <= 5:
            raise SchemaError('illegal version number')
        msg = 'invalid uuid{}'.format(version)

    def validate(value):
        if not isinstance(value, uuid.UUID):
            try:
                value = uuid.UUID(value.strip())
            except Exception:
                raise Invalid(msg) from None
        if version is not None and value.version != version:
            raise Invalid(msg)
        if output_object:
            return value
        else:
            return str(value)
    return validate


def create_re_validator(str name, r):
    """Create validator by regex string

    It will make sure that the entire string matches, so needn't
    add `^`,`$` to regex string.

    Args:
        name (str): validator name, used in error message
        r (str): regex string
    """
    # To make sure that the entire string matches
    match = re.compile(r'(?:%s)\Z' % r).match
    message = 'invalid %s' % name

    def re_validator(compiler):
        def validate(value):
            if not isinstance(value, str):
                raise Invalid('value must be string')
            if match(value):
                return value
            else:
                raise Invalid(message)
        return validate
    re_validator.__name__ = name + '_validator'
    re_validator.__qualname__ = name + '_validator'
    return validator(accept=str, output=str)(re_validator)


builtin_validators = {
    'list': list_validator,
    'dict': dict_validator,
    'any': any_validator,
    'int': int_validator,
    'bool': bool_validator,
    'float': float_validator,
    'str': str_validator,
    'date': date_validator,
    'time': time_validator,
    'datetime': datetime_validator,
    'ipv4': ipv4_validator,
    'ipv6': ipv6_validator,
    'email': email_validator,
    'url': url_validator,
    'uuid': uuid_validator,
}

regexs = {
    'phone': r'((\+86)|(86))?1\d{10}',
    'idcard': r'(\d{17}[\d|x|X])|(\d{15})',
}
for name, r in regexs.items():
    builtin_validators[name] = create_re_validator(name, r)


def create_enum_validator(str name, items, string=True):
    """Create validator by enum items

    Args:
        name (str): validator name, used in error message
        items (iterable): enum items
        string (bool): is string like or not
    """
    items = set(items)
    message = 'invalid {}, expect one of {}'.format(name, list(sorted(items)))

    def enum_validator(compiler):
        def validate(value):
            if value in items:
                return value
            raise Invalid(message)
        return validate
    enum_validator.__name__ = name + '_validator'
    enum_validator.__qualname__ = name + '_validator'
    if string:
        return validator(accept=str, output=str)(enum_validator)
    else:
        return validator(accept=object, output=object)(enum_validator)
