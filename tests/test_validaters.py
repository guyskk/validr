from validater import SchemaParser, Invalid
import pytest
from datetime import datetime, date

sp = SchemaParser()

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
    "str": [("", ""), ("中文", "中文"), ("123", "123"), (str("abc"), "abc")],
    "str&default=\"中文\"": [(None, "中文"), ("abc", "abc")],
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
    "email": tuple_items([
        "12345678@qq.com",
        "python@gmail.com",
        "123@163.com",
        "中文@qq.com",
        "test-demo@vip.qq.com",
        "i+box@gmail.com",
    ]),
    "phone": tuple_items(valid_phones),
    "ipv4": tuple_items(["0.0.0.0", "9.9.9.9", "99.99.99.99",
                         "29.29.29.29", "39.39.39.39",
                         "255.255.255.255", "199.199.199.199",
                         "192.168.191.1", "127.0.0.1"]),
    "idcard": tuple_items([
        "123456789012345",
        "123456789012341234",
        "12345678901234123X",
        "12345678901234123x"
    ]),
    "url": tuple_items([
        "http://tool.lu/regex/",
        "https://github.com/guyskk/kkblog",
        "https://avatars3.githubusercontent.com/u/6367792?v=3&s=40",
        "https://github.com",
        "www.google.com.hk"
    ])
}

schema_value_fails = {
    "bool": [None, "", "true", "false", 0, 1],
    "float": ["1.0.0", None, "", "a.b"],
    "float(0,1)": [-0.01, 1.01],
    "float(0,1)&exmin": [0, 0.0],
    "float(0,1)&exmax": [1, 1.0],
    "float(0,1)&exmin&exmax": [0.0, 1.0],
    "str": [None, 123, b"abc", "中文".encode("utf-8")],
    "str&minlen=1&maxlen=1": ["中文", "ab", ""],
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
    ],
    "phone": invalid_phones,
    "ipv4": [None, "", "127.0.0.", "127.0.0. ", ".0.0.1", " .0.0.1"
             "127.0.0.1 ", " 127.0.0.1", "127.0.0.", "127.0.0. 1"
             "x.1.1.1", "1.x.1.1", "1.1.x.1", "0.0.0.-",
             "256.0.0.0", "0.256.0.0", "0.0.256.0", "0.0.0.256",
             "001.001.001.001", "011.011.011.011", "01.01.01.01",
             "300.400.500.600", "00.00.00.00", "6.66.666.6666"
             ],
    "idcard": [
        "12345678901234",
        "1234567890123456",
        "12345678901234567",
        "12345678901234123 ",
        " 12345678901234123",
    ],
    "url": {
        None,
        "",
        "mail@qq.com",
        "google",
        "readme.md",
        "github.com",
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
def test_validaters_success(schema, value, expect):
    f = sp.parse(schema)
    assert f(value) == expect


@pytest.mark.parametrize("schema,value", params_fail)
def test_validaters_fail(schema, value):
    f = sp.parse(schema)
    with pytest.raises(Invalid):
        f(value)
