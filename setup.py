# coding:utf-8

from setuptools import setup
setup(
    name="validater",
    version="0.9.0",
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
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
