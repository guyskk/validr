# Isomorph-JSON-Schema

[English](Isomorph-JSON-Schema.md) [中文](Isomorph-JSON-Schema-zh-cn.md)

Isomorph-JSON-Schema(同构的JSON-Schema)是用来描述JSON数据的格式。  
这种格式最大的特点就是Schema与实际JSON数据的结构完全相同(Isomorph)，并且语法简洁，从Schema可以直观的看出实际数据的结构。

Isomorph-JSON-Schema不是[JSON Schema](http://json-schema.org)，它比JSON Schema更简洁，可读性更好。


## Example

这是[实际数据](http://json-schema.org/example1.html)：

    {
        "id": 1,
        "name": "A green door",
        "price": 12.50,
        "tags": ["home", "green"]
    }

这是对应的Schema:

    {
        "$self": "某种产品的信息",
        "id?int": "产品ID",
        "name?str": "名称",
        "price?float&min=0&exmin": "价格",
        "tags": ["&minlen=1&unique", "str&desc=\"标签\""]
    }


## ValidatorString

在JSON中，可以用一个字符串描述JSON数据，例如：

    "id?int"

这种格式类似于URL里面的QueryString，可以取名为ValidatorString，完整形式如下：

    "key?validator(arg1,arg2...)&key=value&..."

其中：

- arg1, arg2...value都是有效JSON值
- 如果validator是dict或list，可以省略
- 如果arg1, arg2...都是默认值，则括号可以省略
- 如果key对应的value为true，只需写&key，不需要写&key=true


## Schema

JSON数据可以分为3种结构：

- 映射："名称/值"对的集合，也被理解为对象（object）或字典（dictionary）
- 序列：有序列表，也被理解为数组
- 标量：string number true false null

映射结构用$self描述自身，其余key描述字典里的内容：

	{
		"$self": "ValidatorString",
		"key": "value"
	}

序列结构用第一个元素描述自身，第二个元素描述序列里的内容：

	["ValidatorString", Item]

序列结构也可以省略第一个元素，即只描述序列里的内容，不描述自身。

    [Item]

标量结构用字符串描述自身：

	"ValidatorString"

在映射结构中，如果value是标量，则在key的位置描述value，value的位置写关于这个value介绍：

    {
        "key?ValidatorString": "desc"
    }


### 引用(Refer)

不同的Schema可能含有相同的部分，假设有一个公共的Schema，其他Schema需要引用它，可以使用引用语法。

    "@shared"

    ["&unique", @shared"]

    {
        "key@shared": "desc of key"
    }

也可以加optional参数，表示这个值是可选的:

    {
        "key@shared&optional": "this value is optional"
    }

### 混合(Merge)

在映射结构中可以多个Schema进行组合:

    {
        "$self@shared1@shared2": "desc",
        "addition_key": ...
    }

也可以加optional参数，表示这个映射是可选的:

    {
        "$self@shared1@shared2&optional": "desc",
        "addition_key": ...
    }


### 内置的校验函数

    序列
    list(minlen=0, maxlen=1024, unique=false, default=null, optional=false)

    映射
    dict(optional=false)

    整数
    int(min=-sys.maxsize, max=sys.maxsize, default=null, optional=false)

    布尔值
    bool(default=null, optional=false)

    实数，exmin:是否不包括最小值, exmax:是否不包括最大值
    float(min=-sys.float_info.max, max=sys.float_info.max,
          exmin=false, exmax=false, default=null, optional=false)

    字符串
    str(minlen=0, maxlen=1024*1024, escape=false,
        default=null, optional=false)

    日期和时间，输出结果为字符串
    格式为ISO8601，与Javascript中JSON.stringify输出格式一致
    date(format="%Y-%m-%d", default=null, optional=false)
    time(format="%H:%M:%S", default=null, optional=false)
    datetime(format="%Y-%m-%dT%H:%M:%S.%fZ", default=null, optional=false)

    邮箱地址
    email(default=null, optional=false)

    IP地址
    ipv4(default=null, optional=false)
    ipv6(default=null, optional=false)

    网址
    url(default=null, optional=false)

所有字符串类型的校验器(str,date,datetime,email...)，将空字符串视为null。  
所有布尔型参数默认值都是false，自定义校验函数需遵守此规定。
