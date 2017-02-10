"""
benchmark data validation librarys

benchmark: python benchmark.py
test: python benchmark.py -t
profile: python benchmark.py -p

add case:
    1. create case_{CASE_NAME}.py, add CASE_NAME to `cases` in this module
    2. implement one or more funcs which can validate the `_data` at
       the begin of this module
    3. put validate funcs in a list named `validates` in case module
"""
import json
import statistics
import sys
from profile import runctx
from timeit import timeit

from beeprint import pp

cases = [
    'json',
    'validr',
    'schema',
    'jsonschema',
    'schematics',
    'voluptuous'
]
cases_validates = {
    name: __import__('case_' + name).validates for name in cases
}
_data = {
    "user": {"userid": 5},
    "tags": [1, 2, 5, 9999, 1234567890],
    "style": {
        "width": 400,
        "height": 400,
        "border_width": 5,
        "border_style": "solid",
        "border_color": "red",
        "color": "black"
    },
    # optional
    # "unknown": "string"
}
text = json.dumps(_data)


def test():
    """test validates"""
    for case, validates in cases_validates.items():
        for i, f in enumerate(validates):
            print('{}-{}'.format(case, i).center(60, '-'))
            pp(f(json.loads(text)))


result = {}


def benchmark():
    """do benchmark"""
    for case, validates in cases_validates.items():
        result[case] = []
        for i, f in enumerate(validates):
            print('{}-{}'.format(case, i).center(60, '-'))
            data = json.loads(text)
            t = timeit("f(data)", number=10000,
                       globals={"f": f, "data": data})
            result[case].append(t)
            print(t)
    print('result-of-time'.center(60, '-'))
    pp(result)
    print('speed---time(json)/time(case)*10000'.center(60, '-'))
    base_time = statistics.mean(result['json'])  # 基准时间
    for case, times in result.items():
        for i, time in enumerate(times):
            speed = base_time * 10000 / time
            print('{:>15}-{}: {:.0f}'.format(case, i, speed))


def profile():
    """profile validr"""
    for f in cases_validates['validr']:
        data = json.loads(text)
        runctx("for i in range(1000):f(data)",
               globals=None, locals={'f': f, 'data': data})


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == "-p":
        profile()
    elif cmd == "-t":
        test()
    else:
        benchmark()
