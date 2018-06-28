import sys
from validr import T
from . import case


@case({
    T.int.min(0).max(9): [
        (0, 0),
        (9, 9),
        ('5', 5),
        [-1, 10, 'abc']
    ],
    T.int: [
        (sys.maxsize, sys.maxsize),
        (-sys.maxsize, -sys.maxsize),
        (0, 0),
        [sys.maxsize + 1, -sys.maxsize - 1, float('INF'), float('NAN')]
    ]
})
def test_int():
    pass
