# Isomorph-JSON-Schema

[中文](Isomorph-JSON-Schema-zh-cn.md) [English](Isomorph-JSON-Schema.md)

Isomorph-JSON-Schema is used to describe JSON data structure.   
The greatest feature is that schema has the same structure with JSON data(Isomorph), and the syntax is super concise, you can directly see the actual data structure from the schema.

Isomorph-JSON-Schema is not [JSON Schema](http://json-schema.org),
it is more simple and readable then JSON Schema.

## Example

this is [actual data](http://json-schema.org/example1.html):

    {
        "id": 1,
        "name": "A green door",
        "price": 12.50,
        "tags": ["home", "green"]
    }

and this is schema:

    {
        "$self": "product info",
        "id?int": "product ID",
        "name?str": "product name",
        "price?float&min=0&exmin": "product price",
        "tags": ["&minlen=1&unique", "str&desc=\"product tag\""]
    }


## Syntax

### ValidatorString

In JSON, we can use string to describe data, eg:

    "id?int"

The syntax is similar to QueryString in URL, can be named ValidatorString,
it's complete form is:

    "validator(arg1,arg2...)&key=value&..."

Among them:

- arg1, arg2...value is valid JSON value.
- if validator is dict or list, it can be omitted.
- if arg1, arg2...all is default value, the brackets can be omitted.
- if the value corresponding to key is true, just write &key, no need to write &key=true.

### Schema

From a structureural point of view, all data can be divided into 3 types:

- scalar: string number true false null.
- sequence: also known as array or list.
- mapping: a collection of name/value pairs, also known as object or dictionary.

mapping use $self to describe self, other keys describe it's inner content:

	{
		"$self": "ValidatorString",
		"key": "value"
	}

sequence use first element to describe self, second element to describe inner content:

	["ValidatorString", Item]

sequence can omit self describe, only describe inner content:

    [Item]

scalar use a string to describe self:

	"ValidatorString"

In mapping, if value is scalar, then describe value in the position of key,
and write comment in the position of value:

    {
        "key?ValidatorString": "desc"
    }


### Refer

Different schema may has same parts, assume there is a common schema, other schema need refer it, then can use refer syntax.

    "@shared"

    ["&unique", @shared"]

    {
        "key@shared": "desc of key"
    }

the 'optional' param means the value is optional.

    {
        "key@shared&optional": "this value is optional"
    }


### Mixin

In mapping, you can combine multi schemas:

    {
        "$self@shared1@shared2": "desc",
        "addition_key": ...
    }

the 'optional' param, means the mapping is optional.

    {
        "$self@shared1@shared2&optional": "desc",
        "addition_key": ...
    }


### built-in validator

    # sequence
    list(minlen=0, maxlen=1024, unique=false, default=null, optional=false)

    # mapping
    dict(optional=false)

    # integer
    int(min=-sys.maxsize, max=sys.maxsize, default=null, optional=false)

    # bool
    bool(default=null, optional=false)

    # float, exmin: exclude min value, exmax: exclude max value
    float(min=-sys.float_info.max, max=sys.float_info.max,
          exmin=false, exmax=false, default=null, optional=false)

    # string
    str(minlen=0, maxlen=1024*1024, escape=false,
        default=null, optional=false)

    # date, time and datetime, the output is string
    # default format is ISO8601, the same as JSON.stringify in Javascript
    date(format="%Y-%m-%d", default=null, optional=false)
    time(format="%H:%M:%S", default=null, optional=false)
    datetime(format="%Y-%m-%dT%H:%M:%S.%fZ", default=null, optional=false)

    # email address
    email(default=null, optional=false)

    # IP address
    ipv4(default=null, optional=false)
    ipv6(default=null, optional=false)

    # URL
    url(default=null, optional=false)

All string-like validators(str,date,datetime,email...) should treat empty string as null.  
All bool type params' default value is false,
custom validator should follow this guideline.
