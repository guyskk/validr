from json import dumps, loads


def loads_dumps(value):
    return loads(dumps(value))


CASES = {
    'loads-dumps': loads_dumps
}
