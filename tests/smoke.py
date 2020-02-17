import os
from validr import T, modelclass, asdict


@modelclass
class Model:
    """Base Model"""


class Person(Model):
    name = T.str.maxlen(16).desc('at most 16 chars')
    website = T.url.optional.desc('website is optional')


def check_feature():
    data = dict(name='guyskk', website='https://github.com/guyskk')
    guyskk = Person(**data)
    assert asdict(guyskk) == data, 'smkoe test failed'


def check_pure_python():
    import validr._validator_py  # noqa: F401
    try:
        import validr._validator_c  # noqa: F401
    except ImportError:
        pass
    else:
        assert False, 'Pure Python mode not work!'


def check_c_python():
    import validr._validator_py  # noqa: F401
    import validr._validator_c  # noqa: F401


def check():
    check_feature()
    if os.getenv('VALIDR_SETUP_MODE') == 'py':
        check_pure_python()
    else:
        check_c_python()


if __name__ == "__main__":
    check()
