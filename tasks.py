import os
from invoke import task


@task
def clean(ctx):
    ctx.run('rm -rf build/*')
    ctx.run('rm -rf dist/*')
    ctx.run('rm -rf .pytest_cache')
    ctx.run('rm -rf src/validr/*.c')
    ctx.run('rm -rf src/validr/*.so')
    ctx.run('rm -rf src/validr/*_py.py')
    ctx.run(r'find . | grep -E "(__pycache__|\.egg-info|\.so|\.c|\.pyc|\.pyo)$" | xargs rm -rf')


@task(pre=[clean])
def test(ctx, profile=False):
    os.environ['VALIDR_SETUP_MODE'] = 'dist_dbg'
    ctx.run('pip install --no-deps -e .')
    # cython speedup mode
    ctx.run('pytest --cov=validr --cov-report=term-missing')
    ctx.run('python benchmark/benchmark.py benchmark --validr')
    if profile:
        ctx.run('python benchmark/benchmark.py profile')
    # pure python mode
    ctx.run('rm -rf src/validr/*.so')
    ctx.run('pytest --cov=validr --cov-report=term-missing --cov-config=.coveragerc_py')
    ctx.run('python benchmark/benchmark.py benchmark --validr')
    if profile:
        ctx.run('python benchmark/benchmark.py profile')


@task(pre=[clean])
def build(ctx):
    os.environ['VALIDR_SETUP_MODE'] = 'dist'
    ctx.run('python setup.py build')
    ctx.run('python setup.py sdist')


@task(pre=[build])
def publish(ctx):
    ctx.run('twine upload dist/*')


@task(pre=[build])
def e2e_test(ctx):
    os.environ['VALIDR_SETUP_MODE'] = ''
    ctx.run('pip uninstall -y validr')
    ctx.run('pip install dist/*')
    ctx.run('pytest --cov=validr')
    os.environ['VALIDR_SETUP_MODE'] = 'py'
    ctx.run('pip uninstall -y validr')
    ctx.run('pip install dist/*')
    ctx.run('pytest --cov=validr --cov-config=.coveragerc_py')


@task(pre=[build])
def benchmark(ctx):
    os.environ['VALIDR_SETUP_MODE'] = ''
    ctx.run('pip uninstall -y validr')
    ctx.run('pip install dist/*')
    ctx.run('python benchmark/benchmark.py benchmark')
