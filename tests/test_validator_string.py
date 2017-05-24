import pytest
from validr import SchemaError
from validr.schema import ValidatorString

validator_string = {
    'int': {'name': 'int'},
    'int()': {'name': 'int'},
    'int(0)': {'name': 'int', 'args': tuple([0])},
    'int(0,10)': {'name': 'int', 'args': tuple([0, 10])},
    'int(0, 10)': {'name': 'int', 'args': tuple([0, 10])},
    'int&default=5': {'name': 'int', 'kwargs': {'default': 5}},
    'int&optional': {'name': 'int', 'kwargs': {'optional': True}},
    'int&desc="a number"': {'name': 'int', 'kwargs': {'desc': 'a number'}},
    'int(0,10)&optional&default=5&desc="a number"': {
        'name': 'int',
        'args': tuple([0, 10]),
        'kwargs': {'default': 5, 'optional': True, 'desc': 'a number'}
    },
    '()': {},
    '(0)': {'args': tuple([0])},
    '(0,10)': {'args': tuple([0, 10])},
    '&optional': {'kwargs': {'optional': True}},
    '&default=5&optional': {'kwargs': {'default': 5, 'optional': True}},
    '(0,10)&minlen=1': {'args': tuple([0, 10]), 'kwargs': {'minlen': 1}},
    'key?int(0,10)&optional': {
        'key': 'key',
        'name': 'int',
        'args': tuple([0, 10]),
        'kwargs': {'optional': True}
    },
    'json(1,[2,3],{"k":"v"})': {'name': 'json', 'args': (
        1, [2, 3], {'k': 'v'}
    )},
    'json&k1=[1,2]&k2="&="&k3={"k":"v"}': {'name': 'json', 'kwargs': {
        'k1': [1, 2],
        'k2': '&=',
        'k3': {'k': 'v'},
    }},
    '$self&k=123': {'key': '$self', 'kwargs': {'k': 123}},
    'key@shared': {'key': 'key', 'refers': ['shared'], 'name': None},
    '$self@shared': {'key': '$self', 'refers': ['shared'], 'name': None},
    '@shared': {'refers': ['shared'], 'name': None},
    '': {},
    '@user(0,9)': {'refers': ['user'], 'args': (0, 9)},
    '@user&optional': {'refers': ['user'], 'kwargs': {'optional': True}},
    'key@user(0,9)&optional': {
        'key': 'key',
        'refers': ['user'],
        'args': (0, 9),
        'kwargs': {'optional': True}
    },
    'key@user&optional': {
        'key': 'key',
        'refers': ['user'],
        'kwargs': {'optional': True}
    },
}

invalid_validator_string = [
    'int(0,10',
    'int(0 10)'
    'int&default=abc',
    "int&desc='a number'",
    '(0,10',
    'json(1,[2,3],{"k":v})',
    'json&k1=[1,2&k2="&="&k3={"k":"v"}',
    'key?int@user',
    'key?int?str',
    'key@user@',
    'key@@user',
    None
]
DEFAULT_VS = {
    'key': None,
    'refers': None,
    'name': None,
    'args': tuple(),
    'kwargs': {}
}


@pytest.mark.parametrize('string, expect', validator_string.items())
def test_validator_string(string, expect):
    vs = ValidatorString(string)
    assert repr(vs)
    for k in DEFAULT_VS:
        if k in expect:
            assert getattr(vs, k) == expect[k]
        else:
            assert getattr(vs, k) == DEFAULT_VS[k]


@pytest.mark.parametrize('string', invalid_validator_string)
def test_invalid_validator_string(string):
    with pytest.raises(SchemaError):
        ValidatorString(string)
