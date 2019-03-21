from validr import T
from . import case


@case({
    T.bool: [
        (True, True),
        ('True', True),
        ('true', True),
        ('TRUE', True),
        ('Yes', True),
        ('YES', True),
        ('yes', True),
        ('ON', True),
        ('on', True),
        ('Y', True),
        ('y', True),
        (1, True),
        ('1', True),
        (False, False),
        ('False', False),
        ('false', False),
        ('FALSE', False),
        ('No', False),
        ('NO', False),
        ('no', False),
        ('OFF', False),
        ('off', False),
        ('N', False),
        ('n', False),
        (0, False),
        ('0', False),
        [None, '']
    ],
    T.bool.default(False): [
        (None, False),
        ('', False),
    ],
})
def test_bool():
    pass
