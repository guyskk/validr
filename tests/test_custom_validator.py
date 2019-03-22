from validr import Invalid, Compiler, validator, T
from validr import create_enum_validator, builtin_validators


def test_custom_validator():
    @validator(accept=str, output=str)
    def choice_validator(compiler, items):
        choices = set(items.split())

        def validate(value):
            if value in choices:
                return value
            raise Invalid('invalid choice')

        return validate

    compiler = Compiler(validators={'choice': choice_validator})
    schema = T.list(T.choice('A B C D').default('A'))
    assert T(schema) == schema  # test copy custom validator
    validate = compiler.compile(schema)
    assert validate(['A', 'B', 'C', 'D', None]) == ['A', 'B', 'C', 'D', 'A']


def test_wrapped_validator():
    str_validator = builtin_validators['str']
    assert str_validator.is_string
    assert str_validator.accept_string
    assert str_validator.accept_object
    assert str_validator.output_string
    assert not str_validator.output_object

    logs = []

    @validator(accept=(str, object), string=True)
    def wrapped_str_validator(*args, **kwargs):
        _validate = str_validator.validator(*args, **kwargs)

        def validate(value):
            logs.append(value)
            return _validate(value)

        return validate

    compiler = Compiler(validators={'str': wrapped_str_validator})
    validate = compiler.compile(T.str.optional)
    assert validate('abc') == 'abc'
    assert logs == ['abc']


def test_create_enum_validator():
    abcd_validator = create_enum_validator('abcd', ['A', 'B', 'C', 'D'])
    compiler = Compiler(validators={'abcd': abcd_validator})
    schema = T.list(T.abcd.default('A'))
    validate = compiler.compile(schema)
    assert validate(['A', 'B', 'C', 'D', None]) == ['A', 'B', 'C', 'D', 'A']
