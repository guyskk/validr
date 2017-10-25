from validr import T
from datetime import time

from . import case


@case({
    T.time: [
        (time(0, 0, 0), '00:00:00'),
        ('12:00:59', '12:00:59'),
        ('23:59:59', '23:59:59'),
        [
            '59:59',
            '24:00:00',
            '23:30:60',
            '23:60:30',
            '2016-07-09T00:00:59.123000Z',
            None,
            ''
        ]
    ],
    T.time.optional: [
        (None, ''),
        ('', '')
    ],
    T.time.format('%H/%M/%S'): [
        (time(23, 7, 9), '23/07/09'),
        ('12/59/00', '12/59/00'),
        ('23/7/9', '23/07/09')
    ]
})
def test_time():
    pass
