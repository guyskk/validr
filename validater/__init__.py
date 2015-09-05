# coding:utf-8
# error,value=validate(obj,schema)
# add_validater(name,validater)
# ProxyDict(obj,types)
#

from .proxydict import ProxyDict
from .validaters import validaters, add_validater
from .validate import SchemaError, validate

__all__ = ["ProxyDict", "validaters", "add_validater",
           "SchemaError", "validate"]
