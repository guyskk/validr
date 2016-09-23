# Isomorph-JSON-Schema

[中文](Isomorph-JSON-Schema.md) [English](Isomorph-JSON-Schema-en.md)

Isomorph-JSON-Schema is used to describe JSON data struct. The greatest feature is schema has the same struct with JSON data(Isomorph), and the syntax is super concise, you can directly see the actual data struct from the Schema.

## Syntax

[JSON](http://json.org) has 3 struct: mapping, sequence, scalar.

From a structural point of view, all data can divided into 3 types:
- scalar: string number true false null.
- sequence: also known as array or list.
- mapping: a collection of name/value pairs, also known as object or dictionary.


### Validater function

If there is a general way to describe the 3 structs above,
the way is function(**validater function**).

In JSON, we can use string to represent validater function, eg:

    "int(0,9)&default=5"

Which means this validater function accept number between 0 and 9, default is 5.

The syntax is similar to QueryString in URL, can be named **ValidaterString**,
it's complete form is:

    "validater(arg1,arg2...)&key=value&..."

Among them:

- arg1, arg2...value is valid JSON value.
- if validater is dict or list, it can be omitted.
- if arg1, arg2...all is default value, the brackets may be omitted.
- if the value corresponding to key is true, just write &key, no need to write &key=true.

Because schema and JSON data is isomorph, so the 3 structs should be able to self-described:

mapping use special key to describe self, other keys describe it's inner content:

	{
		"$self": "ValidaterString",
		"key": "value"
	}

sequence use first element to describe self, second element to describe inner content:

	["ValidaterString", Item]

sequence can omit self describe, only describe inner content:

    [Item]

scalar use a string to describe self:

	"ValidaterString"

In mapping, if value is scalar, then describe value in the key(use ? split key and ValidaterString),
and write comment in the position of value(pre-described):

    {
        "key?ValidaterString": "desc"
    }

Let's have a look, this is [actual data](http://json-schema.org/example1.html):

    {
        "id": 1,
        "name": "A green door",
        "price": 12.50,
        "tags": ["home", "green"]
    }

and this is schema:

    {
        "$self": "desc / comment",
        "id？int": "product ID",
        "name?str": "product name",
        "price?float&min=0&exmin": "product price",
        "tags": ["&minlen=1&unique", "str&desc=\"product tag\""]
    }

Note that tags is sequence, in order to avoid ambiguity(Described later) can only self-described.


### Refer

Different schema may has same parts, assume there is a common schema, other schema need refer it, then can use refer syntax.

    "@shared"

    ["&unique", @shared"]

    {
        "key@shared": "desc of key"
    }

    {
        "$self@shared": "desc of this dict"
    }

the 'optional' param means the value is optional, regardless of
@shared is optional or not.

    {
        "key@shared&optional": "this value is optional"
    }


### Mixins

In mapping, you can combine multi schema:

    {
        "$self@shared1@shared2": "desc",
        "addition_key": ...
    }

there also a optional param, means the mapping is optional, regardless of
@shared is optional or not.

    {
        "$self@shared1@shared2&optional": "desc",
        "addition_key": ...
    }


### pre-described and self-described

Mentioned earlier, sequence can only self-described, otherwise will cause ambiguity.
mapping can only self-described too.

First of all, the 3 struct has ability of self-described, but in mapping,
if value is scalar, use pre-described is more convenient and practical.

In order to make schema unified, formulate that key-scalar can only pre-described,
and sequence, mapping can only self-described.

Consider all the situations, only $self, key-scalar, key-refer is pre-described,
other places is self-described.

that is:

    "int&default=0"  # self-described

    ["&minlen=1", "int&default=0"]  # self-described

    {  # self-described
        "$self&optional": "desc",  # pre-described
        "key?int&default=0": "desc",  # pre-described
        "key": ["&minlen=1", "int&default=0"],  # self-described
        "key": {  # self-described
            "$self&optional": "desc"
        }
    }

    "@shared"  # self-described

    ["&minlen=1", "@shared"]  # self-described

    {  # self-described
        "$self@shared": "desc",  # pre-described
        "key@shared": "desc",  # pre-described
        "key": {  # self-described
            "$self@shared": "desc"
        }
    }


### built-in validater

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

    # date and datetime, the output is string
    # default format is ISO8601, the same as JSON.stringify in Javascript
    date(format="%Y-%m-%d", default=null, optional=false)
    datetime(format="%Y-%m-%dT%H:%M:%S.%fZ", default=null, optional=false)

    # email address
    email(default=null, optional=false)

    # phone number
    phone(default=null, optional=false)

    # IPv4 address
    ipv4(default=null, optional=false)

    # chinese idcard
    idcard(default=null, optional=false)

    # URL
    url(default=null, optional=false)

All string like validater(str,date,datetime,email...) treat empty string as null,
all bool type params' default value is false,
custom validater should follow this guideline.
