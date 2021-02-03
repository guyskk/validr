from validr import T
from . import case


_THREE_BYTES = '字'.encode('utf-8')


@case({
    T.bytes: [
        (b'123', b'123'),
        (b'', b''),
        (_THREE_BYTES * 1024 * 1024, _THREE_BYTES * 1024 * 1024),
        ['hello', 123],
    ],
    T.bytes.minlen(1).maxlen(1): [
        (b'a', b'a'),
        [b'ab', b'', _THREE_BYTES]
    ],
    T.bytes.optional: [
        (None, None),
        (b'', b''),
        (_THREE_BYTES, _THREE_BYTES),
    ],
})
def test_bytes():
    pass
