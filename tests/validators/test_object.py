from validr import T
import uuid
from datetime import date, time, datetime

from . import case


UUID4 = uuid.uuid4()
UUID5 = uuid.uuid5(uuid.NAMESPACE_URL, 'test')


@case({
    T.time.object.optional: [
        (time(0, 0, 0), time(0, 0, 0)),
        (time(12, 00, 59), time(12, 00, 59)),
        (time(12, 59, 59), time(12, 59, 59)),
        ('12:59:59', time(12, 59, 59)),
        ('', None),
        (None, None),
    ],
    T.date.object: [
        (datetime(2019, 1, 1), date(2019, 1, 1)),
        ('2019-01-01', date(2019, 1, 1)),
    ],
    T.datetime.object: [
        (datetime(2019, 1, 1, 23, 59, 59), datetime(2019, 1, 1, 23, 59, 59)),
        ('2019-01-01T23:59:59.0Z', datetime(2019, 1, 1, 23, 59, 59)),
    ],
    T.uuid.object.optional: [
        (UUID4, UUID4),
        (UUID5, UUID5),
        ('', None),
        (None, None),
    ],
})
def test_output_object():
    pass
