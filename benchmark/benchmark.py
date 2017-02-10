"""
benchmark data validation librarys

usage:

    python benchmark.py

add case:
    1. create case_{CASE_NAME}.py
    2. implement one or more funcs which can validate the `DATA` in this module
    3. put validate funcs in a dict named `CASES` in case module
"""
import json
import statistics
import sys
from cProfile import runctx
from glob import glob
from os.path import basename, dirname, splitext
from timeit import timeit

import click

from beeprint import pp

DATA = {
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
    # "optional": "string"
}
TEXT = json.dumps(DATA)


def make_data():
    return json.loads(TEXT)


def glob_cases():
    files = glob(dirname(__file__) + '/case_*.py')
    cases = {}
    for filename in files:
        module = splitext(basename(filename))[0]
        name = module[len('case_'):]
        cases[name] = __import__(module).CASES
    return cases


CASES = glob_cases()


@click.group()
def cli():
    pass


@cli.command()
def show():
    """show all cases"""
    pp({name: list(cases) for name, cases in CASES.items()})


@cli.command()
def test():
    """test all cases"""
    for name, subcases in CASES.items():
        for subname, f in subcases.items():
            value = f(make_data())
            try:
                ok = (value['user'] == DATA['user'] and
                      value['tags'] == DATA['tags'] and
                      value['style'] == DATA['style'])
            except:
                ok = False
            if ok:
                print('{}:{} OK'.format(name, subname))
            else:
                print('{}:{}'.format(name, subname).center(60, '-'))
                pp(value)


@cli.command()
@click.option('--validr', is_flag=True, help='only benchmark validr')
def benchmark(validr):
    """do benchmark"""
    if validr:
        cases = {'json': CASES['json'], 'validr': CASES['validr']}
    else:
        cases = CASES
    result = {}
    print('time---the-result-of-timeit'.center(60, '-'))
    for name, suncases in cases.items():
        result[name] = {}
        for subname, f in suncases.items():
            params = {"f": f, "data": make_data()}
            t = timeit("f(data)", number=100000, globals=params)
            result[name][subname] = t
            print('{}:{} {}'.format(name, subname, t))
    print('speed---time(json)/time(case)*10000'.center(60, '-'))
    base_time = statistics.mean(result['json'].values())  # 基准时间
    for name, subcases in result.items():
        for subname, time in subcases.items():
            speed = base_time * 10000 / time
            print('{}:{} {:.0f}'.format(name, subname, speed))


@cli.command()
def profile():
    """profile validr"""
    for name, f in CASES['validr'].items():
        print(name.center(60, '-'))
        params = {"f": f, "data": make_data()}
        runctx("for i in range(10000):f(data)", globals=params, locals=None)


if __name__ == "__main__":
    cli()
