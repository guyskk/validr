import os
from os.path import dirname, basename, splitext
from glob import glob
from multiprocessing import cpu_count
from setuptools import Extension, setup

with open(os.path.join(dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

DEBUG = os.getenv('VALIDR_DEBUG') == '1'
print('VALIDR_DEBUG={}'.format(DEBUG))
USE_CYTHON = os.getenv('VALIDR_USE_CYTHON') == '1'
print('VALIDR_USE_CYTHON={}'.format(USE_CYTHON))

if USE_CYTHON:
    from Cython.Build import cythonize
    directives = {'language_level': 3}
    if DEBUG:
        directives.update({
            'profile': True,
            'linetrace': True,
        })
    ext_modules = cythonize(
        'src/validr/*.pyx',
        nthreads=cpu_count(),
        compiler_directives=directives
    )
else:
    sources = list(glob('src/validr/*.c'))
    assert sources, 'Not found any *.c source files'
    ext_modules = []
    for filepath in sources:
        module_name = 'validr.' + splitext(basename(filepath))[0]
        ext_modules.append(Extension(module_name, [filepath]))

if DEBUG:
    for m in ext_modules:
        m.define_macros.extend([
            ('CYTHON_TRACE', '1'),
            ('CYTHON_TRACE_NOGIL', '1'),
            ('CYTHON_PROFILE', '1'),
        ])

setup(
    name='validr',
    version='1.0.6',
    keywords='validation validator validate schema jsonschema',
    description=('A simple, fast, extensible python library '
                 'for data validation.'),
    long_description=long_description,
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
    ext_modules=ext_modules,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
