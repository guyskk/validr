import functools
import pytest
from validr import ValidrError, Invalid, SchemaError, Compiler

compiler = Compiler()


def schema_error_position(*items):
    def decorator(f):
        @pytest.mark.parametrize('schema,expect', items)
        def wrapped(schema, expect):
            with pytest.raises(SchemaError) as exinfo:
                compiler.compile(schema)
            assert exinfo.value.position == expect
        return wrapped
    return decorator


def expect_position(pos):
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            with pytest.raises(ValidrError) as exinfo:
                f(*args, **kwargs)
            position = exinfo.value.position
            assert position == pos, (position, pos)
        return wrapped
    return decorator


def invalid_position(*items):
    def decorator(f):
        @pytest.mark.parametrize('schema,expect', items)
        def wrapped(schema, expect):
            with pytest.raises(Invalid) as exinfo:
                compiler.compile(schema)
            assert exinfo.value.position == expect
        return wrapped
    return decorator
