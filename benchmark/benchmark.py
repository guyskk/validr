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
from profile import runctx
from glob import glob
from os.path import basename, dirname, splitext
from timeit import Timer as BaseTimer

import click
from beeprint import pp

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

# support Timer.autorange which add in python 3.6
if hasattr(BaseTimer, 'autorange'):
    Timer = BaseTimer
else:
    class Timer(BaseTimer):
        def autorange(self, callback=None):
            """Return the number of loops and time taken so that total time >= 0.2.
            Calls the timeit method with *number* set to successive powers of
            ten (10, 100, 1000, ...) up to a maximum of one billion, until
            the time taken is at least 0.2 second, or the maximum is reached.
            Returns ``(number, time_taken)``.
            If *callback* is given and is not None, it will be called after
            each trial with two arguments: ``callback(number, time_taken)``.
            """
            for i in range(1, 10):
                number = 10**i
                time_taken = self.timeit(number)
                if callback:
                    callback(number, time_taken)
                if time_taken >= 0.2:
                    break
            return (number, time_taken)


@click.group()
def cli():
    pass


@cli.command()
def show():
    """show all cases"""
    pp({name: list(cases) for name, cases in CASES.items()})


def print_item(name, subname, value):
    print('{:>12}:{:<16} {}'.format(name, subname, value))


@cli.command()
def test():
    """test all cases"""
    for name, subcases in CASES.items():
        for subname, f in subcases.items():
            try:
                value = f(make_data())
                assert value['user'] == DATA['user']
                assert value['tags'] == DATA['tags']
                assert value['style'] == DATA['style']
                msg = 'OK'
            except AssertionError:
                msg = 'Failed\n{line}\n{value}{line}'.format(
                    line='-' * 60, value=pp(value, output=False))
            except Exception as ex:
                msg = 'Failed: ' + str(ex)
            print_item(name, subname, msg)


@cli.command()
@click.option('--validr', is_flag=True, help='only benchmark validr')
def benchmark(validr):
    """do benchmark"""
    if validr:
        cases = {k: CASES[k] for k in ['json', 'validr']}
    else:
        cases = CASES
    result = {}

    print('timeits'.center(60, '-'))
    for name, suncases in cases.items():
        for subname, f in suncases.items():
            data = make_data()
            n, t = Timer(lambda: f(data)).autorange()
            result[name, subname] = t / n
            print_item(name, subname, '{:>8} loops cost {:.3f}s'.format(n, t))

    print('scores'.center(60, '-'))
    base = result['json', 'loads-dumps']
    for (name, subname), v in result.items():
        print_item(name, subname, '{:>8}'.format(round(base / v * 1000)))


@cli.command()
def profile():
    """profile validr"""
    f = CASES['validr']['default']
    params = {'f': f, 'data': make_data()}
    runctx('for i in range(10**6): f(data)', globals=params, locals=None)


if __name__ == '__main__':
    cli()
