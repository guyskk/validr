# Validr

[![travis-ci](https://api.travis-ci.org/guyskk/validr.svg)](https://travis-ci.org/guyskk/validr) [![codecov](https://codecov.io/gh/guyskk/validr/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validr)

[中文](README-zh-cn.md) | [English](README.md)

A simple, fast, extensible python library for data validation.

- Simple and readable schema
- 10X faster than [jsonschema](https://github.com/Julian/jsonschema),
  40X faster than [schematics](https://github.com/schematics/schematics)
- Can validate and serialize any object
- Easy to create custom validators
- Accurate and friendly error messages

Note: Only support python 3.3+

## Overview

```python
from collections import namedtuple
from validr import T, Compiler

Person = namedtuple('Person', 'name website')
schema = T.dict(
    name=T.str.strip.desc('leading and trailing whitespaces will be striped'),
    website=T.url.optional.desc('website is optional'),
)

validate = Compiler().compile(schema)
guyskk = Person('  guyskk  ', 'https://github.com/guyskk')

print(validate(guyskk))
```

## Install

    pip install validr

## Schema syntax

### How to describe JSON data?

Essentially, all data can be described by function.

For example, a positive integer:

```python
def validate_int_plus(value):
    assert isinstance(value, int), 'invalid number'
    assert value > 0, 'number must > 0'
```

Another example, a string which max length is 120 chars:

```python
def validate_str_maxlen_120(value):
    assert isinstance(value, str), 'invalid string'
    assert len(value) <= 120, 'string too long'
```

Classify the validate functions, **validator** turns out.

For example, a integer validator which has max value and min value:

```python
def int_validator(min, max):
    def validate(value):
        assert isinstance(value, int), 'invalid number'
        assert value >= min, f'number must >= {min}'
        assert value <= max, f'number must <= {max}'
    return validate
```

Schema is just a represention of validator.

### How to represent validator?

After some surveing, I found a **Step-By-Step** syntax is suitable.

For example, a integer validator:

```
int
```

A min 0 integer validator：

```
int.min(0)
```

A min 0, max 100 interger validator:

```
int.min(0).max(100)
```

It can be detailed step by step, according to requirements.

In addition, if the param value is `True`, we can omit the param value.

```
int.optional(True) == int.optional
```

For list and dict validator, we can validate it's elements:

```
list( int.min(0).max(100) )

dict(
    key1=int.min(0).max(100),
    key2=str.maxlen(10),
)
```

### Write schema in Python

Since int, str, dict, list...etc is already defined in Python, we add `T.` prefix to validator name, eg:

```
T.int.min(0).max(100)
```

### Write schema in JSON

From a structural point of view, JSON data can be divided into 3 types:

- scalar: string number true false null.
- sequence: also known as array or list.
- mapping: a collection of name/value pairs, also known as object or dictionary.

Schema is also JSON, it describe JSON data by the 3 structures too. As a result, the schema was called **Isomorph-JSON-Schema**.

mapping use $self to describe self, other keys describe it's inner elements:

    {
        "$self": "schema",
        "key": "schema"
    }

sequence use first element to describe self, second element to describe inner elements:

    ["schema", Item]

a sequence can omit self-describe, only describe inner elements:

    [Item]

scalar use a string to describe self:

    "schema"

Note: the JSON syntax is for using schema between languages.


## Example

this is [actual data](http://json-schema.org/example1.html):

```json
{
    "id": 1,
    "name": "A green door",
    "price": 12.50,
    "tags": ["home", "green"]
}
```

and it's schema in Python:

```python
T.dict(
    id=T.int.desc('The unique identifier for a product'),
    name=T.str.desc('Name of the product'),
    price=T.float.exmin(0),
    tags=T.list(
        T.str.minlen(1)
    ).unique
)
```

schema in JSON:

```json
{
    "$self": "dict",
    "id": "int.desc('The unique identifier for a product')",
    "name": "str.desc('Name of the product')",
    "price": "float.exmin(0)",
    "tags": [
        "list.unique",
        "str.minlen(1)"
    ]
}
```


### Built-in validators

    # List
    list(minlen=0, maxlen=1024, unique=false, default=null, optional=false)

    # Dict
    dict(optional=false)

    # Integer
    int(min=-sys.maxsize, max=sys.maxsize, default=null, optional=false)

    # Boolean
    bool(default=null, optional=false)

    # Float, exmin: exclusive min value, exmax: exclusive max value
    float(min=-sys.float_info.max, max=sys.float_info.max,
          exmin=-sys.float_info.max, exmax=sys.float_info.max, default=null, optional=false)

    # String
    str(minlen=0, maxlen=1024*1024, escape=false,
        default=null, optional=false)

    # Date, Time and Datetime, the output is string
    # default format is ISO8601
    date(format="%Y-%m-%d", default=null, optional=false)
    time(format="%H:%M:%S", default=null, optional=false)
    datetime(format="%Y-%m-%dT%H:%M:%S.%fZ", default=null, optional=false)

    # Email address
    email(default=null, optional=false)

    # IP address
    ipv4(default=null, optional=false)
    ipv6(default=null, optional=false)

    # URL
    url(default=null, optional=false)

    # Phone number, allow `+86` prefix, only support 11 digits phone number
    phone(default=null, optional=false)

    # Chinese idcard
    idcard(default=null, optional=false)

All string-like validators(str,date,datetime,email...) should treat empty string as null.  
All bool type params' default value is false,
custom validators should follow this guideline.

## Usage

### Schema

Schema has 2 syntaxs：Python and JSON.

```python
from validr import T, IsomorphSchema

schema1 = T.dict(
    id=T.int.desc('The unique identifier for a product'),
    name=T.str.desc('Name of the product'),
    price=T.float.exmin(0),
    tags=T.list(
        T.str.minlen(1).unique
    )
)

schema2 = IsomorphSchema({
    "$self": "dict",
    "id": "int.desc('The unique identifier for a product')",
    "name": "str.desc('Name of the product')",
    "price": "float.exmin(0)",
    "tags": [
        "list",
        "str.minlen(1).unique"
    ]
})

# they are equalment
assert schema1 == schema2
# the same content after convert to JSON string
assert str(schema1) == str(schema2)
# the same content after convert to python primitive
assert schema1.to_primitive() == schema2.to_primitive()
# is hashable，can be dict's key
assert hash(schema1) == hash(schema2)
```

### Compiler

Schema should be compiled before validate data,
there are 2 reasons:

1. compile is slower than validate, and we only compile schema once, this can improve performance.
2. the schema can be extented on compile time, eg: custom validators.

```python
from validr import Compiler

compiler = Compiler()
validate = compiler.compile(schema)
```

### Validate

```python
>>> from validr import T, Compiler, Invalid
>>> f = Compiler().compile(T.int.min(0).max(9))
>>> f("3")
3
>>> f(-1)
...
validr._exception.Invalid: value must >= 0
>>> f("abc")
...
validr._exception.Invalid: invalid int
```

### Handle Exception

#### Exceptions

```
ValidrError
  - Invalid
  - SchemaError
```

#### Handle Invalid:

```python
f = Compiler().compile(
    T.dict(
        numbers=T.list(T.int)
    )
)
try:
    f({"numbers":[1,'x']})
except Invalid as ex:
    print(ex.message)
    print(ex.position)
>>>
invalid int
numbers[1]
>>>
```

#### Report error position:

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

### Custom validator:

`validator()` decorater is used to create validator, and it can make you validator support params `default`, `optional`, `desc`.

string like validator should use `@validator(string=True)` decorator,
it will treat the empty string as None, more suitable for default and optional semantic.

A general custom validator:

```python
from validr import T, validator

@validator(string=True)
def xxx_validator(compiler, items=None, some_param=None):
    """Custom validator

    Params:
        compiler: can be used for compile inner schema
        items: optional, and can only be scalar type, passed by schema in `T.validator(items)` form
        some_param: other params
    Returns:
        validate function
    """
    def validate(value):
        """Validate function

        Params:
            value: data to be validate
        Returns:
            valid value or converted value
        Raises:
            Invalid: value invalid
        """
        return value
    return validate

# use custom validators
compiler = Compiler(validators={
    # name: validator
    'xxx': xxx_validator,
})
```

Example, time interval validator:

```python
from validr import T, validator, SchemaError, Invalid, Compiler

UNITS = {'s':1, 'm':60, 'h':60*60, 'd':24*60*60}

def to_seconds(t):
    return int(t[:-1]) * UNITS[t[-1]]

@validator(string=False)
def interval_validator(compiler, min='0s', max='365d'):
    """Time interval validator, convert value to seconds

    Supported time units:
        s: seconds, eg: 10s
        m: minutes, eg: 10m
        h: hours, eg: 1h
        d: days, eg: 7d
    """
    try:
        min = to_seconds(min)
    except (IndexError,KeyError,ValueError):
        raise SchemaError('invalid min value') from None
    try:
        max = to_seconds(max)
    except (IndexError,KeyError,ValueError):
        raise SchemaError('invalid max value') from None
    def validate(value):
        try:
            value = to_seconds(value)
        except (IndexError,KeyError,ValueError):
            raise Invalid("invalid interval") from None
        if value < min:
            raise Invalid("interval must >= {} seconds".format(min))
        if value > max:
            raise Invalid("interval must <= {} seconds".format(max))
        return value
    return validate

compiler = Compiler(validators={"interval": interval_validator})
f = compiler.compile(T.interval.max('8h'))
>>> f('15m')
900
>>> f('15x')
...
validr._exception.Invalid: invalid interval
>>> f('10h')
...
validr._exception.Invalid: interval must <= 28800 seconds
>>> f = compiler.compile(T.interval.default('5m'))
>>> f(None)
300
>>> compiler.compile(T.interval.max('12x'))
...
validr._exception.SchemaError: invalid max value
```

Another example, enum validator:

```python
@validator(string=False)
def enum_validator(compiler, items):
    items = set(items.split())
    def validate(value):
        if value in items:
            return value
        raise Invalid('value must be one of {}'.format(items))
    return validate

compiler = Compiler(validators={'enum': enum_validator})
f = compiler.compile(T.enum("A B C D"))
>>> f('A')
'A'
>>>
```

Note：`items` can only be scalar type, so it's no ambiguity when convert schema to JSON.

#### Create regex validator:

```python
from validr import build_re_validator

regex_time = r'([01]?\d|2[0-3]):[0-5]?\d:[0-5]?\d'
time_validator = build_re_validator("time", regex_time)
compiler = Compiler(validators={"time": time_validator})
f = compiler.compile(T.time.default("00:00:00"))

>>> f("12:00:00")
'12:00:00'
>>> f("12:00:123")
...
validr._exception.Invalid: invalid time
>>> f(None)
'00:00:00'
>>>
```

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

## Develop

Validr is implemented by [Cython](http://cython.org/) since v0.14.0, it's 5X
faster than original pure python implemented.

**setup**:

It's better to use [virtualenv](https://virtualenv.pypa.io/en/stable/) or
similar tools to create isolated Python environment for develop.  

After that, install all dependencys:

```
pip install -r requires-dev.txt
pre-commit install
```

**build, test and benchmark**:
```
./bb.sh
```


## License

MIT License
