# coding:utf-8


class ProxyDict(dict):

    """ProxyDict 将普通对象包装成dict
        -obj 要代理的对象
        -types 要代理的类型，list of types needed proxy
        若obj的属性(obj.xy)的类型在types列表中，将会自动ProxyDict并返回
        -下划线开头的属性(obj._xy, obj.__xy)不会出现在dict中
    """

    def __init__(self, obj, types=[]):
        self.obj = obj
        self.proxy_types = types
        self.proxy_types.append(type(obj))
        self.update(self._todict())
        # super(ProxyDict, self).__init__(*arg, **kw)

    def _todict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, ProxyDict):
                d[k] = v._todict()
            else:
                d[k] = v
        return d

    def __getitem__(self, key):
        if hasattr(self.obj, key):
            item = getattr(self.obj, key)
            if isinstance(item, tuple(self.proxy_types)):
                return ProxyDict(item, self.proxy_types)
            else:
                return item
        else:
            raise KeyError(key)

    def __setitem__(self, key, item):
        setattr(self.obj, key, item)
        self.update(self._todict())

    def __delitem__(self, key):
        delattr(self.obj, key)
        self.update(self._todict())

    def has_key(self, k):
        return hasattr(self.obj, k)

    def keys(self):
        return [k for k in self.obj.__dict__.keys() if k[:1] != '_']

    def values(self):
        return [self[k] for k in self.keys()]

    def items(self):
        return [(k, self[k]) for k in self.keys()]

    def __iter__(self):
        return iter(self.keys())
