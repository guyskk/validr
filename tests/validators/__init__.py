import pytest
from validr import Invalid, Compiler


def expend(cases):
    """
    Expend cases

    Args:
        cases:

            {
                "schema": [
                    (value, expect), # tuple, valid value
                    ...
                    [value, ...]     # list, invalid value
                ]
            }

        or

            {
                "schema": {
                    "valid": [value, ...]    # valid value, and expect=value
                    "invalid": [value, ...]  # invalid value
                    "expect": [              # valid value and expect
                        (value, expect),
                        ...
                    ]
                }
            }
    Yields:
        schema, value, expect/Invalid
    """
    for schema, items in cases.items():
        if isinstance(items, dict):
            for value in items.get('valid', []):
                yield schema, value, value
            for value in items.get('invalid', []):
                yield schema, value, Invalid
            for value, expect in items.get('expect', []):
                yield schema, value, expect
        else:
            for item in items:
                if type(item) is tuple:
                    value, expect = item
                    yield schema, value, expect
                else:
                    for value in item:
                        yield schema, value, Invalid


compiler = Compiler()


def case(cases):
    """Genereate test from cases data"""
    def decorator(f):
        @pytest.mark.parametrize('schema,value,expect', expend(cases))
        def wrapped(schema, value, expect):
            f = compiler.compile(schema)
            if expect is Invalid:
                with pytest.raises(Invalid):
                    f(value)
            else:
                result = f(value)
                assert result == expect, 'result={!r} expect={!r}'.format(result, expect)
        return wrapped
    return decorator
