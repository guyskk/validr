import os
from invoke import task


@task
def test(ctx):
    os.environ['VALIDR_DEBUG'] = '1'
    os.environ['VALIDR_USE_CYTHON'] = '1'
    ctx.run('python setup.py build --verbose')
    ctx.run('pytest --cov=validr --cov-report=term-missing -r w')
    ctx.run('python benchmark/benchmark.py benchmark --validr')
    ctx.run('python benchmark/benchmark.py profile')


@task
def build(ctx, debug=False):
    if debug:
        os.environ['VALIDR_DEBUG'] = '1'
    os.environ['VALIDR_USE_CYTHON'] = '1'
    ctx.run('rm -rf dist/*')
    ctx.run('python setup.py build')
    ctx.run('python setup.py sdist')
