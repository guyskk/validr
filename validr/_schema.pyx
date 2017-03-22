from ._exception import ValidrError, Invalid, mark_index, mark_key


def _update_wrapper(f):
    def wrapper(__, *args, desc=None, **kwargs):
        kwargs.setdefault('optional', False)
        _validator = f(__, *args, **kwargs)
        params = [repr(x) for x in args]
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


cdef _value_is_none_and_optional(value, bint optional):
    if value is None:
        if optional:
            return True
        else:
            raise Invalid('required')
    return False


@_update_wrapper
def list_validator(inner, int minlen=0, int maxlen=1024,
                   bint unique=False, bint optional=False):
    def _validator(value):
        if _value_is_none_and_optional(value, optional):
            return None
        try:
            value = enumerate(value)
        except TypeError:
            raise Invalid('not list')
        result = []
        cdef int i = -1
        for i, x in value:
            if i >= maxlen:
                raise Invalid('list length must <= %d' % maxlen)
            with mark_index(i):
                v = inner(x)
                if unique and v in result:
                    raise Invalid('not unique')
            result.append(v)
        if i + 1 < minlen:
            raise Invalid('list length must >= %d' % minlen)
        return result
    return _validator


@_update_wrapper
def merged_validator(list validators, bint optional=False):
    def _validator(value):
        if _value_is_none_and_optional(value, optional):
            return None
        result = {}
        for v in validators:
            result.update(v(value))
        return result
    return _validator


@_update_wrapper
def dict_validator(list inners, bint optional=False):
    def _validator(value):
        if _value_is_none_and_optional(value, optional):
            return None
        # use dict instead of Mapping can speed up about 30%
        # so use dict until someone meet problems and need Mapping
        if isinstance(value, dict):
            get_item = _get_dict_value
        else:
            get_item = _get_object_value
        result = {}
        cdef str k
        for k, inner in inners:
            with mark_key(k):
                result[k] = inner(get_item(value, k))
        return result
    return _validator


cdef _get_dict_value(obj, str key):
    return obj.get(key, None)


cdef _get_object_value(obj, str key):
    return getattr(obj, key, None)
