from validr import T
from datetime import timedelta

from . import case


@case({
    T.timedelta: [
        (timedelta(seconds=10), '10s'),
        ('12h59s', '12h59s'),
        ('23h59m59s', '23h59m59s'),
        ('2d59m59s', '48h59m59s'),
        [
            '10x',
            '23:30:30',
            '2016-07-09T00:00:59.123000Z',
            None,
            '',
            object,
        ]
    ],
    T.timedelta.extended: [
        ('24h59m59s', '1d59m59s'),
        ('2d59m59s', '2d59m59s'),
        ('2mo59m59s', '2mo59m59s'),
    ],
    T.timedelta.object.optional: [
        ('12h59s', timedelta(hours=12, seconds=59)),
        ('', None),
    ],
    T.timedelta.optional: [
        (None, ''),
        ('', '')
    ],
})
def test_timedelta():
    pass
