from validr import T
from . import case


@case({
    T.fqdn: {
        'valid': [
            'github.com',
            'www.google.com',
            'aaa-bbb.example-website.io',
            'a.bc',
            '1.2.3.4.com',
            '127.0.0.1',
            'xn--kxae4bafwg.xn--pxaix.gr',
            'a.b',
            'aaa.123',
            '999.999.999.999',
            'a23456789-123456789-123456789-123456789-123456789-123456789-123.b23.com',
            (
                'a23456789-a23456789-a234567890.a23456789.a23456789.a23456789.'
                'a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.'
                'a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.'
                'a23456789.a23456789.a23456789.a23456789.a23456789.a23456789.a2345678.com'
            ),
        ],
        'invalid': [
            'a' * 128 + '.' + 'b' * 128 + '.com',
            'a',
            'localhost',
            'a..bc',
            'ec2-35-160-210-253.us-west-2-.compute.amazonaws.com',
            'a23456789-123456789-123456789-123456789-123456789-123456789-1234.b23.com',
            'aaa_bbb.com',
            'a-',
            '-a',
            '中文',
        ]
    },
    T.fqdn.optional: [
        ('mx.gmail.com.', 'mx.gmail.com'),
        ('localhost.localdomain.', 'localhost.localdomain'),
        ('', ''),
        (None, ''),
    ]
})
def test_fqdn():
    pass
