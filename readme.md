# Validr

[![travis-ci](https://api.travis-ci.org/guyskk/validr.svg)](https://travis-ci.org/guyskk/validr) [![codecov](https://codecov.io/gh/guyskk/validr/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validr)

[中文](readme-zh-cn.md) | [English](readme.md)

A simple,fast,extensible python library for data validation.

- Simple and readable schema
- 10X faster than [jsonschema](https://github.com/Julian/jsonschema),
  40X faster than [schematics](https://github.com/schematics/schematics)
- Can validate and serialize any object
- Easy to create custom validators
- Accurate error messages include reason and position

Note: Only support python 3.3+

## Overview

```python
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
```

## Install

    pip install validr


## Schema syntax

[Isomorph-JSON-Schema](Isomorph-JSON-Schema.md)

## Usage

#### Validate simple data:

```python
>>> from validr import SchemaParser,Invalid
>>> sp = SchemaParser()
>>> f = sp.parse("int(0, 9)")
>>> f("3")
3
>>> f(-1)
...
validr._exception.Invalid: value must >= 0
>>> f("abc")
...
validr._exception.Invalid: invalid int
>>>
```

#### Validate complex data:

```python
>>> f = sp.parse({"userid?int(0,9)": "UserID"})
>>> user = {"userid": 15}
>>> f(user)
...
validr._exception.Invalid: value must <= 9 in userid
>>> class User:pass
...
>>> user = User()
>>> user.userid=5
>>> f(user)
{'userid': 5}
>>> user.userid = 15
>>> f(user)
...
validr._exception.Invalid: value must <= 9 in userid
>>> f = sp.parse({"friends":[{"userid?int(0,9)":"UserID"}]})
>>> f({"friends":[user,user]})
...
validr._exception.Invalid: value must <= 9 in friends[0].userid
>>> user.userid=5
>>> f({"friends":[user,user]})
{'friends': [{'userid': 5}, {'userid': 5}]}
>>>
```

#### Handle Invalid:

```python
>>> user.userid = 15
>>> try:
        f({"friends":[user,user]})
    except Invalid as ex:
        print(ex.message)
        print(ex.position)
>>>
value must <= 9
friends[0].userid
>>>
```

#### Refer:

Simple usage:

```python
>>> shared = {"userid": "int(0,9)"}
>>> sp = SchemaParser(shared=shared)
>>> f = sp.parse("@userid")
>>> f(5)
5
>>> f = sp.parse({"userid@userid":"UserID"})
>>> f({"userid":5})
{'userid': 5}
>>> f = sp.parse(["@userid"])
>>> f([1,2])
[1, 2]
>>> f = sp.parse({"userid@userid&optional":"UserID"})
>>> f({"userid":None})
{'userid': None}
>>>
```

Refer in shared:

```python
>>> from collections import OrderedDict
>>> shared = OrderedDict([
    ("userid", "int(0,9)"),
    ("user", {"userid@userid":"UserID"}),
])
>>> sp = SchemaParser(shared=shared)
>>> f = sp.parse("@user")
>>> f({"userid":5})
{'userid': 5}
```

Note: You can only refer to the back of the front, and you should use OrderedDict instead of dict.

```python
>>> shared = OrderedDict([
    ("user", {"userid@userid":"UserID"}),
    ("userid", "int(0,9)"),
])
>>> sp = SchemaParser(shared=shared)
...
validr._exception.SchemaError: shared 'userid' not found in user.userid
```

#### Merge:

```python
>>> shared = {
      "size": {
        "width?int": "width",
        "height?int": "height"
      },
      "border": {
        "border-width?int": "border-width",
        "border-style?str": "border-style",
        "border-color?str": "border-color"
      }
    }
>>> sp = SchemaParser(shared=shared)
>>> f = sp.parse({"$self@size@border": "merges"})
>>> value = {
        "width": "400",
        "height": "400",
        "border-width": "5",
        "border-style": "solid",
        "border-color": "red"
    }
>>> f(value)
{'height': 400, 'border-width': 5, 'border-color': 'red', 'border-style': 'solid', 'width': 400}
>>>
```

Note: Don't merge schemas which have the same key.  


#### Custom validator:

`validator()` decorater is used to create validator, and it can make you validator support params `default`, `optional`, `desc`.

```python
>>> from validr import validator
>>> @validator(string=False)
    def multiple_validator(value, n):
        try:
            if value%n == 0:
                return value
        except:
            pass
        raise Invalid("not a multiple of %d"%n)
>>> sp = SchemaParser(validators={"multiple": multiple_validator})
>>> f = sp.parse("multiple(3)")
>>> f(6)
6
>>> f(5)
...
validr._exception.Invalid: not a multiple of 3
>>> f = sp.parse("multiple(3)&default=3")
>>> f(None)
3
>>>
```

string like validator should use `@validator(string=True)` decorator,
it will treat the empty string as None, more suitable for default and optional semantic.


#### Create regex validator:

```python
>>> from validr import build_re_validator
>>> regex_time = r'([01]?\d|2[0-3]):[0-5]?\d:[0-5]?\d'
>>> time_validator = build_re_validr("time", regex_time)
>>> sp = SchemaParser(validators={"time":time_validator})
>>> f = sp.parse('time&default="00:00:00"')
>>> f("12:00:00")
'12:00:00'
>>> f("12:00:00123")
...
validr._exception.Invalid: invalid time
>>> f(None)
'00:00:00'
>>>
```


#### `mark_index` and `mark_key`:

`mark_index` and `mark_key` are used to add position infomations to ValidrError or it's subclass(eg: Invalid and SchemaError) object.

```python
from validr import mark_index, mark_key, ValidrError
try:
    with mark_index(0):
        with mark_key('key'):
            with mark_index(-1):  # `-1` means the position is uncertainty
                raise ValidrError('message')
except ValidrError as ex:
    print(ex.position)  # [0].key[], the `[]` is corresponding to mark_index(-1)
```


## Test

use tox:

    pip install tox
    tox

use pytest

    pip install pytest
    pytest


## Performance

    pip install -r requires-dev.txt
    python benchmark/benchmark.py benchmark

benchmark result in travis-ci:

```
        json:loads-dumps              1000
  jsonschema:draft3                   180
  jsonschema:draft4                   184
      schema:default                  41
  schematics:default                  51
      validr:default                  2384
      validr:use-refer-merge          2106
  voluptuous:default                  100
```

## License

MIT License
