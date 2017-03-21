"""This module is keep for compatibility with version 0.13.0 and before"""
from ._exception import Invalid
from ._validator import build_re_validator, builtin_validators  # noqa


def handle_default_optional_desc(string=False):
    """
    Decorator for handling params: default,optional,desc
    :param string: if the value to be validated is string or not
    """

    import warnings
    warnings.warn(DeprecationWarning(
        '`handle_default_optional_desc` is deprecated, it will be '
        'removed in v1.0, please use `validator` instead.'
    ))

    def handler(some_validator):
        def wrapped_validator(*args, **kwargs):
            default = kwargs.pop('default', None)
            optional = kwargs.pop('optional', False)
            kwargs.pop('desc', None)
            origin_validator = some_validator(*args, **kwargs)
            if string:
                def validator(value):
                    if value is None or value == '':
                        if not (default is None or default == ''):
                            return default
                        elif optional:
                            return ''
                        else:
                            raise Invalid('required')
                    return origin_validator(value)
            else:
                def validator(value):
                    if value is None:
                        if default is not None:
                            return default
                        elif optional:
                            return None
                        else:
                            raise Invalid('required')
                    return origin_validator(value)
            return validator
        return wrapped_validator
    return handler
