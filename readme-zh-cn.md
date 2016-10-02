# Validr

[![travis-ci](https://api.travis-ci.org/guyskk/validr.svg)](https://travis-ci.org/guyskk/validr) [![codecov](https://codecov.io/gh/guyskk/validr/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validr)

[English](readme.md) [中文](readme-zh-cn.md)

简单，快速，可拓展的数据校验库。

- 比[JSON Schema](http://json-schema.org)更简洁，可读性更好的Schema
- 拥有标准库中 json.loads 20%~40% 的速度
- 能够序列化任意类型对象
- 实现自定义校验器非常容易
- 准确的错误提示，包括错误原因和位置

注意：仅支持 python 3.3+

## 概览

```python
from validr import SchemaParser

sp = SchemaParser()
validate = sp.parse({
    "id?int": "产品ID",
    "name?str": "名称",
    "price?float&min=0&exmin": "价格",
    "tags": ["&minlen=1&unique", "str&desc=\"标签\""]
})
data = validate({
    "id": 1,
    "name": "Surface Book",
    "price": 9.9,
    "tags": ["笔记本电脑", "平板电脑"]
})
print(data)
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
validr.exceptions.Invalid: value must >= 0
>>> f("abc")
...
validr.exceptions.Invalid: invalid int
>>>
```

#### 校验复杂结构的数据

```python
>>> f = sp.parse({"userid?int(0,9)": "UserID"})
>>> user = {"userid": 15}
>>> f(user)
...
validr.exceptions.Invalid: value must <= 9 in userid
>>> class User:pass
...
>>> user = User()
>>> user.userid=5
>>> f(user)
{'userid': 5}
>>> user.userid = 15
>>> f(user)
...
validr.exceptions.Invalid: value must <= 9 in userid
>>> f = sp.parse({"friends":[{"userid?int(0,9)":"UserID"}]})
>>> f({"friends":[user,user]})
...
validr.exceptions.Invalid: value must <= 9 in friends[0].userid
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
validr.exceptions.SchemaError: shared 'userid' not found in user.userid
```

#### 混合(mixin)

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

注意：  
只有字典结构的Schema才能混合，非字典结构的Schema混合会在校验数据时抛出SchemaError。  
另外，不要混合有相同key的Schema。


#### 自定义校验函数

`handle_default_optional_desc` 装饰器能让自定义的validr支持 `default`, `optional`, `desc` 这几个参数。

```python
>>> from validr.validators import handle_default_optional_desc
>>> @handle_default_optional_desc()
... def multiple_validator(n):
...     def validr(value):
...         if value%n==0:
...             return value
...         else:
...             raise Invalid("不是 %d 的倍数"%n)
...     return validr
...
>>> validators={"multiple":multiple_validator}
>>> sp = SchemaParser(validators=validators)
>>> f = sp.parse("multiple(3)")
>>> f(6)
6
>>> f(5)
...
validr.exceptions.Invalid: 不是 3 的倍数
>>> f = sp.parse("multiple(3)&default=3")
>>> f(None)
3
>>>
```

字符串类型的校验器请用 `@handle_default_optional_desc(string=True)` 装饰器，这样会将空字符串视为null，更符合default和optional的语义。


#### 使用正则表达式构建校验函数

```python
>>> from validr.validators import build_re_validator
>>> regex_time = r'([01]?\d|2[0-3]):[0-5]?\d:[0-5]?\d'
>>> time_validator = build_re_validator("time", regex_time)
>>> sp = SchemaParser(validators={"time":time_validator})
>>> f = sp.parse('time&default="00:00:00"')
>>> f("12:00:00")
'12:00:00'
>>> f("12:00:00123")
...
validr.exceptions.Invalid: invalid time
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
    py.test

## 性能

    # benchmark
    python benchmark.py

    # profile
    python benchmark.py -p


## License

MIT License
