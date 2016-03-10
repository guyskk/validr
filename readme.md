# validater 

![travis-ci](https://api.travis-ci.org/guyskk/validater.svg)

validater can validate and convert value to python object by schema, support python 2.7.x and python 3.3+

validater 可以依据 schema 校验数据并将数据转换成相应的 python 对象，支持 python 2.7.x 和 python 3.3+


## install

	pip install validater

## run test
    
    py.test

    or 
    
    tox

## usage

```python
>>> from validater import parse, validate
>>> validate('5',parse('int(0,9)&required&default=0'))
([], 5)
>>> validate('-1',parse('int(0,9)&required&default=0'))
([(u'', u"must be 'int(0, 9)'")], None)
>>> validate(None,parse('int(0,9)&required&default=0'))
([], 0)
>>> 
>>> snippet = 'int(0,9)&required&default=0','input a int value, >=0 and <= 9'
>>> schema = parse({'key':snippet,'list':[snippet]})
>>> obj={"key":None, "list":["1","23","asd"]}
>>> error,value=validate(obj,schema)
>>> error
[(u'list[1]', u"must be 'int(0, 9)': input a int value, >=0 and <= 9"), 
(u'list[2]', u"must be 'int(0, 9)': input a int value, >=0 and <= 9")]
>>> value
{'list': [1, None, None], 'key': 0}
>>> 
```


## parse(schema, validaters)

validaters is a dict contains all validaters, it will be default_validaters by default

schema has 5 styles:

1. string snippet
    
    ```
    'int(0,9)&required&default=0'
    ```

2. tuple snippet

    ```
    'int(0,9)&required&default=0', 'desc'
    ```

3. dict snippet

    ```
    {
        'validater':'int',
        'args':(0,9),
        'required':True,
        'default':0,
        'desc':'desc'
    }
    ```

4. list schema

    ```
    [snippet]
    ```

5. dict schema

    ```
    {
        'key':snippet,
        'list':[snippet],
        'inner':{
            'key':snippet
        }
    }
    ```

string snippet has 3 part
    
    ------------------------------------------
    |validater  |args   |kwargs              |
    ------------------------------------------
    |int        |(0,9)  |&required&default=0 |
    ------------------------------------------

*validater*: the name of validater

*args*: optional, the args passed to validater

*kwargs*: optional, the kwargs passed to validater, it's value is determine by eval()


built-in kwargs

*required*: is required or not, empty string is treated as missing

*default*: default value, it can be callable without args(used in dict snippet). default value will also be validated

*desc*: desc of the snippet




## validate(obj, schema)

obj can be dict, list or just a value, it should has the same struct as schema

schema is the return value of parse

return `tuple(error,value)`

*error*: a list of `tuple(key, msg)`

*value*: a dict, it's struct is the same as schema


## built-in validater

|name                         | valid value 
|---------------              |-----------------------------------
|any                          | anything
|str                          | six.string_types(basestring on py2, str on py3)
|unicode                      | six.text_type(unicode on py2, str on py3)
|bool                         | bool
|int(start,end)               | int value >=start and <= end
|+int                         | int value >=0
|float(start,end)             | float value >=start and <= end
|datetime(format,output,input)| format is `%Y-%m-%dT%H:%M:%S.%fZ` by default, **output** means datetime to string, **input** means string to datetime, if **both output and input is False**, convert to string if value is datetime, else convert string to datetime
|date(format,output,input)    | format is `%Y-%m-%d` by default, **output** means date/datetime to string, **input** means string/datetime to date, if **both output and input is False**, convert to string if value is date/datetime, else convert string/datetime to date
|email                        | email
|ipv4                         | ipv4
|phone                        | phone number
|idcard                       | idcard number of chinese
|url                          | url, support urls without 'http://'
|name(minlength,maxlength)    | name combine of chars in [a-zA-Z0-9_], and start with chars in [a-zA-Z], minlength is 4 and maxlength is 16 by defeault
|password(minlength,maxlength)| password combine of ascii chars, and don't has space chars, minlength is 6 and maxlength is 16 by defeault
|safestr                      | escape unsafe string: ` & > < ' " `


### examples

string snippet

```python
sche = "unicode&required&default='hello world'"
```

tuple snippet

```python
sche = "unicode&required&default='hello world'", "welcome words"
```

dict snippet

```python
from datetime import datetime
sche = {
    "desc":"a iso8601 format datetime string",
    "required":True,
    "validate":"datetime",
    "input":True,
    "default":datetime.utcnow,
}
```

list schema

```python
sche = ["int&required"]
sche = {'userid_list': ["int&required"]}
```

dict schema

```python
sche = {
    "page_num": ('+int&required&fefault=1', 'the page num'),
    "page_size": ('int(1,50)&required&fefault=10', 'the page size')
}   
```

reuse schema

```python
snippet = {"name": ("safestr","your name")}
schema = {
    "user1": snippet,
    "user2": snippet,
}
```

## custom validater

validater is a callable object and return a tuple

```python
def validater(v, args, kwargs):
    return (True/False, validated_value)
```

re_validater and type_validater

```python
from validater import re_validater,type_validater

# build a validater by regex_object
validater = re_validater(regex_object)

# build a validater by type or types
validater = type_validater(cls, empty='')
```

custom validaters

```python
from validater import default_validaters

my_validaters = {}
my_validaters.update(default_validaters)
# then you can use my_validaters as params of parse, 
# add_validater, remove_validater
```

add_validater and remove_validater

```python
from validater import add_validater, remove_validater

add_validater('name', validater, validaters=my_validaters)
remove_validater('name', validaters=my_validaters)
```



for example

```python
from validater import re_validater,type_validater
from validater import default_validaters
from validater import add_validater, remove_validater

my_validaters = {}
my_validaters.update(default_validaters)

year_validater = re_validater(re.compile(r"^\d{4}$"))
add_validater("year", year_validater, my_validaters)
add_validater("list", type_validater(list, empty=[]), my_validaters)

def abs_validater(v, debug=False):
    try:
        return True, abs(v)
    except:
        if debug:
            raise
        return False, None
add_validater('abs', abs_validater, my_validaters)

schema = parse("abs&required&debug", my_validaters)
err,val = validate(-1, schema)
```


## `ProxyDict` validate custome type 

ProxyDict can wrap custome type object and use it as dict

    ProxyDict(obj, types)

validate custome type 

```python
class User(object):

    def __init__(self, userid):
        self.userid = userid

sche = parse({
    'userid': "int&required",
    'friends': [{'userid': "int&required"}]})

jack, f1, f2 = User(0), User(1), User(2)
jack.friends = [f1, f2]
err, val = validate(jack, sche, proxy_types=[User])
```



## license 

MIT License