import os
from os.path import dirname, basename, splitext
from glob import glob
from setuptools import Extension, setup


def _read_file(filepath):
    with open(os.path.join(dirname(__file__), filepath), 'r', encoding='utf-8') as f:
        return f.read()


_SETUP_OPTIONS = dict(
    name='validr',
    version='1.1.3',
    keywords='validation validator validate schema jsonschema',
    description=(
        'A simple, fast, extensible python library for data validation.'),
    long_description=_read_file('README.md'),
    long_description_content_type="text/markdown",
    author='guyskk',
    author_email='guyskk@qq.com',
    url='https://github.com/guyskk/validr',
    license='MIT',
    packages=['validr'],
    package_dir={'': 'src'},
    install_requires=[
        'pyparsing>=2.1.0',
        'email_validator>=1.0.3',
        'terminaltables>=3.1.0',
    ],
    extras_require={
        'dev': [
            'pre-commit>=0.13.3',
            'tox>=2.6.0',
            'flake8>=3.2.1',
            'pytest>=3.0.6',
            'pytest-cov>=2.4.0',
            'codecov>=2.0.5',
            'terminaltables>=3.1.0',
            'invoke>=1.0.0',
            'twine>=1.11.0',
            'bumpversion>=0.5.3',
        ],
        'benchmark': [
            'beeprint>=2.4.6',
            'click>=6.7',
            'schema>=0.6.5',
            'jsonschema>=2.5.1',
            'schematics>=2.0.0a1',
            'voluptuous>=0.9.3',
        ],
    },
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
        assert mode in _SETUP_MODES, 'unknown validr setup mode {}'.format(mode)
        return mode
    if _has_c_compiler():
        return 'c'
    else:
        return 'py'


def _prepare_setup_options(mode):
    is_pyx = mode in ['pyx', 'pyx_dbg']
    is_c = mode in ['c', 'c_dbg']
    is_dist = mode in ['dist', 'dist_dbg']
    is_debug = mode.endswith('_dbg')
    ext_modules = None
    if is_pyx or is_c or is_dist:
        if is_pyx or is_dist:
            from multiprocessing import cpu_count
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
            assert sources, 'Not found any *.c source files'
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


_validr_setup()
