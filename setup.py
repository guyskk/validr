# coding:utf-8

from setuptools import setup
setup(
    name="validater",
    version="0.8.2",
    description="a python tool to "
    "validate json/dict/list and convert value by schema",
    author="kk",
    url="https://github.com/guyskk/validater",
    license="MIT",
    packages=['validater'],
    install_requires=[
        'python-dateutil>=2.4',
        'six>=1.10.0',
    ],
)
