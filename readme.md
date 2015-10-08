# validater 

validater can validate json/dict/list and **convert value to python object ** by schema, support python 2.7.x and python 3.3+

**support py3 since v0.8.0, tested on py27 and py34**

validater 可以依据 schema 校验 json/dict/list 并将值转换成相应的python对象，支持 python 2.7.x 和 python 3.3+


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
- validate can be string or callable(see `add_validater`)
- empty string is treated as missing(NULL,None)
- nest is supported
- list should contain (only) one sub_schema(item)
- built-in validater

	|name           | valid value 
	|---------------|-----------------------------------
	|any            | anything
	|str            | six.string_types(basestring on py2, str on py3)
	|unicode        | six.text_type(unicode on py2, str on py3)
	|list           | list
	|dict           | dict
	|bool           | bool
	|int            | int
    |+int           | plus int
	|float          | float
	|datetime       | isoformat datetime.datetime
	|objectid       | bson.objectid.ObjectId, **removed since v0.7.4**
	|email          | email
	|ipv4           | ipv4
	|phone          | phone_number
	|idcard         | 身份证号
	|url            | url, support urls without 'http://'
	|name           | common_use_name [a-z or A-Z or 0-9 or _] and 4~16 chars in total
    |password       | password combine of letters, numbers, special chars, 6~16 chars in total
    |safestr        | escape unsafe string: ` & > < ' " `

    `objectid` validater removed since v0.7.4 because it is not common used.

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
# add a validater
add_validater(name,validater)
# build a validater by regex_object
re_validater(regex_object)
# build a validater which validate isinstance(v, cls)
type_validater(cls)
# get all validaters
validaters
```

validater is a callable object and return a tuple
```python
def validater(v):
	return (True/False, validated_value)
```

for example
```python
import re
from validater import add_validater, re_validater
re_http=re.compile(r'^(get|post|put|delete|head|options|trace|patch)$')
add_validater("http_method", re_validater(re_http))

s = {
    "key": [{
        "desc": "accept http method name",
        "required": True,
        "validate": "http_method"
    }]
}
obj = {"key": ["123", "get", "post"]}
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

    or 
    
    tox

## license 

MIT License