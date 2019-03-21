from validr import T
import uuid
from datetime import time

from . import case


UUID4 = uuid.uuid4()
UUID5 = uuid.uuid5(uuid.NAMESPACE_URL, 'test')


@case({
    T.time.object.optional: [
        (time(0, 0, 0), time(0, 0, 0)),
        (time(12, 00, 59), time(12, 00, 59)),
        (time(12, 59, 59), time(12, 59, 59)),
        ('', None),
        (None, None),
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
