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

from setuptools import Extension, setup

DEBUG = os.getenv('VALIDR_DEBUG') == '1'
print('VALIDR_DEBUG={}'.format(DEBUG))

try:
    from Cython.Build import cythonize
except:
    from glob import glob
    from os.path import basename, splitext
    print('USE_CYTHON=False')
    ext_modules = [Extension('validr.'+splitext(basename(x))[0], [x])
                   for x in glob('validr/*.c')]
else:
    print('USE_CYTHON=True')
    directives = {'language_level': 3}
    if DEBUG:
        directives.update({
            'profile': True,
            'linetrace': True,
        })
    ext_modules = cythonize('validr/*.pyx', compiler_directives=directives)

if DEBUG:
    for m in ext_modules:
        m.define_macros.extend([
            ('CYTHON_TRACE', '1'),
            ('CYTHON_TRACE_NOGIL', '1'),
            ('CYTHON_PROFILE', '1'),
        ])

setup(
    name='validr',
    version='0.14.0',
    keywords='validation validator validate schema jsonschema',
    description=('A simple, fast, extensible python library '
                 'for data validation.'),
    long_description=__doc__,
    author='guyskk',
    author_email='guyskk@qq.com',
    url='https://github.com/guyskk/validr',
    license='MIT',
    packages=['validr'],
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
