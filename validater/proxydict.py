#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
import six

# because most os's six version lower than v1.9.0, this always cause problems:
# 'module' object has no attribute 'python_2_unicode_compatible'
# and set install_requires=['six>=1.10.0'] in setup.py seems doesn't work,
# so I copy the python_2_unicode_compatible of six.py to here.


def python_2_unicode_compatible(klass):
    """
    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.
    """
    if six.PY2:
        if '__str__' not in klass.__dict__:
            raise ValueError("@python_2_unicode_compatible cannot be applied "
                             "to %s because it doesn't define __str__()." %
                             klass.__name__)
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


@python_2_unicode_compatible
class ProxyDict(dict):

    """ProxyDict dict proxy for any object

    :param proxy_obj: the object need to proxy
    :param types: list of types need to proxy, if the type of
                  proxy_obj.attribute in types，the attribute will be ProxyDict
    """

    def __init__(self, proxy_obj, types=None):
        self.proxy_obj = proxy_obj
        if types is None:
            self.proxy_types = []
        else:
            self.proxy_types = types
        self.proxy_types.append(type(proxy_obj))

    def __getitem__(self, key):
        if hasattr(self.proxy_obj, key):
            item = getattr(self.proxy_obj, key)
            if isinstance(item, tuple(self.proxy_types)):
                return ProxyDict(item, self.proxy_types)
            else:
                return item
        else:
            raise KeyError(key)

    def __setitem__(self, key, item):
        setattr(self.proxy_obj, key, item)

    def __delitem__(self, key):
        delattr(self.proxy_obj, key)

    def has_key(self, k):
        return k in self

    def keys(self):
        return dir(self.proxy_obj)

    def values(self):
        return [self.__getitem__(k) for k in self.keys()]

    def items(self):
        return [(k, self.__getitem__(k)) for k in self.keys()]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def __len__(self):
        return len(self.keys())

    def __contains__(self, item):
        return hasattr(self.proxy_obj, item)

    def __iter__(self):
        return iter(self.keys())

    def __repr__(self):
        return "ProxyDict(%s)" % repr(self.keys())

    def __str__(self):
        return '"%s"' % repr(self)
