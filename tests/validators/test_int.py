from validr import T

from . import case

MAX_INT = 2**64 - 1


@case({
    T.int.min(0).max(9): [
        (0, 0),
        (9, 9),
        ('5', 5),
        [-1, 10, 'abc']
    ],
    T.int: [
        (MAX_INT, MAX_INT),
        (-MAX_INT, -MAX_INT),
        (0, 0),
        [MAX_INT + 1, -MAX_INT - 1, float('INF'), float('NAN')]
    ]
})
def test_int():
    pass
