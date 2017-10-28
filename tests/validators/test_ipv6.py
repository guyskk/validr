from validr import T
from . import case


@case({
    T.ipv6: {
        'valid': [
            '2001:db8:2de::e13',
            '::1',
        ],
        'invalid': [
            None, 123,
            '2001::25de::cade',
            '127.0.0.1'
        ]
    }
})
def test_ipv6():
    pass
