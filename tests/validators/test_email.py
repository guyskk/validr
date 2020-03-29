from validr import T
from . import case


@case({
    T.email: {
        'valid': [
            '12345678@qq.com',
            'python@gmail.com',
            '123@163.com',
            'test-demo@vip.qq.com',
            'i+box@gmail.com',
        ],
        'invalid': [
            '123'
            '123@'
            '123@163'
            '123@@163.com'
            '123@163.'
            '123@163.com'
            '123@163com',
            '123 @163.com',
            '123@ 163.com',
            'qq.com',
            ' @163.com',
            '中文@qq.com',
            'i' * 256 + '@gmail.com',
            str,
            None,
            123,
        ],
        'expect': [
            (' 123@163.com', '123@163.com'),
            ('123@163.com ', '123@163.com'),
            (' 123@163.com  ', '123@163.com'),
        ]
    },
    T.email.optional: [
        ('', ''),
        (None, '')
    ],
})
def test_email():
    pass
