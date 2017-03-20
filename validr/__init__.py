"""A simple,fast,extensible python library for data validation."""
from ._exception import Invalid, SchemaError, ValidrError, mark_index, mark_key
from ._validator import build_re_validator, builtin_validators, validator
from .schema import SchemaParser

__all__ = ('ValidrError', 'Invalid', 'SchemaError', 'mark_index', 'mark_key',
           'builtin_validators', 'build_re_validator', 'validator',
           'SchemaParser',)
