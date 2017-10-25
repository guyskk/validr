import pytest
from validr import SchemaError, Element, T

elements = {
    'int': T.int,
    'int.optional': T.int.optional,
    'int.min(0).max(10)': T.int.min(0).max(10),
    'int.default(5)': T.int.default(5),
    'int.desc("a number")': T.int.desc('a number'),
    'int.min(0).max(10).optional.default(5).desc("a number")':
        T.int.min(0).max(10).optional.default(5).desc('a number'),
    'enum("A B C")': T.enum('A B C'),
    "enum('A B C')": T.enum('A B C'),
}

invalid_elements = [
    None,
    '',
    'int.',
    'int.min()()',
    'int.range(0,10)',
    'int.range([0,10])',
    'enum([1,2,3])',
]


@pytest.mark.parametrize('string, expect', elements.items())
def test_elements(string, expect):
    e = Element(string)
    assert repr(e)
    assert e == expect


@pytest.mark.parametrize('string', invalid_elements)
def test_invalid_elements(string):
    with pytest.raises(SchemaError):
        Element(string)
