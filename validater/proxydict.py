# coding:utf-8


class ProxyDict(dict):

    """ProxyDict 将普通对象包装成dict

    :param proxy_obj: 要代理的对象
    :param types: 要代理的类型，list of types needed proxy,
        若proxy_obj的属性(proxy_obj.xy)的类型在types列表中，将会自动ProxyDict并返回
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

    def __unicode__(self):
        return u'"%s"' % repr(self)
