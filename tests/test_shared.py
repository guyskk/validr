from collections import OrderedDict

import pytest
from validr import SchemaError, SchemaParser


def test_ordered():
    """shared should keep ordered"""
    shared = OrderedDict([
        ("user_id", "int"),
        ("user", {"user_id@user_id": "desc"}),
        ("group", {"user@user": "desc"}),
        ("team", {"group@group": "desc"}),
    ])
    for i in range(100):
        SchemaParser(shared=shared)


def test_error_position():
    shared = {"name": [{"key?unknown": "value"}]}
    with pytest.raises(SchemaError) as exinfo:
        SchemaParser(shared=shared)
    assert exinfo.value.position == "name[].key"
