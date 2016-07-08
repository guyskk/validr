from setuptools import setup
setup(
    name="validater",
    version="0.9.5",
    description="a python tool to "
    "validate and convert value to python object by schema",
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
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
