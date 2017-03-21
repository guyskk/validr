from util import case


@case({
    'str': [
        ('中文', '中文'),
        ('123', '123'),
        (str('abc'), 'abc'),
        [None, '', b'', 123, b'abc', '中文'.encode('utf-8')]
    ],
    'str&default="中文"': [
        (None, '中文'),
        ('', '中文'),
        ('abc', 'abc')
    ],
    'str&minlen=1&maxlen=1': [
        ('中', '中'),
        ('a', 'a'),
        ['中文', 'ab', '']
    ],
    'str&minlen=2': [
        ['中', 'A']
    ],
    'str&escape': [
        ('中文', '中文'),
        ("&><'\"", '&amp;&gt;&lt;&#39;&#34;')
    ],
})
def test_str():
    pass
