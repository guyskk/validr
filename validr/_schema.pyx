from ._exception import ValidrError, Invalid, mark_index, mark_key
from ._validator import validator


@validator(string=False)
def merged_validator(value, list validators):
    result = {}
    for v in validators:
        result.update(v(value))
    return result


@validator(string=False)
def dict_validator(value, list inners):
    # use dict instead of Mapping can speed up about 30%
    # so use dict until someone meet problems and need Mapping
    if isinstance(value, dict):
        get_item = get_dict_value
    else:
        get_item = get_object_value
    result = {}
    cdef str k
    for k, inner in inners:
        with mark_key(k):
            result[k] = inner(get_item(value, k))
    return result


@validator(string=False)
def list_validator(value, inner, int minlen=0, int maxlen=1024, bint unique=False):
    try:
        value = enumerate(value)
    except TypeError:
        raise Invalid("not list")
    result = []
    cdef int i = -1
    for i, x in value:
        if i >= maxlen:
            raise Invalid("list length must <= %d" % maxlen)
        with mark_index(i):
            v = inner(x)
            if unique and v in result:
                raise Invalid("not unique")
        result.append(v)
    if i + 1 < minlen:
        raise Invalid("list length must >= %d" % minlen)
    return result


cdef get_dict_value(obj, str key):
    return obj.get(key, None)


cdef get_object_value(obj, str key):
    return getattr(obj, key, None)
