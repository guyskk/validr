"""
Overview:

.. code-block:: python

    from validr import SchemaParser

    sp = SchemaParser()
    validate = sp.parse({
        "id?int": "product ID",
        "name?str": "product name",
        "price?float&min=0&exmin": "product price",
        "tags": ["&minlen=1&unique", "str&desc=\"product tag\""]
    })
    data = validate({
        "id": 1,
        "name": "TeaCup",
        "price": 9.9,
        "tags": ["Cup"]
    })
    print(data)
"""
from setuptools import setup
setup(
    name="validr",
    version="0.13.0",
    description="A simple,fast,extensible python library for data validation.",
    long_description=__doc__,
    author="guyskk",
    author_email='guyskk@qq.com',
    url="https://github.com/guyskk/validr",
    license="MIT",
    packages=['validr'],
    install_requires=[],
    tests_require=[
        'pytest',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
