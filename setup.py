from setuptools import setup
setup(
    name="validater",
    version="0.10.3",
    description="a python tool to "
                "validate json/dict/list and convert value by schema",
    author="guyskk",
    author_email='guyskk@qq.com',
    url="https://github.com/guyskk/validater",
    license="MIT",
    packages=['validater'],
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
