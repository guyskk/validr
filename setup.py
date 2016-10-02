from setuptools import setup
setup(
    name="validr",
    version="0.12.0",
    description="A simple,fast,extensible python library for data validation.",
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
