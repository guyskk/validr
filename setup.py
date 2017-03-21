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
from setuptools import Extension, setup

try:
    from Cython.Build import cythonize
    ext_modules = cythonize('validr/*.pyx')
except:
    from glob import glob
    from os.path import basename, splitext
    ext_modules = [Extension('validr.'+splitext(basename(x))[0], [x])
                   for x in glob('validr/*.c')]

setup(
    name='validr',
    version='0.13.0',
    keywords='validation validator validate schema jsonschema',
    description='A simple,fast,extensible python library for data validation.',
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
