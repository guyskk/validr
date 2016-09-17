import json
from .exceptions import Invalid, SchemaError
from .validaters import builtin_validaters


class ValidaterString:
    """ValidaterString

    eg::

        key?validater(args,args)&k&k=v
        key@xx@yy(args,args)&k&k=v

    Note: don't contain ',)' in args and '&=' in kwargs
    """

    def __init__(self, text):

        if text is None:
            raise SchemaError("can't parse None")

        # first: name, key?name, @refer or key@refer@refer
        # last: (args,args)&k&k=v or &k&k=v
        cuts = [text.find("("), text.find("&"), len(text)]
        cut = min([x for x in cuts if x >= 0])
        first, last = text[:cut], text[cut:]
        key = name = refers = None
        if first:
            if ("?" in first and "@" in first)\
                    or first[-1] in "?@":
                raise SchemaError("invalid syntax %s" % repr(first))

            if "@" in first:
                # key@refer@refer / key@@refer
                items = first.split("@")
                if items[0]:
                    key = items[0]
                refers = items[1:]
                if not all(refers):
                    raise SchemaError("invalid syntax %s" % repr(first))
            else:
                # key, key?name / key?name?name
                items = first.split("?")
                if len(items) == 2:
                    key, name = items
                elif len(items) == 1:
                    name = items[0]
                else:
                    raise SchemaError("invalid syntax %s" % repr(first))
        self.key = key
        self.name = name
        self.refers = refers

        text_args = text_kwargs = None
        if last and last[0] == "(":
            cut = last.find(")")
            if cut < 0:
                raise SchemaError("missing ')'")
            text_args = last[1:cut].rstrip(' ,')
            last = last[cut + 1:]
        if last:
            text_kwargs = last[1:]

        args = []
        if text_args:
            for x in text_args.split(","):
                try:
                    args.append(json.loads(x))
                except ValueError:
                    raise SchemaError(
                        "invalid JSON value in %s" % repr(text_args))
        self.args = tuple(args)

        kwargs = {}
        if text_kwargs:
            for kv in text_kwargs.split("&"):
                cut = kv.find("=")
                if cut >= 0:
                    try:
                        kwargs[kv[:cut]] = json.loads(kv[cut + 1:])
                    except ValueError:
                        raise SchemaError(
                            "invalid JSON value in %s" % repr(kv))
                else:
                    kwargs[kv] = True
        self.kwargs = kwargs

    def __repr__(self):
        return repr({
            "key": self.key,
            "name": self.name,
            "refers": self.refers,
            "args": self.args,
            "kwargs": self.kwargs
        })


def cut_schema_key(k):
    cut = k.find("?")
    if cut < 0:
        cut = k.find("@")
    if cut > 0:
        return k[:cut]
    else:
        return k


class MarkIndex:
    """Add current index to Invalid/SchemaError"""

    def __init__(self, items):
        self.items = items

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is Invalid or exc_type is SchemaError:
            if self.items is None:
                exc_val.mark_index(None)
            else:
                exc_val.mark_index(len(self.items))
        if exc_type is not None:
            return False


class MarkKey:
    """Add current key to Invalid/SchemaError"""

    def __init__(self, key):
        self.key = key

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is Invalid or exc_type is SchemaError:
            exc_val.mark_key(self.key)
        if exc_type is not None:
            return False


class SchemaParser:
    """SchemaParser

    :param validaters: custom validaters
    :param shared" shared schema
    """

    def __init__(self, validaters=None, shared=None):
        if validaters is None:
            self.validaters = {}
        else:
            self.validaters = validaters
        self.shared = {}
        if shared is not None:
            for k, v in shared.items():
                with MarkKey(k):
                    self.shared[k] = self.parse(v)

    def merge_validaters(self, validaters):
        def merged_validater(value):
            result = {}
            for v in validaters:
                result.update(v(value))
            return result
        return merged_validater

    def parse(self, schema):
        """Parse schema"""
        return self._parse(schema)

    def _parse(self, schema, vs=None):
        """Parse schema

        :param schema: schema
        :param vs: ValidaterString
        """
        if isinstance(schema, dict):
            inner = {}
            for k, v in schema.items():
                with MarkKey(cut_schema_key(k)):
                    if k[:5] == "$self":
                        # $self: 前置描述
                        vs = ValidaterString(k)
                        vs.kwargs["desc"] = v
                    else:
                        if isinstance(v, (dict, list)):
                            # 自描述
                            if any(char in k for char in"?@&()"):
                                raise SchemaError("should be self-described")
                            inner[k] = self._parse(v)
                        else:
                            # k-标量和k-引用：前置描述
                            if "?" not in k and "@" not in k:
                                raise SchemaError("should be pre-described")
                            inner_vs = ValidaterString(k)
                            inner[inner_vs.key] = self._parse(v, inner_vs)
            if vs:
                _validater = self.dict_validater(inner, *vs.args, **vs.kwargs)
                if not vs.refers:
                    return _validater
                else:
                    _validaters = []
                    for refer in vs.refers:
                        if refer not in self.shared:
                            raise SchemaError("shared '%s' not found" % refer)
                        _validaters.append(self.shared[refer])
                    _validaters.append(_validater)
                    return self.merge_validaters(_validaters)
            else:
                return self.dict_validater(inner)
        elif isinstance(schema, list):
            if len(schema) == 1:
                schema = schema[0]
            elif len(schema) == 2:
                vs = ValidaterString(schema[0])
                schema = schema[1]
            else:
                raise SchemaError("invalid length of list schema")
            with MarkIndex(None):
                inner = self._parse(schema)
                if vs:
                    return self.list_validater(inner, *vs.args, **vs.kwargs)
                else:
                    return self.list_validater(inner)
        else:
            if vs:
                vs.kwargs["desc"] = schema
            else:
                vs = ValidaterString(schema)
            if vs.refers:
                if len(vs.refers) >= 2:
                    raise SchemaError("multi refer not allowed")
                refer = vs.refers[0]
                if refer not in self.shared:
                    raise SchemaError("shared '%s' not found" % refer)
                _validater = self.shared[refer]
                if not vs.kwargs.get("optional"):
                    return _validater
                else:
                    def optional_shared_validater(value):
                        if value is None:
                            return None
                        else:
                            return _validater(value)
                    return optional_shared_validater
            else:
                if vs.name in self.validaters:
                    validater = self.validaters[vs.name]
                elif vs.name in builtin_validaters:
                    validater = builtin_validaters[vs.name]
                else:
                    raise SchemaError("validater '%s' not found" % vs.name)
                try:
                    _validater = validater(*vs.args, **vs.kwargs)
                except TypeError as ex:
                    raise SchemaError(str(ex))
                default = vs.kwargs.get("default", None)
                if default is not None:
                    try:
                        _validater(default)
                    except Invalid:
                        raise SchemaError("invalid default value")
                return _validater

    def dict_validater(self, inners, optional=False, desc=None):

        inners = inners.items()

        def validater(value):
            if value is None:
                if optional:
                    return None
                else:
                    raise Invalid("required")
            result = {}
            if isinstance(value, dict):
                for k, inner in inners:
                    with MarkKey(k):
                        v = inner(value.get(k, None))
                    result[k] = v
            else:
                for k, inner in inners:
                    with MarkKey(k):
                        v = inner(getattr(value, k, None))
                    result[k] = v
            return result
        return validater

    def list_validater(self, inner, minlen=0, maxlen=1024, unique=False,
                       optional=False, desc=None):
        def validater(value):
            if value is None:
                if optional:
                    return None
                else:
                    raise Invalid("required")
            if not isinstance(value, list):
                raise Invalid("not list")
            result = []
            for x in value:
                if len(result) >= maxlen:
                    raise Invalid("list length must <= %d" % maxlen)
                with MarkIndex(result):
                    v = inner(x)
                    if unique and v in result:
                        raise Invalid("not unique")
                result.append(v)
            if len(result) < minlen:
                raise Invalid("list length must >= %d" % minlen)
            return result
        return validater
