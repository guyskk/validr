from collections.abc import Mapping
from .exceptions import Invalid, SchemaError


cdef class MarkIndex:
    """Add current index to Invalid/SchemaError"""

    cdef public list items

    def __init__(self, items):
        self.items = items

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is Invalid or exc_type is SchemaError:
            if self.items is None:
                exc_val.mark_index(None)
            else:
                exc_val.mark_index(len(self.items))
        if exc_type is not None:
            return False


cdef class MarkKey:
    """Add current key to Invalid/SchemaError"""

    cdef public str key

    def __init__(self, key):
        self.key = key

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is Invalid or exc_type is SchemaError:
            exc_val.mark_key(self.key)
        if exc_type is not None:
            return False
    

def merge_validators(list validators, bint optional=False, str desc=None):
    def merged_validator(value):
        if check_optional(value, optional):
            return None
        cdef dict result = {}
        for v in validators:
            data = v(value)
            try:
                result.update(data)
            except TypeError:
                raise SchemaError("can't merge non-dict value")
        return result
    return merged_validator
    
    
def dict_validator(inners, bint optional=False, str desc=None):

    inners = list(inners.items())

    def validator(value):
        if check_optional(value, optional):
            return None
        result = {}
        # use dict instead of Mapping can speed up about 10%
        if isinstance(value, Mapping):
            get_item = get_dict_value
        else:
            get_item = get_object_value
        cdef str k
        for k, validate in inners:
            with MarkKey(k):
                result[k] = validate(get_item(value, k))
        return result
    return validator

def list_validator(inner, int minlen=0, int maxlen=1024, bint unique=False,
                   bint optional=False, str desc=None):
    def validator(value):
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
    return validator


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
