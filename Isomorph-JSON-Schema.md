# 同构的JSON-Schema

同构的JSON-Schema(Isomorph-JSON-Schema)是用来描述JSON数据的格式，这种格式最大的特点就是Schema与实际JSON数据的结构完全相同，并且语法简洁，从Schema可以直观的看出实际数据的结构。

## 语法

[JSON](http://json.org/json-zh.html)有3种结构：映射，序列，标量。

[数据类型和Json格式-阮一峰](http://www.ruanyifeng.com/blog/2009/05/data_types_and_json.html)
> 从结构上看，所有的数据（data）最终都可以分解成三种类型：

> 第一种类型是标量（scalar），也就是一个单独的字符串（string）或数字（numbers），比如"北京"这个单独的词。

> 第二种类型是序列（sequence），也就是若干个相关的数据按照一定顺序并列在一起，又叫做数组（array）或列表（List），比如"北京，上海"。

> 第三种类型是映射（mapping），也就是一个名/值对（Name/value），即数据有一个名称，还有一个与之相对应的值，这又称作散列（hash）或字典（dictionary），比如"首都：北京"。


### 校验函数validater

如果用一种通用的方式同时描述3种结构，这种方式只有函数，即**校验函数**。
在JSON中，可以用一个字符串表示校验函数，例如：

    "int(0,9)&default=5"

表示这个校验函数接受0-9的整数，默认值是5。

这种格式类似于URL里面的QueryString，可以取名为**ValidaterString**，完整形式如下：

    "validater(arg1,arg2...)&key=value&..."

其中：

- arg1, arg2...value都是有效JSON值，即true/false是小写的，空值为null，字符串要加双引号。
- 如果validater是dict或list，可以省略，因为可以从JSON结构看出是dict还是list。
- 如果arg1, arg2...都是默认值，则括号可以省略。
- 如果key对应的value为true，只需写&key，不需要写&key=true。

因为Schema和JSON数据是同构的，所以这3种结构都需要能够自己描述自己(**自描述**)，即：

映射结构用特殊的key描述自身，其余key描述字典里的内容：

	{
		"$self": "ValidaterString",
		"key": "value"
	}

序列结构用第一个元素描述自身，第二个元素描述序列里的内容：

	["ValidaterString", Item]

序列结构也可以省略第一个元素，即只描述序列里的内容，不描述自身。

    [Item]

标量结构用字符串描述自身：

	"ValidaterString"

在映射结构中，如果value是标量，则在key中描述value(用？分隔key和ValidaterString)，value的位置写关于这个value介绍，即**前置描述**：

    {
        "key?ValidaterString": "desc"
    }

下面来用一下这种语法，这是实际数据：

    {
        "id": 1,
        "name": "A green door",
        "price": 12.50,
        "tags": ["home", "green"]
    }

这是对应的Schema:

    {
        "$self": "某种产品的信息",
        "id？int": "产品ID",
        "name?str": "名称",
        "price?float&min=0&exmin": "价格",
        "tags": ["&minlen=1&unique", "str&desc=\"标签\""]
    }

注意tags是序列结构，为了避免歧义（后面说明）只能用自描述。


### 引用refer

不同的Schema可能含有相同的部分，假设有一个公共的Schema，其他Schema需要引用它，可以使用引用语法。

    "@shared"

    ["&unique", @shared"]

    {
        "key@shared": "desc of key"
    }

    {
        "$self@shared": "desc of this dict"
    }

引用的optional参数，表示这个值是可选的，不管@shared是否可选。

    {
        "key@shared&optional": "this value is optional"
    }

### 混合mixins

在映射结构中可以多个Schema进行组合：

    {
        "$self@shared1@shared2": "desc",
        "addition_key": ...
    }

也可以加optional参数，表示这个映射是可选的，不管@shared是否可选。

    {
        "$self@shared1@shared2&optional": "desc",
        "addition_key": ...
    }


### 前置描述(pre-described)和自描述(self-described)

前面提到序列结构只能用自描述，否则会有歧义，映射结构也只能用自描述。

首先，这三种结构都有自描述的能力，但是在映射结构里面，key-标量中的标量用前置描述更方便实用。
为了使Schema的写法统一，规定key-标量中的标量只能用前置描述，序列结构和映射结构只能用自描述。

如果考虑所有的情况，只有 $self, key-标量, key-引用 这三个地方用前置描述()，其他地方都用自描述。

即：

    "int&default=0"  # 自描述

    ["&minlen=1", "int&default=0"]  # 自描述

    {  # 自描述
        "$self&optional": "desc",  # 前置描述
        "key?int&default=0": "desc",  # 前置描述
        "key": ["&minlen=1", "int&default=0"],  # 自描述
        "key": {  # 自描述
            "$self&optional": "desc"
        }
    }

    "@shared"  # 自描述

    ["&minlen=1", "@shared"]  # 自描述

    {  # 自描述
        "$self@shared": "desc",  # 前置描述
        "key@shared": "desc",  # 前置描述
        "key": {  # 自描述
            "$self@shared": "desc"
        }
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
    datetime(format="%Y-%m-%dT%H:%M:%S.%fZ", default=null, optional=false)

    邮箱地址
    email(default=null, optional=false)

    电话号码
    phone(default=null, optional=false)

    IPv4地址
    ipv4(default=null, optional=false)

    身份证号
    idcard(default=null, optional=false)

    网址
    url(default=null, optional=false)

所有字符串类型的校验器(str,date,datetime,email...)，将空字符串视为null。
所有布尔型参数默认值都是false，自定义校验函数需遵守此规定。
