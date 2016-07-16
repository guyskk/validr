import json
from .exceptions import Invalid, SchemaError
from .validaters import builtin_validaters


class ValidaterString:

    def __init__(self, text):
        cut = text.find("?")
        if cut >= 0:
            is_refer = False
        else:
            cut = text.find("@")
            if cut >= 0:
                is_refer = True
            else:
                is_refer = False
        if cut > 0:
            key = text[:cut]
            text = text[cut + 1:]
        else:
            key = None
            if cut == 0:
                text = text[cut + 1:]

        cut = text.find("(")
        if cut >= 0:
            name = text[:cut]
            text = text[cut + 1:]
            cut = text.find(")")
            if cut < 0:
                raise SchemaError("missing ')'")
            args = text[:cut]
            text = text[cut + 1:]
        else:
            name = None
            args = None

        cut = text.find("&")
        if cut >= 0:
            if name is None:
                name = text[:cut]
            kwargs = text[cut + 1:]
        else:
            if name is None:
                name = text
            kwargs = None

        if is_refer:
            if (not name) or args or kwargs:
                raise SchemaError("invalid refer syntax")
        self.key = key
        self.is_refer = is_refer
        self.name = name
        self_args = []
        if args:
            for x in args.split(","):
                try:
                    self_args.append(json.loads(x))
                except ValueError:
                    raise SchemaError("invalid JSON value '%s'" % x)
        self.args = tuple(self_args)
        self.kwargs = {}
        if kwargs:
            for kv in kwargs.split("&"):
                cut = kv.find("=")
                if cut >= 0:
                    try:
                        self.kwargs[kv[:cut]] = json.loads(kv[cut + 1:])
                    except ValueError:
                        raise SchemaError(
                            "invalid JSON value '%s'" % kv)
                else:
                    self.kwargs[kv] = True

    def __repr__(self):
        return repr({
            "key": self.key,
            "is_refer": self.is_refer,
            "name": self.name,
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
                if vs.is_refer:
                    if vs.name not in self.shared:
                        raise SchemaError(
                            "shared '%s' not found" % vs.name)
                    refer = self.shared[vs.name]

                    def validater(value):
                        result = refer(value)
                        result.update(_validater(value))
                        return result
                    return validater
                else:
                    return _validater
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
            if vs.is_refer:
                if vs.name not in self.shared:
                    raise SchemaError("shared '%s' not found" % vs.name)
                return self.shared[vs.name]
            else:
                if vs.name in self.validaters:
                    validater = self.validaters[vs.name]
                elif vs.name in builtin_validaters:
                    validater = builtin_validaters[vs.name]
                else:
                    raise SchemaError("validater '%s' not found" % vs.name)
                _validater = validater(*vs.args, **vs.kwargs)
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
