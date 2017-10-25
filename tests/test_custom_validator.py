from validr import Invalid, Compiler, validator, T


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
