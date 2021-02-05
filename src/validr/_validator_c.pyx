import re
import sys
import uuid
import time
import datetime
import ipaddress
import typing
from copy import copy
from functools import partial
from urllib.parse import urlparse, urlunparse

from .exception import Invalid, SchemaError, mark_key, mark_index
from ._vendor import durationpy
from ._vendor.email_validator import validate_email, EmailNotValidError
from ._vendor.fqdn import FQDN


cpdef bint is_dict(obj):
    # use isinstance(obj, Mapping) is slow,
    # hasattr check can speed up about 30%
    return hasattr(obj, '__getitem__') and hasattr(obj, 'get')


cpdef inline get_dict_value(obj, str key):
    return obj.get(key, None)


cpdef inline get_object_value(obj, str key):
    return getattr(obj, key, None)


cpdef inline bint _is_empty(value):
    return value is None or value == ''


cpdef _update_validate_func_info(validate_func, origin_func, schema):
    # make friendly validate func representation
    m_repr = schema.repr(prefix=False, desc=False)
    validate_func.__schema__ = schema
    validate_func.__module__ = origin_func.__module__
    validate_func.__name__ = '{}<{}>'.format(origin_func.__name__, m_repr)
    if hasattr(origin_func, '__qualname__'):
        qualname = '{}<{}>'.format(origin_func.__qualname__, m_repr)
        validate_func.__qualname__ = qualname
    if origin_func.__doc__:
        validate_func.__doc__ = origin_func.__doc__
    else:
        validate_func.__doc__ = schema.params.get('desc')


def _parse_hints(hints):
    if not isinstance(hints, (tuple, set, list)):
        hints = [hints]
    is_string = False
    is_object = False
    types = []
    for hint in hints:
        if hint is str:
            is_string = True
        else:
            is_object = True
        if hint is object:
            hint = typing.Any
        types.append(hint)
    return is_string, is_object, tuple(types)


def _update_validate_func_type_hints(
        validate_func,
        optional, has_default,
        accept_hints, output_hints,
):
    assert accept_hints, 'no accept_hints'
    assert output_hints, 'no output_hints'
    if len(accept_hints) == 1:
        value_typing = accept_hints[0]
    else:
        value_typing = typing.Union[accept_hints]
    if optional:
        value_typing = typing.Optional[value_typing]
    if len(output_hints) == 1:
        return_typing = output_hints[0]
    else:
        return_typing = typing.Union[output_hints]
    if optional and not has_default:
        return_typing = typing.Optional[return_typing]
    annotations = {'value': value_typing, 'return': return_typing}
    validate_func.__annotations__ = annotations


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
    if accept is None or not accept:
        accept_string = True
        accept_object = True
        accept_hints = (str, typing.Any)
    else:
        accept_string, accept_object, accept_hints = _parse_hints(accept)
    if not (accept_string or accept_object):
        raise ValueError('invalid accept argument {}'.format(accept))
    if output is None or not output:
        output_string = string
        output_object = not string
        output_hints = (str,) if string else (typing.Any,)
    else:
        output_string, output_object, output_hints = _parse_hints(output)
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
                local_output_object = bool(params.get('object', None))
                # TODO: fix special case of timedelta
                if schema.validator == 'timedelta':
                    local_output_object = not bool(params.get('string', None))
            if output_object and 'object' in params:
                params['output_object'] = bool(params.pop('object', None))
            if local_output_object:
                null_output = None
            else:
                null_output = ''
            cdef bint optional = params.pop('optional', False)
            default = params.pop('default', None)
            params.pop('desc', None)
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

            # check null, empty string and default
            def _m_validate(value):
                cdef bint is_null
                if accept_string:
                    is_null = _is_empty(value)
                else:
                    is_null = value is None
                if is_null:
                    if has_default:
                        return default
                    elif optional:
                        return null_output
                    else:
                        raise Invalid('required')
                if not accept_object and not isinstance(value, str):
                    raise Invalid('require string value')
                value = validate(value)
                # check again after validate
                if accept_string:
                    is_null = _is_empty(value)
                else:
                    is_null = value is None
                if is_null:
                    if has_default:
                        return default
                    elif optional:
                        return null_output
                    else:
                        raise Invalid('required')
                return value

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

            _update_validate_func_info(m_validate, f, schema)

            _update_validate_func_type_hints(
                m_validate, optional=optional, has_default=has_default,
                accept_hints=accept_hints, output_hints=output_hints)

            return m_validate

        def m_validator(compiler, schema):
            try:
                return _m_validator(compiler, schema)
            except SchemaError as ex:
                ex.set_value(schema)
                raise

        # TODO: deprecate below attributes because they are implement details
        m_validator.is_string = output_string
        m_validator.accept_string = accept_string
        m_validator.accept_object = accept_object
        m_validator.output_string = output_string
        m_validator.output_object = output_object
        m_validator.validator = f
        # end deprecate

        m_validator.__module__ = f.__module__
        m_validator.__name__ = f.__name__
        if hasattr(f, '__qualname__'):
            m_validator.__qualname__ = f.__qualname__
        m_validator.__doc__ = f.__doc__
        return m_validator
    return decorator


cpdef str _UNIQUE_CHECK_ERROR_MESSAGE = "unable to check unique for non-hashable types"


cpdef inline _key_of_scalar(v):
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


@validator(accept=typing.Iterable, output=typing.List)
def list_validator(compiler, items=None, int minlen=0, int maxlen=1024,
                   bint unique=False):
    if items is None:
        inner = None
    else:
        with mark_index():
            inner = compiler.compile(items)
    if unique:
        key_of = _key_func_of_schema(items)
    del compiler, items

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
        if minlen > 0 and i + 1 < minlen:
            raise Invalid('list length must >= %d' % minlen)
        return result
    return validate


cpdef inline dict _slim_dict(dict value):
    return {k: v for k, v in value.items() if not _is_empty(v)}


@validator(accept=(typing.Mapping, typing.Any), output=dict)
def dict_validator(compiler, items=None, key=None, value=None,
                   int minlen=0, int maxlen=1024, bint slim=False):
    if items is None:
        inners = None
    else:
        inners = []
        for k, v in items.items():
            with mark_key(k):
                inners.append((k, compiler.compile(v)))
    validate_extra_key = validate_extra_value = None
    if key is not None:
        with mark_key('$self_key'):
            validate_extra_key = compiler.compile(key)
    if value is not None:
        with mark_key('$self_value'):
            validate_extra_value = compiler.compile(value)
    cdef bint is_dynamic
    is_dynamic = bool(validate_extra_key or validate_extra_value)
    del compiler, items, key, value

    def validate(value):
        if inners is None and not is_dynamic:
            if not is_dict(value):
                raise Invalid('must be dict')
            if len(value) > maxlen:
                raise Invalid('dict length must <= %d' % maxlen)
            elif minlen > 0 and len(value) < minlen:
                raise Invalid('dict length must >= %d' % minlen)
            if slim:
                value = _slim_dict(value)
            return copy(value)
        if is_dict(value):
            getter = get_dict_value
            if is_dynamic:
                if len(value) > maxlen:
                    raise Invalid('dict length must <= %d' % maxlen)
                elif minlen > 0 and len(value) < minlen:
                    raise Invalid('dict length must >= %d' % minlen)
        else:
            getter = get_object_value
            if is_dynamic:
                raise Invalid("dynamic dict not allowed non-dict value")
        result = {}
        cdef str k
        if inners is not None:
            for k, inner in inners:
                with mark_key(k):
                    result[k] = inner(getter(value, k))
        if is_dynamic:
            extra_keys = map(str, set(value) - set(result))
            for k in extra_keys:
                if validate_extra_key:
                    with mark_key('$self_key'):
                        k = str(validate_extra_key(k))
                with mark_key(k):
                    v = getter(value, k)
                    if validate_extra_value is not None:
                        result[k] = validate_extra_value(v)
                    else:
                        result[k] = copy(v)
        if slim:
            result = _slim_dict(result)
        return result
    return validate


@validator(accept=(typing.Mapping, typing.Any), output=object)
def model_validator(compiler, items=None):
    if items is None:
        raise SchemaError('model class not provided')

    def validate(value):
        return items(value)

    return validate


cpdef _dump_enum_value(value):
    if value is None:
        return 'null'
    elif value is False:
        return 'false'
    elif value is True:
        return 'true'
    elif isinstance(value, str):
        return repr(value)  # single quotes by default
    else:
        return str(value)  # number


@validator(output=object)
def enum_validator(compiler, items):
    if not items:
        raise SchemaError("enum items not provided")
    expects = '{' + ', '.join(map(_dump_enum_value, items)) + '}'
    items = frozenset(items)

    def validate(value):
        if value in items:
            return value
        raise Invalid("expect one of {}".format(expects))

    return validate


cpdef union_validator(compiler, schema):
    if not schema.items:
        raise SchemaError('union schemas not provided')
    default = schema.params.get('default')
    if default is not None:
        raise SchemaError("not allowed default for union schema")
    by = schema.params.get('by')
    if isinstance(schema.items, list):
        if by is not None:
            raise SchemaError("not allowed 'by' argument for union list schema")
        return _union_list_validator(compiler, schema)
    elif isinstance(schema.items, dict):
        if by is None or by == "":
            raise SchemaError("required 'by' argument for union dict schema")
        if not isinstance(by, str):
            raise SchemaError("'by' argument must be str type for union schema")
        return _union_dict_validator(compiler, schema)
    else:
        raise SchemaError('union schemas type invalid')


cpdef _optional_or_has_default(schema):
    if schema.params.get('optional'):
        return True
    if schema.params.get('default') is not None:
        return True
    return False


def _union_list_validator(compiler, schema):
    scalar_inner = None
    list_inner = None
    dict_inner = None
    for i, inner_schema in enumerate(schema.items):
        with mark_index(i):
            if inner_schema.validator == 'union':
                raise SchemaError('ambiguous union schema')
            if _optional_or_has_default(inner_schema):
                raise SchemaError('not allowed optional or default for union schemas')
            if schema.params.get('optional'):
                inner_schema = inner_schema.copy()
                inner_schema.params['optional'] = True
            if inner_schema.validator == 'list':
                if list_inner is not None:
                    raise SchemaError('ambiguous union schema')
                list_inner = compiler.compile(inner_schema)
            elif inner_schema.validator in ('dict', 'model'):
                if dict_inner is not None:
                    raise SchemaError('ambiguous union schema')
                dict_inner = compiler.compile(inner_schema)
            else:
                if scalar_inner is not None:
                    raise SchemaError('ambiguous union schema')
                scalar_inner = compiler.compile(inner_schema)

    def validate(value):
        if isinstance(value, list):
            if list_inner is None:
                raise Invalid('not allowed list')
            return list_inner(value)
        elif is_dict(value) or hasattr(value, '__asdict__'):
            if dict_inner is None:
                raise Invalid('not allowed dict')
            return dict_inner(value)
        elif value is None:
            return (scalar_inner or list_inner or dict_inner)(value)
        else:
            if scalar_inner is None:
                raise Invalid('not allowed scalar value')
            return scalar_inner(value)

    _update_validate_func_info(validate, union_validator, schema)

    return validate


@validator(accept=object, output=object)
def _union_dict_validator(compiler, items, str by):
    inners = {}
    for key, schema in items.items():
        with mark_key(key):
            if schema.validator not in ('dict', 'model'):
                raise SchemaError('must be dict or model schema')
            if _optional_or_has_default(schema):
                raise SchemaError('not allowed optional or default for union schemas')
            is_model = schema.validator == 'model'
            inners[key] = (is_model, compiler.compile(schema))
    expect_bys = '{' + ', '.join(sorted(inners.keys())) + '}'
    del key, schema, is_model

    def validate(value):
        if is_dict(value):
            getter = get_dict_value
        else:
            getter = get_object_value
        cdef str by_name
        with mark_key(by):
            by_name = getter(value, by)
            if not by_name:
                raise Invalid('required', value=by_name)
            inner_info = inners.get(by_name)
            if inner_info is None:
                err_msg = 'expect one of {}'.format(expect_bys)
                raise Invalid(err_msg, value=by_name)
        is_model, inner = inner_info
        result = inner(value)
        if not is_model:
            result[by] = by_name
        return result

    return validate


cpdef any_validate(value):
    return copy(value)


@validator(accept=object, output=object)
def any_validator(compiler, **ignore_kwargs):
    """Accept any value"""
    return any_validate


@validator(accept=(int, float, str), output=int)
def int_validator(compiler, min=-sys.maxsize, max=sys.maxsize):
    """Validate int or convert string to int

    Args:
        min (int): the min value, default -sys.maxsize
        max (int): the max value, default sys.maxsize
    """
    min, max = int(min), int(max)

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


@validator(accept=(bool, int, str), output=bool)
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


@validator(accept=(int, float, str), output=float)
def float_validator(compiler, min=-sys.float_info.max, max=sys.float_info.max,
                    exmin=False, exmax=False):
    """Validate float string

    Args:
        min (float): the min value, default -sys.float_info.max
        max (float): the max value, default sys.float_info.max
        exmin (bool,float): exclude min value or not, default false
        exmax (bool,float): exclude max value or not, default false
    """
    min, max = float(min), float(max)
    if isinstance(exmin, (int, float)) and not isinstance(exmin, bool):
        min = float(exmin)
        exmin = True
    else:
        exmin = bool(exmin)
    if isinstance(exmax, (int, float)) and not isinstance(exmax, bool):
        max = float(exmax)
        exmax = True
    else:
        exmax = bool(exmax)

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


@validator(accept=(str, object), output=str)
def str_validator(compiler, int minlen=0, int maxlen=1024 * 1024,
                  bint strip=False, bint escape=False, str match=None,
                  bint accept_object=False):
    """Validate string

    Args:
        minlen (int): min length of string, default 0
        maxlen (int): max length of string, default 1024*1024
        strip (bool): strip white space or not, default false
        escape (bool): escape to html safe string or not, default false
        match (str): regex to match, default None
    """

    # To make sure that the entire string matches
    if match:
        try:
            re_match = re.compile(r'(?:%s)\Z' % match).match
        except Exception as ex:
            raise SchemaError('match regex %s compile failed' % match) from ex
    else:
        re_match = None

    def validate(value):
        if not isinstance(value, str):
            if accept_object or isinstance(value, int):
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
            value = (value.replace('&', '&amp;')
                     .replace('>', '&gt;')
                     .replace('<', '&lt;')
                     .replace("'", '&#39;')
                     .replace('"', '&#34;'))
        if re_match is not None and not re_match(value):
            raise Invalid("string not match regex %s" % match)
        return value
    return validate


@validator(accept=bytes, output=bytes)
def bytes_validator(compiler, int minlen=0, int maxlen=-1):
    """Validate bytes

    Args:
        minlen (int): min length of bytes, default 0
        maxlen (int): max length of bytes, default unlimited
    """

    def validate(value):
        if not isinstance(value, bytes):
            raise Invalid('invalid bytes')
        cdef int length = len(value)
        if length < minlen:
            raise Invalid('bytes length must >= %d' % minlen)
        elif maxlen > -1 and length > maxlen:
            raise Invalid('bytes length must <= %d' % maxlen)
        return value

    return validate


@validator(accept=(str, datetime.date), output=(str, datetime.date))
def date_validator(compiler, str format='%Y-%m-%d', bint output_object=False):
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


@validator(accept=(str, datetime.time), output=(str, datetime.time))
def time_validator(compiler, str format='%H:%M:%S', bint output_object=False):
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


@validator(accept=(str, datetime.datetime), output=(str, datetime.datetime))
def datetime_validator(compiler, str format='%Y-%m-%dT%H:%M:%S.%fZ', bint output_object=False):
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


cpdef _parse_timedelta(value):
    if isinstance(value, (int, float)):
        value = datetime.timedelta(seconds=value)
    elif isinstance(value, str):
        value = durationpy.from_str(value)
    else:
        if not isinstance(value, datetime.timedelta):
            raise ValueError("invalid timedelta")
    return value


@validator(accept=(int, float, str, datetime.timedelta), output=(str, float, datetime.timedelta))
def timedelta_validator(compiler, min=None, max=None, bint string=False,
                        bint extended=False, bint output_object=False):
    """Validate timedelta string or convert timedelta to string

    Format (Go's Duration strings):
        ns - nanoseconds
        us - microseconds
        ms - milliseconds
        s - seconds
        m - minutes
        h - hours
        d - days
        mo - months
        y - years
    """
    if string and output_object:
        raise SchemaError('can not output both string and object')
    try:
        min_value = _parse_timedelta(min) if min is not None else None
    except (durationpy.DurationError, ValueError, TypeError) as ex:
        raise SchemaError('invalid min timedelta') from ex
    try:
        max_value = _parse_timedelta(max) if max is not None else None
    except (durationpy.DurationError, ValueError, TypeError) as ex:
        raise SchemaError('invalid max timedelta') from ex
    del min, max
    min_repr = max_repr = None
    if min_value is not None:
        min_repr = durationpy.to_str(min_value, extended=True)
    if max_value is not None:
        max_repr = durationpy.to_str(max_value, extended=True)

    def validate(value):
        try:
            value = _parse_timedelta(value)
        except (durationpy.DurationError, ValueError, TypeError) as ex:
            raise Invalid('invalid timedelta') from ex
        if min_value is not None:
            if value < min_value:
                raise Invalid('value must >= {}'.format(min_repr))
        if max_value is not None:
            if value > max_value:
                raise Invalid('value must <= {}'.format(max_repr))
        if output_object:
            return value
        if string:
            value = durationpy.to_str(value, extended=extended)
        else:
            value = value.total_seconds()
        return value
    return validate


@validator(accept=(str, ipaddress.IPv4Address), output=(str, ipaddress.IPv4Address))
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


@validator(accept=(str, ipaddress.IPv6Address), output=(str, ipaddress.IPv6Address))
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
def url_validator(compiler, str scheme='http https', int maxlen=255, bint output_object=False):
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


@validator(output=str)
def fqdn_validator(compiler):
    def validate(value):
        try:
            value = value.strip()
            fqdn_obj = FQDN(value)
            if fqdn_obj.is_valid:
                return fqdn_obj.relative
        except (ValueError, TypeError, AttributeError) as ex:
            raise Invalid("invalid fqdn") from ex
        raise Invalid("invalid fqdn")
    return validate


@validator(output=(str, uuid.UUID))
def uuid_validator(compiler, version=None, bint output_object=False):
    if version is None:
        msg = 'invalid uuid'
    else:
        if version not in {1, 3, 4, 5}:
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


def create_re_validator(str name, str r, int default_maxlen=255):
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

    def re_validator(compiler, int minlen=0, int maxlen=default_maxlen, bint strip=False):
        def validate(value):
            if not isinstance(value, str):
                raise Invalid('value must be string')
            if strip:
                value = value.strip()
            cdef int length = len(value)
            if length < minlen:
                raise Invalid('%s length must >= %d' % (name, minlen))
            elif length > maxlen:
                raise Invalid('%s length must <= %d' % (name, maxlen))
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
    'model': model_validator,
    'union': union_validator,
    'enum': enum_validator,
    'any': any_validator,
    'int': int_validator,
    'bool': bool_validator,
    'float': float_validator,
    'str': str_validator,
    'bytes': bytes_validator,
    'date': date_validator,
    'time': time_validator,
    'datetime': datetime_validator,
    'timedelta': timedelta_validator,
    'ipv4': ipv4_validator,
    'ipv6': ipv6_validator,
    'email': email_validator,
    'url': url_validator,
    'fqdn': fqdn_validator,
    'uuid': uuid_validator,
}

regexs = {
    'phone': (r'((\+\d{2}\s?)|(\d{2}\s?))?1\d{10}', 15),
    'idcard': (r'(\d{17}[\d|x|X])|(\d{15})', 18),
    'slug': (r'[a-z0-9]+(?:-[a-z0-9]+)*', 255),
}
for name, options in regexs.items():
    builtin_validators[name] = create_re_validator(name, *options)


def create_enum_validator(str name, items, bint string=True):
    """Create validator by enum items

    Args:
        name (str): validator name, used in error message
        items (iterable): enum items
        string (bool): is string like or not

    Deprecated since v1.2.0, use enum validator instead.
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
