"""
Overview:

.. code-block:: python

    from sys import version_info
    from validr import SchemaParser

    parser = SchemaParser()
    validate = parser.parse({
        "major?int&min=3": "Major version",
        "minor?int&min=3": "Minor version",
        "micro?int&min=0": "Micro version",
        "releaselevel?str": "Release level",
        "serial?int": "Serial number"
    })
    print(validate(version_info))
"""
import os
from os.path import basename, splitext
from glob import glob
from setuptools import Extension, setup

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
    ext_modules = cythonize('validr/*.pyx', compiler_directives=directives)
else:
    sources = list(glob('validr/*.c'))
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
    version='1.0.0',
    keywords='validation validator validate schema jsonschema',
    description=('A simple, fast, extensible python library '
                 'for data validation.'),
    long_description=__doc__,
    author='guyskk',
    author_email='guyskk@qq.com',
    url='https://github.com/guyskk/validr',
    license='MIT',
    packages=['validr'],
    install_requires=[
        'pyparsing>=2.1.0',
        'email_validator>=1.0.3',
    ],
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
