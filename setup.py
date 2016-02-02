#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, print_function

from setuptools import setup
setup(
    name="validater",
    version="0.9.3",
    description="a python tool to "
    "validate and convert value to python object by schema",
    author="kk",
    url="https://github.com/guyskk/validater",
    license="MIT",
    packages=['validater'],
    install_requires=[
        'six>=1.10.0',
    ],
    tests_require=[
        'pytest',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
