# Validr

[![travis-ci](https://api.travis-ci.org/guyskk/validr.svg)](https://travis-ci.org/guyskk/validr) [![codecov](https://codecov.io/gh/guyskk/validr/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validr)

[English](README.md) | [中文](README-zh-cn.md)

简单，快速，可拓展的数据校验库。

- 简洁，易读的 Schema
- 比 [jsonschema](https://github.com/Julian/jsonschema) 快 10 倍，比 [schematics](https://github.com/schematics/schematics) 快 40 倍
- 能够校验&序列化任意类型对象
- 易于拓展自定义校验器
- 准确友好的错误提示

注意：仅支持 python 3.3+

## 概览

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

## 安装

    pip install validr

## Schema语法

### 如何描述JSON数据？

本质上，所有数据都可以用函数来描述。

比如，一个大于 0 的整数：

```python
def validate_int_plus(value):
    assert isinstance(value, int), 'invalid number'
    assert value > 0, 'number must > 0'
```

又如，一个最大长度为 120 个字符的字符串：

```python
def validate_str_maxlen_120(value):
    assert isinstance(value, str), 'invalid string'
    assert len(value) <= 120, 'string too long'
```

把这些函数分门别类，就有了各种 **校验器**。

比如，可以指定最大值和最小值的整数校验器：

```python
def int_validator(min, max):
    def validate(value):
        assert isinstance(value, int), 'invalid number'
        assert value >= min, f'number must >= {min}'
        assert value <= max, f'number must <= {max}'
    return validate
```

Schema 仅仅是校验器的一种表示方式。

### 如何表示校验器？

经过对比，我发现一种 **渐进表示法** 非常适合。

比如，整数校验器：

```
int
```

最小值为 0 的整数校验器：

```
int.min(0)
```

最小值为 0，最大值为 100 的整数校验器：

```
int.min(0).max(100)
```

它可以根据需要，不断地补充描述。

另外，如果参数值为 `True`，可以省略参数值：

```
int.optional(True) == int.optional
```

对于字典和列表，可以校验容器內的元素：

```
list( int.min(0).max(100) )

dict(
    key1=int.min(0).max(100),
    key2=str.maxlen(10),
)
```

### 用Python语法表示校验函数

因为 int, str, dict 等等在 Python 中已有特定的含义，
所以要给校验器名称加上 `T.` 前缀，例如：

```
T.int.min(0).max(100)
```

### 用JSON语法表示校验函数

JSON数据可以分为3种结构：

- 映射："名称/值"对的集合，也被理解为对象（object）或字典（dictionary）
- 序列：有序列表，也被理解为数组
- 标量：string number true false null

Schema本身也是JSON，也用这三种结构描述相应的数据，也因此称为 *同构的JSON-Schema*。

映射结构用$self描述自身，其余key描述字典里的内容：

    {
        "$self": "schema",
        "key": "schema"
    }

序列结构用第一个元素描述自身，第二个元素描述序列里的内容：

    ["schema", Item]

序列结构也可以省略第一个元素，即只描述序列里的内容，不描述自身。

    [Item]

标量结构用字符串描述自身：

    "schema"


注：JSON格式主要用于跨语言使用 Schema。

### Example

这是[实际数据](http://json-schema.org/example1.html)：

```json
{
    "id": 1,
    "name": "A green door",
    "price": 12.50,
    "tags": ["home", "green"]
}
```

对应Schema的Python语法表示:

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

对应Schema的JSON语法表示:

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

### 内置的校验函数

    列表
    list(minlen=0, maxlen=1024, unique=false, default=null, optional=false)

    字典
    dict(optional=false)

    整数
    int(min=-sys.maxsize, max=sys.maxsize, default=null, optional=false)

    布尔值
    bool(default=null, optional=false)

    实数，exmin:不包括最小值, exmax:不包括最大值
    float(min=-sys.float_info.max, max=sys.float_info.max,
          exmin=-sys.float_info.max, exmax=sys.float_info.max,
          default=null, optional=false)

    字符串
    str(minlen=0, maxlen=1024*1024, escape=false, strip=false,
        default=null, optional=false)

    日期和时间，输出结果为字符串，格式为ISO8601
    date(format="%Y-%m-%d", default=null, optional=false)
    time(format="%H:%M:%S", default=null, optional=false)
    datetime(format="%Y-%m-%dT%H:%M:%S.%fZ", default=null, optional=false)

    邮箱地址
    email(default=null, optional=false)

    IP地址
    ipv4(default=null, optional=false)
    ipv6(default=null, optional=false)

    网址
    url(scheme='http https', default=null, optional=false)

    手机号，支持 `+86` 开头，只支持 11 位手机号，不支持固定电话号码
    phone(default=null, optional=false)

    身份证号，只校验数字长度和 xX，不校验地址码和日期
    idcard(default=null, optional=false)

所有字符串类型的校验器(str,date,datetime,email...)，将空字符串视为null。  
所有布尔型参数默认值都是false，自定义校验函数需遵守此规定。

## 使用

### Schema

Schema有两种表示方法：Python语法和JSON语法。

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

# 两种表示方式是等价的
assert schema1 == schema2
# 转换成JSON字符串内容是一样的
assert str(schema1) == str(schema2)
# 转换成Python内置类型也是一样的
assert schema1.to_primitive() == schema2.to_primitive()
# 可Hash，可作为字典的Key
assert hash(schema1) == hash(schema2)
```

### Compiler

Schema需要编译后才能校验数据，这么做有两个原因：

1. 编译相对来说比较耗时的，并且编译只需要执行一次，这样可以提高性能
2. 编译过程中可以拓展Schema，比如自定义校验器

```python
from validr import Compiler

compiler = Compiler()
validate = compiler.compile(schema)
```

### 校验数据

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

### 处理异常

#### 异常类型

```
ValidrError
  - Invalid
  - SchemaError
```

#### 处理校验错误

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

#### 记录错误位置

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

### 自定义校验器

`validator()` 装饰器用于创建自定义的校验器，并使它自动支持 `default`, `optional`, `desc` 这几个参数。

字符串类型的校验器请用 `@validator(string=True)` ，这样会将空字符串视为 None，
更符合 default 和 optional 的语义。

校验器的一般写法：

```python
from validr import T, validator

@validator(string=True)
def xxx_validator(compiler, items=None, some_param=None):
    """自定义校验器

    Params:
        compiler: 可以用它编译内部校验器
        items: 可选，只能为标量类型，通过 T.validator(items) 形式的Schema指定
        some_param: 其他参数
    Returns:
        校验函数
    """
    def validate(value):
        """校验函数

        Params:
            value: 待校验的数据
        Returns:
            合法的值或处理后的值
        Raises:
            Invalid: 校验失败
        """
        return value
    return validate

# 使用自定义校验器
compiler = Compiler(validators={
    # 名称: 校验器
    'xxx': xxx_validator,
})
```

示例，时间间隔校验器：

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

另一个例子，枚举校验器：

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

注：`items` 只能为标量类型，这样是为了用JSON表示时无歧义。

#### 构建枚举校验器

```python
from validr import Compiler, T, build_enum_validator
from string import digits
digit_validator = build_enum_validator('digit', digits)
compiler = Compiler(validators={"digit": digit_validator})
f = compiler.compile(T.digit.default('0'))
>>> f('2')
'2'
>>> f('x')
...
validr._exception.Invalid: invalid digit, expect one of ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
```

#### 使用正则表达式构建校验器

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
