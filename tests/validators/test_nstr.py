from validr import T

from . import case


@case({
    T.nstr: [
        ('中文', '中文'),
        ('123', '123'),
        (0, '0'),
        ('', ''),
        [None, b'', b'abc', '中文'.encode('utf-8')]
    ],
    T.nstr.default('中文'): [
        (None, '中文'),
        ('', ''),
        ('abc', 'abc')
    ],
    T.nstr.optional: [
        ('中文', '中文'),
        (0, '0'),
        ('', ''),
        (None, None),
        [b'', b'abc']
    ],
})
def test_nstr():
    pass
