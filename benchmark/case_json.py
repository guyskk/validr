from json import dumps, loads


def _validate_0(value):
    return loads(dumps(value))


validates = [_validate_0]
