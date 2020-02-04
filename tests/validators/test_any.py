from validr import T
from . import case


@case({
    T.any: [
        (1, 1),
        ('', ''),
        ('hello', 'hello'),
        ([1, 2, 3], [1, 2, 3]),
        ({'key': 123}, {'key': 123}),
        (object, object),
        [
            None
        ]
    ],
    T.any.optional: [
        (None, None),
        ('', '')
    ],
})
def test_any():
    pass
