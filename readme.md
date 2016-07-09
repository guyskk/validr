# validater 

![travis-ci](https://api.travis-ci.org/guyskk/validater.svg)

validater can validate and convert value to python object by schema, only support python 3.3+.

validater 可以依据 schema 校验数据并将数据转换成相应的 python 对象，仅支持 python 3.3+。

## install

    cd validater
    git checkout next
    pip install -e .

## usage

Basic:
```python
>>> from validater import SchemaParser
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

Pro:
```python
>>> f = sp.parse({"userid?int(0,9)": "UserID"})
>>> user = {"userid": 15}
>>> f(user)
...
validater.exceptions.Invalid: value must <= 9
>>> class User:pass
... 
>>> user = User()
>>> user.userid=5
>>> f(user)
{'userid': 5}
>>> user.userid = 15
>>> f(user)
...
validater.exceptions.Invalid: value must <= 9
>>>
```
## syntax

[同构JSON-Schema](https://github.com/ncuhome/backend-guide/blob/master/同构JSON-Schema.md)

## license 

MIT License
