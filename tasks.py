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
def test(ctx, benchmark=False, profile=False, k=None):
    pytest_k = ' -k {}'.format(k) if k is not None else ''
    os.environ['VALIDR_SETUP_MODE'] = 'dist_dbg'
    ctx.run('pip install --no-deps -e .')
    # cython speedup mode
    ctx.run("pytest" + pytest_k)
    if benchmark:
        ctx.run('python benchmark/benchmark.py benchmark --validr')
    if profile:
        ctx.run('python benchmark/benchmark.py profile')
    # pure python mode
    ctx.run('rm -rf src/validr/*.so')
    ctx.run("pytest --cov-config=.coveragerc_py" + pytest_k)
    if benchmark:
        ctx.run('python benchmark/benchmark.py benchmark --validr')
    if profile:
        ctx.run('python benchmark/benchmark.py profile')


@task(pre=[clean])
def build(ctx):
    os.environ['VALIDR_SETUP_MODE'] = 'dist'
    ctx.run('python setup.py build')
    ctx.run('python setup.py sdist')


@task(pre=[build])
def e2e_test(ctx):
    PYTHON = '.test-venv/bin/python'
    PIP = '{PYTHON} -m pip'.format(PYTHON=PYTHON)

    os.environ['VALIDR_SETUP_MODE'] = 'py'
    ctx.run('python -m venv --clear .test-venv')
    ctx.run('{PIP} install dist/*'.format(PIP=PIP))
    ctx.run('{PYTHON} tests/smoke.py'.format(PYTHON=PYTHON))

    os.environ['VALIDR_SETUP_MODE'] = ''
    ctx.run('python -m venv --clear .test-venv')
    ctx.run('{PIP} install dist/*'.format(PIP=PIP))
    ctx.run('{PYTHON} tests/smoke.py'.format(PYTHON=PYTHON))


@task(pre=[test, e2e_test, build])
def publish(ctx):
    ctx.run('twine upload dist/*')


@task(pre=[build])
def benchmark(ctx, validr=False):
    os.environ['VALIDR_SETUP_MODE'] = ''
    ctx.run('pip uninstall -y validr')
    ctx.run('pip install dist/*')
    benchmark_command = 'python benchmark/benchmark.py benchmark'
    if validr:
        benchmark_command += ' --validr'
    ctx.run(benchmark_command)
