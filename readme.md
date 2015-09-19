# validater 

validater can validate json/dict/list and **convert value to python object ** by schema

validater 可以依据 schema 校验 json/dict/list 并将值转换成相应的python对象


##install 安装

	pip install validater


## usage 用法

```python
>>> from validater import validate
>>> schema={
	"key":{
		"desc":"input a int value",
		"required":True,
		"validate":"int",
		"default":"123"
	},
	"list":[{
		"desc":"input a int value",
		"required":True,
		"validate":"int",
		"default":"123"
	}]
}
>>> obj={
	"key":"333",
	"list":["1","23","asd"]
}

>>> error,value=validate(obj,schema)
>>> print error
[('list.[2]', u"must be 'int': input a int value")]
>>> print value
{'list': [1, 23, None], 'key': 333}
```


## validate(obj, schema)

obj can be dict, list or just a value, 

if you want to validate json, you should loads json to dict or list first

return is `tuple(error,validated_value)`

- error is a list of `tupe(key,err_msg)`
- validated_value is a dict, it's struct is the same as schema, invalid value will be None


## schema format

```python
{
	"desc":"description",
	"required":True,
	"validate":"int",
	"default":"123"
}
```

- validate is required, desc/required/default is optional
- desc is msg which will add to err_msg
- default can be value or callable(without args)
- validate can be basestring or callable(see `add_validater`)
- nest is supported
- list should contain (only) one sub_schema(item)
- built-in validater

	|name           | valid value 
	|---------------|-----------------------------------
	|any            | anything
	|basestring     | basestring
	|unicode        | unicode
	|str            | str
	|list           | list
	|dict           | dict
	|bool           | bool
	|int            | int
	|long           | long
	|float          | float
	|datetime       | isoformat datetime.datetime
	|objectid       | bson.objectid.ObjectId
	|re_email       | email
	|re_ipv4        | ipv4
	|re_phone       | phone_number
	|re_idcard      | 身份证号
	|re_url         | url, support urls without 'http://'
	|re_name        | common_use_name [a-z or A-Z or 0-9 or _] and 4~16 chars 
    |safestr        | escape unsafe string

###some examples

value of datetime
```python
{
    "desc":"desc of the key",
    "required":True,
    "validate":"datetime",
    "default":datetime.utcnow,
}
```
list of datetime
```python
[{
    "desc":"desc of the key",
    "required":True,
    "validate":"datetime",
    "default":"default_value",
}]
```
nest schema
```python
{
    "key1":{
        "desc":"desc of the key",
        "required":True,
        "validate":"validater, eg datetime",
        "default":"default_value",
    },
    "key2":{
        "key_nest":{
            "desc":"desc of the key",
            "required":True,
            "validate":"datetime",
            "default":"default_value",
        },
        ...
    },
    "key_list":[{
            "desc":"desc of the key",
            "required":True,
            "validate":"datetime",
            "default":"default_value",
        }]
    ...
}   
```

**invalid** schema will cause `SchemaError` (list should contain (only) one item)
```python
[{
    "desc":"desc of the key",
    "required":True,
    "validate":"datetime",
    "default":"default_value",
},
{
    "desc":"desc of the key",
    "required":True,
    "validate":"datetime",
    "default":"default_value",
}]
```


## add_validater

```python
add_validater(name,validater)
```

validater is a callable object and return a tuple
```python
def validater(v):
	return (True/False, validated_value)
```

for example
```python
from validater import add_validater
def plus_int(v):
    try:
        return (int(v) > 0, int(v))
    except:
        return (False, None)
add_validater("+int", plus_int)

s = {
    "key": [{
        "desc": "plus int",
        "required": True,
        "validate": "+int"
    }]
}
obj = {"key": ["123", "0", "-123"]}
(error, value) = validate(obj, s)
print error
print value
```

## `ProxyDict` validate custome type 
###校验自定义类型的对象

ProxyDict can wrap custome type object and use it as dict

	ProxyDict(obj, types)

if you custome type object contain other custome type object, you can add custome type to types, then it will be auto proxy 

```python
class XX(object):

    """docstring for XX"""

    def __init__(self, xx):
        self.xx = xx

xx = XX("haha")
d = ProxyDict(xx)
schema={
	"xx":{"validate":"str"}
}
error,value = validate(d, schema)
```


## test 测试
	
	py.test

## license 

MIT License