from datetime import date
from validr import T
from . import case


@case({
    T.date: [
        (date(2016, 7, 9), '2016-07-09'),
        ('2016-07-09', '2016-07-09'),
        ('2016-7-9', '2016-07-09'),
        [
            '2016-13-09', '07-09', '16-07-09',
            '', None
        ]
    ],
    T.date.optional: [
        (None, ''),
        ('', '')
    ],
    T.date.format('%Y/%m/%d'): [
        (date(2016, 7, 9), '2016/07/09'),
        ('2016/07/09', '2016/07/09'),
        ('2016/7/9', '2016/07/09'),
        ['2016-07-09', '07/09']
    ]
})
def test_date():
    pass
