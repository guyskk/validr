# Validr

[![travis-ci](https://api.travis-ci.org/guyskk/validr.svg)](https://travis-ci.org/guyskk/validr) [![codecov](https://codecov.io/gh/guyskk/validr/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validr)

A simple, fast, extensible python library for data validation.

- Simple and readable schema
- 10X faster than [jsonschema](https://github.com/Julian/jsonschema),
  40X faster than [schematics](https://github.com/schematics/schematics)
- Can validate and serialize any object
- Easy to create custom validators
- Accurate and friendly error messages

简单，快速，可拓展的数据校验库。

- 简洁，易读的 Schema
- 比 [jsonschema](https://github.com/Julian/jsonschema) 快 10 倍，比 [schematics](https://github.com/schematics/schematics) 快 40 倍
- 能够校验&序列化任意类型对象
- 易于拓展自定义校验器
- 准确友好的错误提示

## Overview

```python
from validr import T, modelclass, asdict

@modelclass
class Model:
    """Base Model"""

class Person(Model):
    name=T.str.maxlen(16).desc('at most 16 chars')
    website=T.url.optional.desc('website is optional')

guyskk = Person(name='guyskk', website='https://github.com/guyskk')
print(asdict(guyskk))
```

## Install

Note: Only support python 3.4+

    pip install validr

## Document

https://github.com/guyskk/validr/wiki

## Performance

benchmark result in travis-ci:

```
--------------------------timeits---------------------------
        json:loads-dumps         10000 loops cost 0.214s
  jsonschema:draft3              10000 loops cost 1.249s
  jsonschema:draft4              10000 loops cost 1.242s
      schema:default              1000 loops cost 0.507s
  schematics:default              1000 loops cost 1.340s
      validr:default            100000 loops cost 0.951s
  voluptuous:default             10000 loops cost 0.531s
---------------------------scores---------------------------
        json:loads-dumps          1000
  jsonschema:draft3                171
  jsonschema:draft4                172
      schema:default                42
  schematics:default                16
      validr:default              2247
  voluptuous:default               403
```

## Develop

Validr is implemented by [Cython](http://cython.org/) since v0.14.0, it's 5X
faster than original pure python implemented.

**setup**:

It's better to use [virtualenv](https://virtualenv.pypa.io/en/stable/) or
similar tools to create isolated Python environment for develop.  

After that, install dependencys:

```
./bootstrap.sh
```

**build, test and benchmark**:

```
inv build
inv test
inv benchmark
```

## License

MIT License
