import sys
from validr import T
from . import case


@case({
    T.float: [
        ('0', 0.0),
        (-100, -100.0),
        [
            '1.x',
            sys.float_info.max * 2,
            -sys.float_info.max * 2,
            float('INF'),
        ]
    ],
    T.float.default(1.0): [
        (None, 1.0),
        (2.0, 2.0),
    ],
    T.float.min(0).max(1): [
        (0.0, 0.0),
        (1.0, 1.0),
        [-0.01, 1.01]
    ],
    T.float.min(0).exmin.max(1).exmax: [
        (0.01, 0.01),
        (0.99, 0.99),
        [0.0, 1.0]
    ],
    T.float.exmin(0).exmax(1): [
        (0.01, 0.01),
        (0.99, 0.99),
        [0.0, 1.0]
    ]
})
def test_float():
    pass
