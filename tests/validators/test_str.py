import pytest
from validr import T, SchemaError
from . import case, compiler


@case({
    T.str: [
        ('中文', '中文'),
        ('123', '123'),
        (str('abc'), 'abc'),
        (123, '123'),
        [None, '', b'', b'abc', '中文'.encode('utf-8')]
    ],
    T.str.default('中文'): [
        (None, '中文'),
        ('', '中文'),
        ('abc', 'abc')
    ],
    T.str.minlen(1).maxlen(1): [
        ('中', '中'),
        ('a', 'a'),
        ['中文', 'ab', '']
    ],
    T.str.minlen(2): [
        ['中', 'A']
    ],
    T.str.escape: [
        ('中文', '中文'),
        ("&><'\"", '&amp;&gt;&lt;&#39;&#34;')
    ],
    T.str.strip: [
        (' aaa ', 'aaa'),
        (' 中文 ', '中文'),
        [' ', '  ', None]
    ],
    T.str.match("[a-z]+"): [
        ('aaz', 'aaz'),
        [None, '', 'aA', 'zZ', 'a0', 'a-'],
    ]
})
def test_str():
    pass


def test_invalid_match_regex():
    with pytest.raises(SchemaError):
        compiler.compile(T.str.match('c++'))
