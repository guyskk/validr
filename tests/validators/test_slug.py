from validr import T
from . import case


@case({
    T.slug: {
        'valid': [
            'aaa',
            'aa-b-c',
            '123-abc'
        ],
        'invalid': [
            '-',
            'aa_b',
            'a--b',
            'a-',
            '-a',
            '中文',
            ' whitespace ',
            'x' * 256,
        ]
    },
    T.slug.maxlen(16): {
        'valid': ['x', 'x' * 16],
        'invalid': ['x' * 17]
    },
})
def test_slug():
    pass
