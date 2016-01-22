#!/usr/bin/env python
# coding: utf-8
from __future__ import absolute_import, print_function
"""
validater
~~~~~~~~~~~~~~~~~~~~~~~~~

.. versionchanged:: 0.9.2

    - rewrite validate
    - support validater params
    - ``schema`` removed
    - ``Schema``, ``parse`` added
"""
from validater.proxydict import ProxyDict
from validater.validaters import (default_validaters, re_validater, type_validater,
                                  add_validater, remove_validater)
from validater.schema import SchemaError, Schema, validate, parse, parse_snippet

__all__ = ["ProxyDict", "default_validaters", "re_validater", "type_validater",
           "add_validater", "remove_validater", "SchemaError", "Schema",
           "validate", "parse", "parse_snippet"]
