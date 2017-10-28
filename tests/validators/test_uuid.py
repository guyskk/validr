import uuid
import pytest
from validr import T, Compiler, SchemaError
from . import case

_UUID_1 = '2049d70e-bbd9-11e7-aaa2-a0c5896f8c2c'
_UUID_4 = '905ab193-d74d-48e7-be30-c2554b78074a'


@case({
    T.uuid: {
        'valid': [
            '12345678-1234-5678-1234-567812345678',
            _UUID_1, _UUID_4
        ],
        'expect': [
            ('12345678123456781234567812345678', '12345678-1234-5678-1234-567812345678'),
            (uuid.UUID(_UUID_1), _UUID_1),
            (uuid.UUID(_UUID_4), _UUID_4),
        ],
        'invalid': [
            None,
            123,
            'abcd',
            'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
        ]
    },
    T.uuid.version(4): {
        'valid': [
            _UUID_4
        ],
        'invalid': [
            _UUID_1
        ]
    },
    T.uuid.version(1): {
        'valid': [
            _UUID_1
        ],
        'invalid': [
            _UUID_4
        ]
    },
})
def test_uuid():
    pass


def test_illegal_version():
    with pytest.raises(SchemaError):
        Compiler().compile(T.uuid.version(10))
