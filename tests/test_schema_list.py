import pytest
from validr import Invalid, SchemaError, SchemaParser

sp = SchemaParser()


@pytest.mark.parametrize("schema", [
    ["int"],
    ['&desc="A list"', "int"]
])
def test_basic(schema):
    f = sp.parse(schema)
    assert f([3]) == [3]


@pytest.mark.parametrize("value", [
    [1, 2, 3],
    (1, 2, 3),
    "123",
    iter([1, 2, 3]),
])
def test_iterable(value):
    f = sp.parse(["int"])
    assert f(value) == [1, 2, 3]


def test_not_iterable():
    f = sp.parse(["int"])
    with pytest.raises(Invalid):
        f(3.14)


@pytest.mark.parametrize("schema", [
    [],
    ['&desc="A list"', "int", "xxxx"]
])
def test_invalid_length(schema):
    with pytest.raises(SchemaError):
        sp.parse(schema)


@pytest.mark.parametrize("schema", [
    ["(1,3)", "int"],
    ["&minlen=1&maxlen=3", "int"],
])
def test_minlen_maxlen(schema):
    f = sp.parse(schema)
    assert f([1]) == [1]
    assert f([1, 2, 3]) == [1, 2, 3]
    with pytest.raises(Invalid):
        f([])
    with pytest.raises(Invalid):
        f([1, 2, 3, 4])


@pytest.mark.parametrize("value", [
    [1, 1],
    [1, 2, "2"],
    [1, "1", 2],
])
def test_unique(value):
    f = sp.parse(["&unique", "int"])
    with pytest.raises(Invalid):
        f(value)


def test_optional():
    f = sp.parse(["&optional", "int"])
    assert f(None) is None
    assert f([]) == []
    # empty string is not treated as None,
    # and str is iterable, so the result is []
    assert f("") == []
