# Validr

[![travis-ci](https://api.travis-ci.org/guyskk/validr.svg)](https://travis-ci.org/guyskk/validr) [![codecov](https://codecov.io/gh/guyskk/validr/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validr)

[English](readme.md) [中文](readme-zh-cn.md)

简单，快速，可拓展的数据校验库。

- 比 [JSON Schema](http://json-schema.org) 更简洁的 Schema
- 速度是 [jsonschema](https://github.com/Julian/jsonschema) 的 10 倍
- 能够校验&序列化任意类型对象
- 实现自定义校验器非常容易
- 准确的错误提示，包括错误原因和位置

注意：仅支持 python 3.3+

## 概览

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

## 安装

    pip install validr


## Schema语法

[Isomorph-JSON-Schema](Isomorph-JSON-Schema-zh-cn.md)


## 用法

#### 校验简单数据

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

#### 校验复杂结构的数据

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

#### 处理校验错误

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

#### 引用(refer)

简单用法：

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

引用内部相互引用：

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

注意：只能后面的引用前面的，并且要使用OrderedDict代替dict。

```python
>>> shared = OrderedDict([
    ("user", {"userid@userid":"UserID"}),
    ("userid", "int(0,9)"),
])
>>> sp = SchemaParser(shared=shared)
...
validr._exception.SchemaError: shared 'userid' not found in user.userid
```

#### 混合(merge)

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

注意：不要混合有相同 key 的 Schema。


#### 自定义校验器

`validator()` 装饰器用于创建自定义的校验器，并使它自动支持 `default`, `optional`, `desc` 这几个参数。

```python
>>> from validr import validator
>>> @validator(string=False)
    def multiple_validator(value, n):
        try:
            if value%n == 0:
                return value
        except:
            pass
        raise Invalid("不是 %d 的倍数"%n)
>>> sp = SchemaParser(validators={"multiple": multiple_validator})
>>> f = sp.parse("multiple(3)")
>>> f(6)
6
>>> f(5)
...
validr._exception.Invalid: 不是 3 的倍数
>>> f = sp.parse("multiple(3)&default=3")
>>> f(None)
3
>>>
```

字符串类型的校验器请用 `@validator(string=True)` ，这样会将空字符串视为None，更符合default和optional的语义。


#### 使用正则表达式构建校验器

```python
>>> from validr import build_re_validator
>>> regex_time = r'([01]?\d|2[0-3]):[0-5]?\d:[0-5]?\d'
>>> time_validator = build_re_validator("time", regex_time)
>>> sp = SchemaParser(validators={"time":time_validator})
>>> f = sp.parse('time&default="00:00:00"')
>>> f("12:00:00")
'12:00:00'
>>> f("12:00:123")
...
validr._exception.Invalid: invalid time
>>> f(None)
'00:00:00'
>>>
```


## 关于内置校验函数

### idcard

内置的idcard校验函数只校验数字长度和xX，不校验地址码和日期。

### phone

支持 `+86` 开头，支持校验手机号段，只支持11位手机号，不支持固定电话号码。

### 其他

见Schema语法。


## 测试

用tox测试:

    pip install tox
    tox

用pytest测试:

    pip install pytest
    pytest


## 性能

    pip install -r requires-dev.txt
    python benchmark/benchmark.py benchmark

在我电脑上的测试结果(Intel(R) Core(TM) i5-3230M CPU @ 2.60GHz)

    ----------------time---the-result-of-timeit-----------------
    validr:default 3.9474168669985374
    validr:use-refer-merge 4.608337737998227
    json:loads-dumps 1.6587990809930488
    voluptuous:default 18.96944373799488
    schema:default 40.53439778399479
    schematics:default 34.1044494890084
    jsonschema:draft3 9.507412713996018
    jsonschema:draft4 9.953055930993287
    ------------speed---time(json)/time(case)*10000-------------
    validr:default 4202
    validr:use-refer-merge 3600
    json:loads-dumps 10000
    voluptuous:default 874
    schema:default 409
    schematics:default 486
    jsonschema:draft3 1745
    jsonschema:draft4 1667


## License

MIT License
