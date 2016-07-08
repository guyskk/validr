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
def int_validater(min=0, max=1024):
    def validater(value):
        try:
            v = int(value)
        except ValueError:
            raise Invalid("invalid int")
        if v < min:
            raise Invalid("value must >= %d" % min)
        elif v > max:
            raise Invalid("value must <= %d" % max)
        return v
    return validater


@handle_default_optional_desc
def bool_validater():
    def validater(value):
        if isinstance(value, bool):
            return value
        else:
            raise Invalid("invalid bool")
    return validater

builtin_validaters = {
    "int": int_validater,
    "bool": bool_validater,
}
