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
            ' whitespace '
        ]
    }
})
def test_slug():
    pass
