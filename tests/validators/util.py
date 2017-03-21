import pytest
from validr import Invalid, SchemaParser


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
        else:
            for item in items:
                if type(item) is tuple:
                    value, expect = item
                    yield schema, value, expect
                else:
                    for value in item:
                        yield schema, value, Invalid


sp = SchemaParser()


def case(cases):
    """Genereate test from cases data"""
    def decorator(f):
        @pytest.mark.parametrize('schema,value,expect', expend(cases))
        def wrapped(schema, value, expect):
            f = sp.parse(schema)
            if expect is Invalid:
                with pytest.raises(Invalid):
                    f(value)
            else:
                assert f(value) == expect
        return wrapped
    return decorator
