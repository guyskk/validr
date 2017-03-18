from ._exception import ValidrError, Invalid, SchemaError, MarkIndex, MarkKey


def merge_validators(list validators, bint optional=False, str desc=None):
    def merged_validator(value):
        if check_optional(value, optional):
            return None
        result = {}
        for v in validators:
            result.update(v(value))
        return result
    return merged_validator


def dict_validator(inners, bint optional=False, str desc=None):

    inners = list(inners.items())

    def validate_dict(value):
        if check_optional(value, optional):
            return None
        # use dict instead of Mapping can speed up about 30%
        # so use dict until someone meet problems and need Mapping
        if isinstance(value, dict):
            get_item = get_dict_value
        else:
            get_item = get_object_value
        result = {}
        cdef str k
        for k, inner in inners:
            with MarkKey(k):
                result[k] = inner(get_item(value, k))
        return result
    return validate_dict

def list_validator(inner, int minlen=0, int maxlen=1024, bint unique=False,
                   bint optional=False, str desc=None):
    def validate_list(value):
        if check_optional(value, optional):
            return None
        try:
            value = enumerate(value)
        except TypeError:
            raise Invalid("not list")
        result = []
        cdef int i = -1
        for i, x in value:
            if i >= maxlen:
                raise Invalid("list length must <= %d" % maxlen)
            with MarkIndex(result):
                v = inner(x)
                if unique and v in result:
                    raise Invalid("not unique")
            result.append(v)
        if i + 1 < minlen:
            raise Invalid("list length must >= %d" % minlen)
        return result
    return validate_list


cdef check_optional(value, bint optional):
    """Return should_return_none"""
    if value is None:
        if optional:
            return True
        else:
            raise Invalid("required")
    return False


cdef get_dict_value(obj, str key):
    return obj.get(key, None)


cdef get_object_value(obj, str key):
    return getattr(obj, key, None)
