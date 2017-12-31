# Validr

[![travis-ci](https://api.travis-ci.org/guyskk/validr.svg)](https://travis-ci.org/guyskk/validr) [![codecov](https://codecov.io/gh/guyskk/validr/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validr)

[English](readme.md) | [中文](readme-zh-cn.md)

Note: 如果你对这个项目感兴趣，请看一下 [New schema syntax discussion](https://github.com/guyskk/validr/issues/15)，我打算废弃旧语法。

简单，快速，可拓展的数据校验库。

- 简洁，易读的 Schema
- 比 [jsonschema](https://github.com/Julian/jsonschema) 快 10 倍，比 [schematics](https://github.com/schematics/schematics) 快 40 倍
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

注意：只能后面的引用前面的，并且要使用 OrderedDict 代替 dict。

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

字符串类型的校验器请用 `@validator(string=True)` ，这样会将空字符串视为 None，
更符合 default 和 optional 的语义。

另一个例子：

```python
>>> @validator(string=False)
    def choice_validator(value, *choices):
        try:
            if value in choices:
                return value
        except:
            pass
        raise Invalid('invalid choice')
>>> sp = SchemaParser(validators={'choice': choice_validator})
>>> f = sp.parse('choice("A","B","C","D")')
>>> f('A')
'A'
>>>
```


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


#### `mark_index` 和 `mark_key`:

`mark_index` 和 `mark_key` 是用来向 ValidrError 或者它的子类对象
（例如：Invalid 和 SchemaError）中添加出错位置信息。

```python
from validr import mark_index, mark_key, ValidrError
try:
    with mark_index(0):
        with mark_key('key'):
            with mark_index(-1):  # `-1` 表示位置不确定
                raise ValidrError('message')
except ValidrError as ex:
    print(ex.position)  # [0].key[], 其中的 `[]` 对应于 mark_index(-1)
```


## 内置校验函数

### idcard

内置的 idcard 校验函数只校验数字长度和 xX，不校验地址码和日期。

### phone

支持 `+86` 开头，支持校验手机号段，只支持 11 位手机号，不支持固定电话号码。

### 其他

见 Schema 语法。


## 性能

    pip install -r requires-dev.txt
    python benchmark/benchmark.py benchmark

travis-ci 上的测试结果:

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


## 开发

Validr 从 v0.14.0 开始用 [Cython](http://cython.org/) 实现，它比纯 Python 实现快了 5 倍。

**搭建开发环境**:

建议使用 [virtualenv](https://virtualenv.pypa.io/en/stable/) 或者类似的工具来创建
独立的 Python 开发环境。

之后，安装所有的依赖:

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
