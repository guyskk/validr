import pytest
from validr import Invalid, SchemaParser
from validr.validators import handle_default_optional_desc


def test_custom_validator():
    with pytest.warns(DeprecationWarning):
        @handle_default_optional_desc()
        def choice_validator():
            def validator(value):
                if value in 'ABCD':
                    return value
                raise Invalid('invalid choice')
            return validator
    sp = SchemaParser(validators={'choice': choice_validator})
    for value in 'ABCD':
        assert sp.parse('choice')(value) == value
    assert sp.parse('choice&optional')(None) is None


def test_deprecated():
    from validr.validators import builtin_validators  # noqa
    from validr.validators import build_re_validator  # noqa
    from validr.schema import MarkIndex, MarkKey  # noqa
    with pytest.warns(DeprecationWarning):
        try:
            with MarkIndex([1, 2, 3]):
                raise Invalid('test')
        except Invalid:
            pass
    with pytest.warns(DeprecationWarning):
        try:
            with MarkKey('key'):
                raise Invalid('test')
        except Invalid:
            pass
