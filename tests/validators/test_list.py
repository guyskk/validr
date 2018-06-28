from validr import T
from . import case


@case({
    T.list(T.int): [
        ([], []),
        ([1, 2], [1, 2]),
        (range(3), [0, 1, 2]),
    ],
    T.list(T.int).optional: {
        'valid': [
            None,
            [],
        ],
        'invalid': [
            123,
        ]
    },
    T.list(T.int).unique: {
        'valid': [
            [1, 2, 3],
        ],
        'invalid': [
            [1, 2, '2'],
        ]
    },
    T.list(T.dict(key=T.int)).unique: {
        'valid': [
            [{'key': 1}, {'key': 2}],
        ],
        'invalid': [
            [{'key': 1}, {'key': 1}],
        ]
    },
    T.list(T.int).minlen(1).maxlen(3): {
        'valid': [
            [1],
            [1, 2, 3],
        ],
        'invalid': [
            [],
            [1, 2, 3, 4],
        ]
    }
})
def test_list():
    pass
