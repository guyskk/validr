import pytest
from validr import Invalid, SchemaError, SchemaParser

sp = SchemaParser()


@pytest.mark.parametrize("schema,expect", [
    ("unknown", ""),
    ([], ""),
    ({"userid": "ID"}, "userid"),
    (["unknown"], "[]"),
    ({"user": {"userid": "ID"}}, "user.userid"),
    ({"tags": ["unknown"]}, "tags[]"),
    ([{"userid": "int"}], "[].userid"),
    ([["unknown"]], "[][]"),
    ({"user": {"tags": ["unknown"]}}, "user.tags[]"),
])
def test_schema_error(schema, expect):
    with pytest.raises(SchemaError) as exinfo:
        sp.parse(schema)
    assert exinfo.value.position == expect


@pytest.mark.parametrize("schema,expect", [
    ("int&unknown", ""),
    ({"userid": "int&unknown"}, "userid"),
    ({"friends": [{"userid": "int&unknown"}]}, "friends[].userid"),
])
def test_invalid_validator_params(schema, expect):
    with pytest.raises(SchemaError) as exinfo:
        sp.parse(schema)
    assert exinfo.value.position == expect


@pytest.mark.parametrize("value,expect", [
    (None, ""),
    ({"user": None}, "user"),
    ({"user": {"userid": "x", "tags": []}}, "user.userid"),
    ({"user": {"userid": 1, "tags": None}}, "user.tags"),
    ({"user": {"userid": 1, "tags": [0, 'x']}}, "user.tags[1]"),
])
def test_dict_invalid(value, expect):
    f = sp.parse({
        "user": {
            "userid?int": "ID",
            "tags": ["int"]
        }
    })
    with pytest.raises(Invalid) as exinfo:
        f(value)
    assert exinfo.value.position == expect


@pytest.mark.parametrize("value,expect", [
    (None, ""),
    ([None], "[0]"),
    ([[{"userid": 0}], [None]], "[1][0]"),
    ([[{"userid": "x"}]], "[0][0].userid"),
])
def test_list_invalid(value, expect):
    f = sp.parse([[{"userid?int": "ID"}]])
    with pytest.raises(Invalid) as exinfo:
        f(value)
    assert exinfo.value.position == expect
