try:
    from ._exception_c import *  # noqa: F401,F403
except ImportError:
    from ._exception_py import *  # noqa: F401,F403
