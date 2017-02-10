import sys

from util import case


@case({
    "int(0,9)": [
        (0, 0),
        (9, 9),
        ("5", 5),
        [-1, 10, "abc"]
    ],
    "int": [
        (sys.maxsize, sys.maxsize),
        (-sys.maxsize, -sys.maxsize),
        (0, 0),
        [sys.maxsize + 1, -sys.maxsize - 1, float('INF'), float('NAN')]
    ]
})
def test_int():
    pass
