# Validater 

![travis-ci](https://api.travis-ci.org/guyskk/validater.svg) [![codecov](https://codecov.io/gh/guyskk/validater/branch/master/graph/badge.svg)](https://codecov.io/gh/guyskk/validater)

为RESTful API而生的校验器：

- 可以作为API文档，Schema即文档
- 可以用来校验请求参数
- 可以用来校验输出与API文档是否一致
- 可以用来序列化任意类型的对象

注意：仅支持 python 3.3+

## 安装

    pip install validater


## Schema语法

[同构的JSON-Schema](Isomorph-JSON-Schema.md)


## 用法

校验简单数据:
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

校验复杂结构的数据:
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

处理校验错误:

```python
>>> user.userid = 15
>>> try:
...     f({"friends":[user,user]})
... except Invalid as ex:
...     print(ex.message)
...     print(ex.position)
... 
value must <= 9
friends[0].userid
>>> 
```

引用:

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
>>> 
```

自定义校验函数:

```python
>>> from validater import handle_default_optional_desc
>>> @handle_default_optional_desc
... def multiple_validater(n):
...     def validater(value):
...         if value%n==0:
...             return value
...         else:
...             raise Invalid("不是 %d 的倍数"%n)
...     return validater
... 
>>> validaters={"multiple":multiple_validater}
>>> sp = SchemaParser(validaters=validaters)
>>> f = sp.parse("multiple(3)")
>>> f(6)
6
>>> f(5)
...
validater.exceptions.Invalid: 不是 3 的倍数
>>> f = sp.parse("multiple(3)&default=3")
>>> f(None)
3
>>> 
```

`handle_default_optional_desc` 装饰器能让自定义的validater支持default,optional,desc这几个参数。


## 关于内置校验函数

### email

参考：http://tool.lu/regex/

### idcard

完整校验身份证号的正则表达式非常复杂(还不一定正确)，如果通过代码逻辑判断结果能很准确，但(我感觉)没这种必要。内置的idcard校验函数只校验数字长度和xX，不校验地址码和日期。

验证身份证号的正则，可以参考这个(有Bug)：
http://blog.sina.com.cn/s/blog_491997ee0100avd2.html

如果需要解析身份证号信息，可以参考这个：
https://github.com/mc-zone/IDValidator

### phone

支持 `+86` 开头，支持校验手机号段，只支持11位手机号，不支持固定电话号码。
参考：http://tool.lu/regex/

### ipv4

支持完整校验IPv4地址。
参考：https://segmentfault.com/a/1190000004622152

### 其他

见Schema语法。


## 测试

用tox测试：

    pip install tox
    tox

用pytest测试：

    pip install pytest
    py.test


## 其他

validater是拼写错误的单词，正确的拼写是validator，但是validator这个名字已经被用掉了，所以继续用validater这个名字。


## License 

MIT License
