from datetime import timedelta

import pytest

from validr import T, SchemaError
from validr._vendor import durationpy

from . import case, compiler


def seconds(value):
    return durationpy.from_str(value).total_seconds()


@case({
    T.timedelta: [
        (timedelta(seconds=10), seconds('10s')),
        ('12h59s', seconds('12h59s')),
        ('23h59m59s', seconds('23h59m59s')),
        ('2d59m59s', seconds('48h59m59s')),
        [
            '10x',
            '23:30:30',
            '2016-07-09T00:00:59.123000Z',
            None,
            '',
            object,
        ]
    ],
    T.timedelta.min(10).max('24h'): [
        ('10s', seconds('10s')),
        ('24h', seconds('24h')),
        ['9s', 9.9, '24h1s']
    ],
    T.timedelta.object.optional: [
        ('12h59s', timedelta(hours=12, seconds=59)),
        ('', None),
    ],
    T.timedelta.optional: [
        (None, None),
        ('', None)
    ],
})
def test_timedelta():
    pass


def test_timedelta_schema():
    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.timedelta.min('1x'))
    assert 'min' in exinfo.value.message
    with pytest.raises(SchemaError) as exinfo:
        compiler.compile(T.timedelta.max('1x'))
    assert 'max' in exinfo.value.message
