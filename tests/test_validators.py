from validr import SchemaParser, Invalid
from validr.validators import handle_default_optional_desc
import pytest
from datetime import datetime, date, time

sp = SchemaParser()

# 手机号码测试用例
# http://blog.csdn.net/mr_lady/article/details/50245223
phone_headers = [133, 153, 180, 181, 189, 177, 130, 131, 132,
                 155, 156, 145, 185, 186, 176, 185, 134, 135,
                 136, 137, 138, 139, 150, 151, 152, 158, 159,
                 182, 183, 184, 157, 187, 188, 147, 178]
valid_phones = ["%d87654321" % x for x in phone_headers]
valid_phones.extend(["+86%s" % x for x in valid_phones[:5]])

invalid_phones = ["%d87654321" for x in range(10, 20)
                  if x not in [13, 14, 15, 17, 18]]
invalid_phones.extend([
    "1331234567",
    "1331234",
    "1331234567x",
    "13312345678x",
    "x1331234567",
    ".1331234567",
    "#1331234567",
    "13312345678 ",
    " 13312345678",
    "1331234 5678"
])

# 身份证号测试用例，只校验数字位数和xX
# http://id.8684.cn/
valid_idcards = [
    '210727198507128796', '652826198609135797',
    '430204197501228571', '652823197903247972',
    '44172319870827259X', '431302198807267352',
    '330701197107203338', '650103197605126317',
    '211403198001282511', '150900197608286734',
    '140421198905176811', '52030319770113997X',
    '210782198909223256', '430300197806216838',
    '370403197801263078', '371602198601115150',
    '230521197105208136', '120109198702188412',
    '430381198502107002', '34180119780914174X',
    '441700197702251887', '511500197606221220',
    '654226197901272021', '131003198406139543',
    '130431197702191284', '370705198407284720',
    '532600198802191668', '13063019850715310X',
    '320301198405188229', '370102197901149480',
    '210411198206281861', '620321198208147387',
    '150421197708131881', '310110198101127447',
    '652300199008251729', '370982198103104843',
    '431023198202192429', '532926198303176068',
    '44172319870827259x', '44172312340827259x'
]

# https://github.com/mc-zone/IDValidator
valid_idcards.extend([
    "431389760616601",
    "431389990616601",
    "431389000616601",
])


def tuple_items(items):
    return [(x, x) for x in items]

schema_value_expects = {
    "bool": [
        (True, True),
        (False, False),
    ],
    "bool&default=false": [(None, False)],
    "bool&optional": [(None, None)],
    "float": [("0", 0.0), ("0.0", 0.0), (1.0, 1.0), (-1, -1.0), (-1.0, -1.0)],
    "float&default=1.0": [(None, 1.0), (2.0, 2.0)],
    "float(0,1)": [(0.5, 0.5), (0.0, 0.0), (1.0, 1.0)],
    "str": [("中文", "中文"), ("123", "123"), (str("abc"), "abc")],
    "str&default=\"中文\"": [(None, "中文"), ("", "中文"), ("abc", "abc")],
    "str&minlen=1&maxlen=1": [("中", "中"), ("a", "a")],
    "str&maxlen=5&escape": [
        ("中文", "中文"),
        ("&><'\"", "&amp;&gt;&lt;&#39;&#34;")
    ],
    "datetime": [
        (datetime(2016, 7, 9), "2016-07-09T00:00:00.000000Z"),
        (datetime(2016, 7, 9, 14, 47, 30, 123), "2016-07-09T14:47:30.000123Z"),
        ("2016-07-09T00:00:00.000000Z", "2016-07-09T00:00:00.000000Z"),
        ("2016-07-09T00:00:00.123Z", "2016-07-09T00:00:00.123000Z"),
        ("2016-7-9T00:00:00.000000Z", "2016-07-09T00:00:00.000000Z")
    ],
    'datetime&format="%Y-%m-%d %H:%M:%S.%f"': [
        (datetime(2016, 7, 9), "2016-07-09 00:00:00.000000"),
        ("2016-07-09 00:00:00.123", "2016-07-09 00:00:00.123000"),
    ],
    "date": [
        (date(2016, 7, 9), "2016-07-09"),
        ("2016-07-09", "2016-07-09"),
        ("2016-7-9", "2016-07-09")
    ],
    'date&format="%Y/%m/%d"': [
        (date(2016, 7, 9), "2016/07/09"),
        ("2016/07/09", "2016/07/09"),
        ("2016/7/9", "2016/07/09")
    ],
    "time": [
        (time(0, 0, 0), "00:00:00"),
        ("12:00:59", "12:00:59"),
        ("23:59:59", "23:59:59")
    ],
    'time&format="%H/%M/%S"': [
        (time(23, 7, 9), "23/07/09"),
        ("12/59/00", "12/59/00"),
        ("23/7/9", "23/07/09")
    ],
    "email": tuple_items([
        "12345678@qq.com",
        "python@gmail.com",
        "123@163.com",
        "test-demo@vip.qq.com",
        "i+box@gmail.com",
    ]),
    "email&optional": [
        ("", ""),
        (None, "")
    ],
    "phone": tuple_items(valid_phones),
    "ipv4": tuple_items([
        "0.0.0.0", "9.9.9.9", "99.99.99.99",
        "29.29.29.29", "39.39.39.39",
        "255.255.255.255", "199.199.199.199",
        "192.168.191.1", "127.0.0.1"
    ]),
    "ipv6": tuple_items([
        "2001:0DB8:02de:0000:0000:0000:0000:0e13",
        "2001:DB8:2de:0000:0000:0000:0000:e13",
        "2001:DB8:2de:000:000:000:000:e13",
        "2001:DB8:2de:00:00:00:00:e13",
        "2001:DB8:2de:0:0:0:0:e13",
        "2001:DB8:2de::e13",
        "2001:0DB8:0000:0000:0000:0000:1428:57ab",
        "2001:0DB8:0000:0000:0000::1428:57ab",
        "2001:0DB8:0:0:0:0:1428:57ab",
        "2001:0DB8:0::0:1428:57ab",
        "2001:0DB8::1428:57ab",
        "0000:0000:0000:0000:0000:ffff:874B:2B34",
        "::ffff:135.75.43.52",
        "::1",
    ]),
    "idcard": tuple_items(valid_idcards),
    "url": tuple_items([
        "http://tool.lu/regex/",
        "https://github.com/guyskk/validator",
        "https://avatars3.githubusercontent.com/u/6367792?v=3&s=40",
        "https://github.com",
        "//cdn.bootcss.com/bootstrap/4.0.0-alpha.3/css/bootstrap.min.css"
    ])
}

schema_value_fails = {
    "bool": [None, "", "true", "false", 0, 1],
    "float": ["1.0.0", None, "", "a.b"],
    "float&default=1.0": ["", b""],
    "float(0,1)": [-0.01, 1.01],
    "float(0,1)&exmin": [0, 0.0],
    "float(0,1)&exmax": [1, 1.0],
    "float(0,1)&exmin&exmax": [0.0, 1.0],
    "str": [None, "", b"", 123, b"abc", "中文".encode("utf-8")],
    "str&minlen=1&maxlen=1": ["中文", "ab", ""],
    "str&minlen=3": ["中文", "ab"],
    "datetime": [
        "2016-07-09T00:00:00.000000",
        "2016-07-09 00:00:00.000000Z",
        "2016-07-09T00:00:00Z",
        "2016-07-09T00:00:60.123000Z",
    ],
    'datetime&format="%Y-%m-%d %H:%M:%S.%f"': [
        "2016-07-09T00:00:00.000000",
        "2016-07-09 00:00:00.000000Z",
        "2016-07-09 00:00:00",
    ],
    "date": [
        "2016-13-09",
        "07-09",
        "16-07-09"
    ],
    'date&format="%Y/%m/%d"': [
        "2016-07-09",
        "16/07/09",
    ],
    "time": [
        "59:59",
        "24:00:00",
        "23:30:60",
        "23:60:30",
        "2016-07-09T00:00:59.123000Z"
    ],
    'time&format="%H/%M/%S"': [
        "12:59:59",
        "16/07/09/30",
    ],
    "email": [
        "123"
        "123@"
        "123@163"
        "123@@163.com"
        "123@163."
        "123@163.com"
        "123@163com",
        " 123@163.com",
        "123 @163.com",
        "123@ 163.com",
        "123@163.com ",
        "qq.com",
        " @163.com",
        "中文@qq.com",
        None,
        datetime.utcnow()
    ],
    "phone": invalid_phones,
    "ipv4": [
        None, "", "127.0.0.", "127.0.0. ", ".0.0.1", " .0.0.1"
        "127.0.0.1 ", " 127.0.0.1", "127.0.0.", "127.0.0. 1"
        "x.1.1.1", "1.x.1.1", "1.1.x.1", "0.0.0.-",
        "256.0.0.0", "0.256.0.0", "0.0.256.0", "0.0.0.256",
        "001.001.001.001", "011.011.011.011", "01.01.01.01",
        "300.400.500.600", "00.00.00.00", "6.66.666.6666",
        "0.00.00.00", "0.0.0.00"
    ],
    "ipv6": [
        "2001::25de::cade",
    ],
    "idcard": [
        "43138976061660X",
        "43138976061660x",
        "21072719850712",
        "2107271985071287",
        "21072719850712879",
        "21072719850712879 ",
        " 21072719850712879",
        '210727198507128796x',
        '210727198507128796X',
    ],
    "url": {
        None,
        "",
        "mail@qq.com",
        "google",
        "readme.md",
        "github.com",
        "www.google.com"
    }
}

params_success = []
params_fail = []

for schema, value_expects in schema_value_expects.items():
    for value, expect in value_expects:
        params_success.append((schema, value, expect))

for schema, values in schema_value_fails.items():
    for value in values:
        params_fail.append((schema, value))


@pytest.mark.parametrize("schema,value,expect", params_success)
def test_validators_success(schema, value, expect):
    f = sp.parse(schema)
    assert f(value) == expect


@pytest.mark.parametrize("schema,value", params_fail)
def test_validators_fail(schema, value):
    f = sp.parse(schema)
    with pytest.raises(Invalid):
        f(value)


def test_custom_validator():
    @handle_default_optional_desc()
    def choice_validator():
        def validator(value):
            if value in "ABCD":
                return value
            raise Invalid("invalid choice")
        return validator
    sp = SchemaParser(validators={"choice": choice_validator})
    for value in "ABCD":
        assert sp.parse("choice")(value) == value
    assert sp.parse("choice&optional")(None) is None
