# coding:utf-8

from setuptools import setup
setup(
    name="validater",
    version="0.7.3",
    description="a python tool to "
    "validate json/dict/list and convert value by schema",
    author="kk",
    url="https://github.com/guyskk/validater",
    license="MIT",
    packages=['validater'],
    install_requires=[
        'python-dateutil>=2.4',
        'pymongo>=3.0'
    ],
)
