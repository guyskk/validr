from validr import Invalid, Compiler, validator, T
from validr import build_enum_validator


def test_custom_validator():

    @validator(string=True)
    def choice_validator(parser, items):
        choices = items.split()

        def validate(value):
            if value in choices:
                return value
            raise Invalid('invalid choice')

        return validate

    compiler = Compiler(validators={'choice': choice_validator})
    schema = T.list(T.choice('A B C D').default('A'))
    validate = compiler.compile(schema)
    assert validate(['A', 'B', 'C', 'D', None]) == ['A', 'B', 'C', 'D', 'A']


def test_build_enum_validator():
    abcd_validator = build_enum_validator('abcd', ['A', 'B', 'C', 'D'])
    compiler = Compiler(validators={'abcd': abcd_validator})
    schema = T.list(T.abcd.default('A'))
    validate = compiler.compile(schema)
    assert validate(['A', 'B', 'C', 'D', None]) == ['A', 'B', 'C', 'D', 'A']
