from validr import Invalid, SchemaParser
from validr.validators import handle_default_optional_desc


def test_custom_validator():
    @handle_default_optional_desc()
    def choice_validator():
        def validator(value):
            if value in "ABCD":
                return value
            raise Invalid("invalid choice")
        return validator
    sp = SchemaParser(validators={"choice": choice_validator})
    for value in "ABCD":
        assert sp.parse("choice")(value) == value
    assert sp.parse("choice&optional")(None) is None
