from validr import T

from . import case


@case({
    T.enum(['A', 'B', 123]): [
        ('A', 'A'),
        ('B', 'B'),
        (123, 123),
        [
            'X',
            ' A',
            'A ',
            '123',
            None,
            '',
            object,
        ]
    ],
    T.enum('A B C'): [
        ('A', 'A'),
        ('B', 'B'),
        ['X', 123, None, ''],
    ],
    T.enum('A B C').optional: [
        ('', None),
        (None, None),
    ],
})
def test_enum():
    pass
