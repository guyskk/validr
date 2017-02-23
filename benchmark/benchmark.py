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
from timeit import repeat

import click

from analyze import analyze, scores
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


def warmup():
    data = make_data()
    validates = list(CASES['json'].values()) + list(CASES['validr'].values())
    for i in range(10000):
        for f in validates:
            f(data)


@cli.command()
@click.option('--validr', is_flag=True, help='only benchmark validr')
def benchmark(validr):
    """do benchmark"""
    if validr:
        warmup()
        cases = {'json': CASES['json'], 'validr': CASES['validr']}
    else:
        cases = CASES
    result = {}
    for name, suncases in cases.items():
        for subname, f in suncases.items():
            params = {"f": f, "data": make_data()}
            times = repeat("f(data)", repeat=1000, number=100, globals=params)
            result['{}:{}'.format(name, subname)] = times
    speeds = analyze(result)
    print('speeds'.center(60, '-'))
    print(speeds)
    print('scores'.center(60, '-'))
    print(scores(speeds))


@cli.command()
def profile():
    """profile validr"""
    for name, f in CASES['validr'].items():
        print(name.center(60, '-'))
        params = {"f": f, "data": make_data()}
        runctx("for i in range(10000):f(data)", globals=params, locals=None)


if __name__ == "__main__":
    cli()
