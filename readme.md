# Validater

[![travis-ci](https://api.travis-ci.org/guyskk/validater.svg)](https://travis-ci.org/guyskk/validater) [![codecov](https://codecov.io/gh/guyskk/validater/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validater)

[中文](readme-zh-cn.md) [English](readme.md)

A simple,fast,extensible library for validating.

- Simple and readable schema
- 20%~40% speed compare with json.loads
- Can serialize any object
- Easy to create custom validators
- Accurate error messages, include reason and position

Note: Only support python 3.3+

## Overview

```python
from validater import SchemaParser

sp = SchemaParser()
validate = sp.parse({
    "id?int": "product ID",
    "name?str": "product name",
    "price?float&min=0&exmin": "product price",
    "tags": ["&minlen=1&unique", "str&desc=\"product tag\""]
})
data = validate({
    "id": 1,
    "name": "Surface Book",
    "price": 9.9,
    "tags": ["Laptop"]
})
print(data)
```

## Install

    pip install validater


## Schema syntax

[Isomorph-JSON-Schema](Isomorph-JSON-Schema.md)

## Usage

#### Validate simple data:

```python
>>> from validater import SchemaParser,Invalid
>>> sp = SchemaParser()
>>> f = sp.parse("int(0, 9)")
>>> f("3")
3
>>> f(-1)
...
validater.exceptions.Invalid: value must >= 0
>>> f("abc")
...
validater.exceptions.Invalid: invalid int
>>>
```

#### Validate complex data:

```python
>>> f = sp.parse({"userid?int(0,9)": "UserID"})
>>> user = {"userid": 15}
>>> f(user)
...
validater.exceptions.Invalid: value must <= 9 in userid
>>> class User:pass
...
>>> user = User()
>>> user.userid=5
>>> f(user)
{'userid': 5}
>>> user.userid = 15
>>> f(user)
...
validater.exceptions.Invalid: value must <= 9 in userid
>>> f = sp.parse({"friends":[{"userid?int(0,9)":"UserID"}]})
>>> f({"friends":[user,user]})
...
validater.exceptions.Invalid: value must <= 9 in friends[0].userid
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
validater.exceptions.SchemaError: shared 'userid' not found in user.userid
```

#### Mixin:

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
>>> f = sp.parse({"$self@size@border": "mixins"})
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

Note: Only dict schema can mixin, non-dict schema mixin will cause SchemaError on validating data. And don't mixin schemas which has same key.

#### Custom validater

`handle_default_optional_desc` decorater can make you validater support `default`, `optional`, `desc` params.

```python
>>> from validater.validaters import handle_default_optional_desc
>>> @handle_default_optional_desc()
... def multiple_validater(n):
...     def validater(value):
...         if value%n==0:
...             return value
...         else:
...             raise Invalid("not a multiple of %d"%n)
...     return validater
...
>>> validaters={"multiple":multiple_validater}
>>> sp = SchemaParser(validaters=validaters)
>>> f = sp.parse("multiple(3)")
>>> f(6)
6
>>> f(5)
...
validater.exceptions.Invalid: not a multiple of 3
>>> f = sp.parse("multiple(3)&default=3")
>>> f(None)
3
>>>
```

string like validater should use `@handle_default_optional_desc(string=True)` decorater,
it will treat empty string as null, more suitable for default and optional semantic.


#### Create regex validater:

```python
>>> from validater.validaters import build_re_validater
>>> regex_time = r'([01]?\d|2[0-3]):[0-5]?\d:[0-5]?\d'
>>> time_validater = build_re_validater("time", regex_time)
>>> sp = SchemaParser(validaters={"time":time_validater})
>>> f = sp.parse('time&default="00:00:00"')
>>> f("12:00:00")
'12:00:00'
>>> f("12:00:00123")
...
validater.exceptions.Invalid: invalid time
>>> f(None)
'00:00:00'
>>>
```


## Test

use tox:

    pip install tox
    tox

use pytest

    pip install pytest
    py.test

## Performance

    # benchmark
    python benchmark.py

    # profile
    python benchmark.py -p


## Other

validater is misspell, the correct spelling is validator, but validator is registered.


## License

MIT License
