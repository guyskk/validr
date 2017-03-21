import json

from ._exception import SchemaError, mark_index, mark_key
from ._schema import dict_validator, list_validator, merged_validator
from ._validator import builtin_validators


# -------------------------deprecated------------------------- #


class MarkKey(mark_key):
    """for compatibility with version 0.13.0 and before"""

    def __init__(self, *args, **kwargs):
        import warnings
        warnings.warn(DeprecationWarning(
            '`MarkKey` is deprecated, it will be '
            'removed in v1.0, please use `mark_key` instead.'
        ))
        super().__init__(*args, **kwargs)


class MarkIndex:
    """Add current index to Invalid/SchemaError"""

    def __init__(self, items):
        import warnings
        warnings.warn(DeprecationWarning(
            '`MarkIndex` is deprecated, it will be '
            'removed in v1.0, please use `mark_index` instead.'
        ))
        self.items = items

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        from ._exception import Invalid
        if exc_type is Invalid or exc_type is SchemaError:
            if self.items is None:
                exc_val.mark_index(None)
            else:
                exc_val.mark_index(len(self.items))
        if exc_type is not None:
            return False

# -------------------------deprecated------------------------- #


class ValidatorString:
    """ValidatorString

    eg::

        key?validator(args,args)&k&k=v
        key@xx@yy(args,args)&k&k=v

    Note: don't contain ',)' in args and '&=' in kwargs
    """

    def __init__(self, text):

        if text is None:
            raise SchemaError("can't parse None")

        # first: name, key?name, @refer or key@refer@refer
        # last: (args,args)&k&k=v or &k&k=v
        cuts = [text.find('('), text.find('&'), len(text)]
        cut = min([x for x in cuts if x >= 0])
        first, last = text[:cut], text[cut:]
        self.init_first_part(first)
        self.init_last_part(last)

    def init_first_part(self, first):
        key = name = refers = None
        if first:
            if ('?' in first and '@' in first) or first[-1] in '?@':
                raise SchemaError('invalid syntax %s' % repr(first))

            if '@' in first:
                # key@refer@refer / key@@refer
                items = first.split('@')
                if items[0]:
                    key = items[0]
                refers = items[1:]
                if not all(refers):
                    raise SchemaError('invalid syntax %s' % repr(first))
            else:
                # key, key?name / key?name?name
                items = first.split('?')
                if len(items) == 2:
                    key, name = items
                elif len(items) == 1:
                    name = items[0]
                else:
                    raise SchemaError('invalid syntax %s' % repr(first))
        self.key = key
        self.name = name
        self.refers = refers

    def init_last_part(self, last):
        text_args = text_kwargs = None
        if last and last[0] == '(':
            cut = last.find(')')
            if cut < 0:
                raise SchemaError("missing ')'")
            text_args = last[1:cut].rstrip(' ,')
            last = last[cut + 1:]
        if last:
            text_kwargs = last[1:]
        self.args = self.parse_args(text_args)
        self.kwargs = self.parse_kwargs(text_kwargs)

    def parse_args(self, text):
        if not text:
            return tuple()
        args = []
        for x in text.split(','):
            try:
                args.append(json.loads(x))
            except ValueError:
                raise SchemaError('invalid JSON value in %s' % repr(text))
        return tuple(args)

    def parse_kwargs(self, text):
        if not text:
            return {}
        kwargs = {}
        for kv in text.split('&'):
            cut = kv.find('=')
            if cut >= 0:
                try:
                    kwargs[kv[:cut]] = json.loads(kv[cut + 1:])
                except ValueError:
                    raise SchemaError('invalid JSON value in %s' % repr(kv))
            else:
                kwargs[kv] = True
        return kwargs

    def __repr__(self):
        return repr({
            'key': self.key,
            'name': self.name,
            'refers': self.refers,
            'args': self.args,
            'kwargs': self.kwargs
        })


def _schema_key(k):
    cut = k.find('?')
    if cut < 0:
        cut = k.find('@')
    if cut > 0:
        return k[:cut]
    else:
        return k


class SchemaParser:
    """SchemaParser

    Args:
        validators (dict): custom validators
        shared (dict): shared schema
    """

    def __init__(self, validators=None, shared=None):
        if validators is None:
            self.validators = {}
        else:
            self.validators = validators
        self.shared = {}
        if shared is not None:
            for k, v in shared.items():
                with mark_key(k):
                    self.shared[k] = self.parse(v)

    def parse(self, schema):
        """Parse schema"""
        return self._parse(schema)

    def _parse_dict(self, schema):
        inners = {}
        vs = None
        for k, v in schema.items():
            with mark_key(_schema_key(k)):
                if k[:5] == '$self':
                    if vs is not None:
                        raise SchemaError('multi $self not allowed')
                    vs = ValidatorString(k)
                    vs.kwargs['desc'] = v
                else:
                    if isinstance(v, (dict, list)):
                        if any(char in k for char in'?@&()'):
                            raise SchemaError('invalid key %s' % repr(k))
                        inners[k] = self._parse(v)
                    else:
                        if '?' not in k and '@' not in k:
                            raise SchemaError('missing validator or refer')
                        inner_vs = ValidatorString(k)
                        inners[inner_vs.key] = self._parse(v, inner_vs)
        inners = list(inners.items())
        if vs:
            if not vs.refers:
                return dict_validator(inners, *vs.args, **vs.kwargs)
            else:
                _validators = []
                for refer in vs.refers:
                    if refer not in self.shared:
                        raise SchemaError("shared '%s' not found" % refer)
                    validator = self.shared[refer]
                    if not validator.__name__.startswith('dict_validator'):
                        raise SchemaError("can't merge non-dict '@%s'" % refer)
                    _validators.append(validator)
                _validators.append(dict_validator(inners))
                return merged_validator(_validators, *vs.args, **vs.kwargs)
        else:
            return dict_validator(inners)

    def _parse_list(self, schema):
        vs = None
        if len(schema) == 1:
            schema = schema[0]
        elif len(schema) == 2:
            vs = ValidatorString(schema[0])
            schema = schema[1]
        else:
            raise SchemaError('invalid length of list schema')
        with mark_index(-1):
            inner = self._parse(schema)
            if vs:
                return list_validator(inner, *vs.args, **vs.kwargs)
            else:
                return list_validator(inner)

    def _parse_scalar(self, schema, vs):
        if vs:
            vs.kwargs['desc'] = schema
        else:
            vs = ValidatorString(schema)
        if vs.refers:
            # refer
            if len(vs.refers) >= 2:
                raise SchemaError('multi refers not allowed')
            refer = vs.refers[0]
            if refer not in self.shared:
                raise SchemaError("shared '%s' not found" % refer)
            _validator = self.shared[refer]
            # refer optional
            if not vs.kwargs.get('optional'):
                return _validator
            else:
                def optional_refer_validator(value):
                    if value is None:
                        return None
                    else:
                        return _validator(value)
                return optional_refer_validator
        else:
            if vs.name in self.validators:
                validator = self.validators[vs.name]
            elif vs.name in builtin_validators:
                validator = builtin_validators[vs.name]
            else:
                raise SchemaError("validator '%s' not found" % vs.name)
            return validator(*vs.args, **vs.kwargs)

    def _parse(self, schema, vs=None):
        """Parse schema

        Args:
            schema: schema
            vs: ValidatorString
        """
        if isinstance(schema, dict):
            return self._parse_dict(schema)
        elif isinstance(schema, list):
            return self._parse_list(schema)
        else:
            return self._parse_scalar(schema, vs)
