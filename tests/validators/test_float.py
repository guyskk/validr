import sys

from util import case


@case({
    "float": [
        ("0", 0.0),
        (-100, -100.0),
        [
            "1.x",
            sys.float_info.max * 2,
            -sys.float_info.max * 2,
            float('INF'),
        ]
    ],
    "float&default=1.0": [
        (None, 1.0),
        (2.0, 2.0),
    ],
    "float(0,1)": [
        (0.0, 0.0),
        (1.0, 1.0),
        [-0.01, 1.01]
    ],
    "float(0,1)&exmin&exmax": [
        (0.01, 0.01),
        (0.99, 0.99),
        [0.0, 1.0]
    ]
})
def test_float():
    pass
