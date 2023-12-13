import os
from glob import glob
from multiprocessing import cpu_count
from os.path import basename, dirname, splitext
from platform import python_implementation

from setuptools import Extension, setup


def _read_file(filepath):
    filepath = os.path.join(dirname(__file__), filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


_SETUP_OPTIONS = dict(
    name='validr',
    version='1.2.1',
    keywords='validation validator validate schema jsonschema',
    description=(
        'A simple, fast, extensible python library for data validation.'),
    long_description=_read_file('README.md'),
    long_description_content_type="text/markdown",
    author='guyskk',
    author_email='guyskk@qq.com',
    url='https://github.com/guyskk/validr',
    license='MIT',
    packages=['validr', 'validr._vendor'],
    package_dir={'': 'src'},
    package_data={'validr': ['*.pyi']},
    include_package_data=True,
    install_requires=[
        'idna>=2.5',
        'pyparsing>=2.1.0',
    ],
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)


_SETUP_MODES = {
    'pyx',       # cythonize *.pyx
    'pyx_dbg',   # cythonize *.pyx with debug info
    'c',         # ext_modules from *.c
    'c_dbg',     # ext_modules from *.c with debug info
    'py',        # pure python
    'dist',      # build *_c.c and *_py.py for release
    'dist_dbg',  # build *_c.c and *_py.py for release with debug info
}


def _has_c_compiler():
    try:
        import distutils.ccompiler
        cc = distutils.ccompiler.new_compiler()
        return cc.has_function('rand', includes=['stdlib.h'])
    except Exception as ex:
        print('failed to check c compiler: {}'.format(ex))
        return False


def _get_validr_setup_mode():
    mode = os.getenv('VALIDR_SETUP_MODE')
    if mode:
        mode = mode.strip().lower()
        if mode not in _SETUP_MODES:
            err_msg = 'unknown validr setup mode {}'.format(mode)
            raise RuntimeError(err_msg)
        return mode
    if _has_c_compiler():
        return 'c'
    else:
        return 'py'


def _prepare_setup_options(mode):
    is_pyx = mode in ['pyx', 'pyx_dbg']
    is_c = mode in ['c', 'c_dbg']
    is_debug = mode.endswith('_dbg')
    is_dist = mode in ['dist', 'dist_dbg']
    enable_c = python_implementation() == 'CPython'
    ext_modules = None
    if enable_c and (is_pyx or is_c or is_dist):
        if is_pyx or is_dist:
            from Cython.Build import cythonize
            directives = {'language_level': 3}
            if is_debug:
                directives.update({
                    'profile': True,
                    'linetrace': True,
                })
            ext_modules = cythonize(
                'src/validr/*.pyx',
                nthreads=cpu_count(),
                compiler_directives=directives
            )
        if is_c:
            sources = list(glob('src/validr/*.c'))
            if not sources:
                raise RuntimeError('Not found any *.c source files')
            ext_modules = []
            for filepath in sources:
                module_name = 'validr.' + splitext(basename(filepath))[0]
                ext_modules.append(Extension(module_name, [filepath]))
        if is_debug:
            for m in ext_modules:
                m.define_macros.extend([
                    ('CYTHON_TRACE', '1'),
                    ('CYTHON_TRACE_NOGIL', '1'),
                    ('CYTHON_PROFILE', '1'),
                ])
    if is_dist:
        from validr_uncython import compile_pyx_to_py
        sources = list(glob('src/validr/*.pyx'))
        compile_pyx_to_py(sources, debug=is_debug)

    return dict(ext_modules=ext_modules, **_SETUP_OPTIONS)


def _validr_setup():
    mode = _get_validr_setup_mode()
    print('VALIDR_SETUP_MODE={}'.format(mode))
    options = _prepare_setup_options(mode)
    setup(**options)


if __name__ == '__main__':
    _validr_setup()
