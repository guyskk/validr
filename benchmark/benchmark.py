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
from cProfile import runctx
from glob import glob
from os.path import basename, dirname, splitext

import click

from beeprint import pp
from stable_timeit import stable_timeit as timeit

DATA = {
    'user': {'userid': 5},
    'tags': [1, 2, 5, 9999, 1234567890],
    'style': {
        'width': 400,
        'height': 400,
        'border_width': 5,
        'border_style': 'solid',
        'border_color': 'red',
        'color': 'black'
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
                print_item(name, subname, 'OK')
            else:
                print('{}:{}'.format(name, subname).center(60, '-'))
                pp(value)


def print_item(name, subname, value):
    print('{}:{} {}'.format(name.rjust(12), subname.ljust(24), value))


@cli.command()
@click.option('--validr', is_flag=True, help='only benchmark validr')
def benchmark(validr):
    """do benchmark"""
    if validr:
        cases = {'json': CASES['json'], 'validr': CASES['validr']}
    else:
        cases = CASES
    result = {}

    print('timeits'.center(60, '-'))
    for name, suncases in cases.items():
        for subname, f in suncases.items():
            data = make_data()
            t = timeit(lambda: f(data), number=100, repeat=500)
            result[name, subname] = t
            print_item(name, subname, t)

    print('speeds'.center(60, '-'))
    for (name, subname), v in result.items():
        print_item(name, subname, round(1.0/v))

    print('scores'.center(60, '-'))
    base = result['json', 'loads-dumps']
    for (name, subname), v in result.items():
        print_item(name, subname, round(base/v*1000))


@cli.command()
def profile():
    """profile validr"""
    for name, f in CASES['validr'].items():
        print(name.center(60, '-'))
        params = {'f': f, 'data': make_data()}
        runctx('for i in range(1000000):f(data)', globals=params, locals=None)


if __name__ == '__main__':
    cli()
