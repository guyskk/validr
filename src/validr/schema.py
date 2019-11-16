"""
Schema and Compiler

schema is instance of Schema or object which has __schema__ attribute,
and the __schema__ is instance of Schema.

compiler can compile schema:

    compiler.compile(schema) -> validate function.

validate function has __schema__ attribute, it's also a schema.

the Builder's instance T can build schema.
in addition, T can be called directly, which convert schema-like things to
instance of Builder:

    T(JSON) -> Isomorph Schema
    T(func) -> Schema of validate func
    T(Schema) -> Copy of Schema
    T(Model) -> Schema of Model

Builder support schema slice:

    T[...keys] -> sub schema

relations:

    T(schema) -> T
    T.__schema__ -> Schema
"""
import json

from pyparsing import (
    Group, Keyword, Optional, StringEnd, StringStart, Suppress,
    ZeroOrMore, quotedString, removeQuotes, replaceWith,
    pyparsing_common, ParseBaseException,
)

from .validator import builtin_validators
from .exception import SchemaError, mark_index, mark_key


def _make_keyword(kwd_str, kwd_value):
    return Keyword(kwd_str).setParseAction(replaceWith(kwd_value))


def _define_value():
    TRUE = _make_keyword('true', True)
    FALSE = _make_keyword('false', False)
    NULL = _make_keyword('null', None)
    STRING = quotedString().setParseAction(removeQuotes)
    NUMBER = pyparsing_common.number()
    return TRUE | FALSE | NULL | STRING | NUMBER


def _define_element():
    VALIDATOR = pyparsing_common.identifier.setName('validator').setResultsName('validator')
    ITEMS = _define_value().setName('items').setResultsName('items')
    ITEMS_WRAPPER = Optional(Suppress('(') + ITEMS + Suppress(')'))
    PARAMS_KEY = pyparsing_common.identifier.setName('key').setResultsName('key')
    PARAMS_VALUE = _define_value().setName('value').setResultsName('value')
    PARAMS_VALUE_WRAPPER = Optional(Suppress('(') + PARAMS_VALUE + Suppress(')'))
    PARAMS_KEY_VALUE = Group(Suppress('.') + PARAMS_KEY + PARAMS_VALUE_WRAPPER)
    PARAMS = Group(ZeroOrMore(PARAMS_KEY_VALUE)).setName('params').setResultsName('params')
    return StringStart() + VALIDATOR + ITEMS_WRAPPER + PARAMS + StringEnd()


ELEMENT_GRAMMAR = _define_element()


def _dump_value(value):
    if value is None:
        return 'null'
    elif value is False:
        return 'false'
    elif value is True:
        return 'true'
    elif isinstance(value, str):
        return repr(value)  # single quotes by default
    else:
        return str(value)  # number


def _pair(k, v):
    return '{}({})'.format(k, _dump_value(v))


def _sort_schema_params(params):
    def key(item):
        k, v = item
        if k == 'desc':
            return 3
        if k == 'optional':
            return 2
        if k == 'default':
            return 1
        if isinstance(v, bool):
            return -1
        if isinstance(v, str):
            return -2
        else:
            return -3
    return list(sorted(params, key=key))


class Schema:

    def __init__(self, *, validator=None, items=None, params=None):
        self.validator = validator
        self.items = items
        self.params = params or {}

    def __eq__(self, other):
        if hasattr(other, '__schema__'):
            other = other.__schema__
        if not isinstance(other, Schema):
            return False
        return (self.validator == other.validator and
                self.items == other.items and
                self.params == other.params)

    def __hash__(self):
        params = tuple(sorted(self.params.items()))
        items = self.items
        if isinstance(items, dict):
            items = tuple(sorted(items.items()))
        return hash((self.validator, items, params))

    def __str__(self):
        return json.dumps(self.to_primitive(), indent=4,
                          ensure_ascii=False, sort_keys=True)

    def repr(self, *, prefix=True, desc=True):
        if not self.validator:
            return 'T' if prefix else ''
        ret = ['T'] if prefix else []
        if self.items is None:
            ret.append(self.validator)
        else:
            if self.validator == 'dict':
                keys = ', '.join(sorted(self.items)) if self.items else ''
                ret.append('{}({})'.format(self.validator, '{' + keys + '}'))
            elif self.validator == 'list':
                ret.append('{}({})'.format(self.validator, self.items.validator))
            else:
                ret.append(_pair(self.validator, self.items))
        for k, v in _sort_schema_params(self.params.items()):
            if not desc and k == 'desc':
                continue
            if v is False:
                continue
            if v is True:
                ret.append(k)
            else:
                ret.append(_pair(k, v))
        return '.'.join(ret)

    def __repr__(self):
        r = self.repr(prefix=False)
        return '{}<{}>'.format(type(self).__name__, r)

    def copy(self):
        schema = type(self)(validator=self.validator, params=self.params.copy())
        if self.validator == 'dict' and self.items is not None:
            items = {}
            for k, v in self.items.items():
                if isinstance(v, Schema):
                    v = v.copy()
                items[k] = v
        elif self.validator == 'list' and self.items is not None:
            if isinstance(self.items, Schema):
                items = self.items.copy()
            else:
                items = self.items
        else:
            items = self.items
        schema.items = items
        return schema

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self, memo):
        return self.copy()

    def to_primitive(self):
        if not self.validator:
            return None
        ret = []
        if self.validator in {'dict', 'list'} or self.items is None:
            ret.append(self.validator)
        else:
            ret.append(_pair(self.validator, self.items))
        for k, v in _sort_schema_params(self.params.items()):
            if v is False:
                continue
            if v is True:
                ret.append(k)
            else:
                ret.append(_pair(k, v))
        ret = '.'.join(ret)
        if self.validator == 'dict' and self.items is not None:
            ret = {'$self': ret}
            for k, v in self.items.items():
                if isinstance(v, Schema):
                    v = v.to_primitive()
                ret[k] = v
        elif self.validator == 'list' and self.items is not None:
            ret = [ret]
            if isinstance(self.items, Schema):
                ret.append(self.items.to_primitive())
            else:
                ret.append(self.items)
        return ret

    @classmethod
    def parse_element(cls, text):
        if text is None:
            raise SchemaError("can't parse None")
        text = text.strip()
        if not text:
            raise SchemaError("can't parse empty string")
        try:
            result = ELEMENT_GRAMMAR.parseString(text, parseAll=True)
        except ParseBaseException as ex:
            msg = 'invalid syntax in col {} of {!r}'.format(ex.col, repr(ex.line))
            raise SchemaError(msg) from None
        validator = result['validator']
        items = None
        if 'items' in result:
            items = result['items']
        params = {}
        for item in result['params']:
            value = True
            if 'value' in item:
                value = item['value']
            params[item['key']] = value
        return cls(validator=validator, items=items, params=params)

    @classmethod
    def parse_isomorph_schema(cls, obj):
        if isinstance(obj, str):
            return cls.parse_element(obj)
        elif isinstance(obj, dict):
            e = cls.parse_element(obj.pop('$self', 'dict'))
            items = {}
            for k, v in obj.items():
                with mark_key(k):
                    items[k] = cls.parse_isomorph_schema(v)
            return cls(validator=e.validator, items=items, params=e.params)
        elif isinstance(obj, list):
            if len(obj) == 1:
                validator = 'list'
                params = None
                items = obj[0]
            elif len(obj) == 2:
                e = cls.parse_element(obj[0])
                validator = e.validator
                params = e.params
                items = obj[1]
            else:
                raise SchemaError('invalid list schema')
            with mark_index():
                items = cls.parse_isomorph_schema(items)
            return cls(validator=validator, items=items, params=params)
        else:
            raise SchemaError('{} object is not schema'.format(type(obj)))


class Compiler:

    def __init__(self, validators=None, is_dump=False):
        self.validators = builtin_validators.copy()
        if validators:
            self.validators.update(validators)
        self.is_dump = is_dump

    def compile(self, schema):
        if hasattr(schema, '__schema__'):
            schema = schema.__schema__
        if not isinstance(schema, Schema):
            raise SchemaError('{} object is not schema'.format(type(schema)))
        if not schema.validator:
            raise SchemaError('incomplete schema')
        validator = self.validators.get(schema.validator)
        if not validator:
            raise SchemaError('validator {!r} not found'.format(schema.validator))
        return validator(self, schema)


_BUILDER_INIT = 'init'
_EXP_ATTR = 'expect-attr'
_EXP_ATTR_OR_ITEMS = 'expect-attr-or-items'
_EXP_ATTR_OR_CALL = 'expect-attr-or-call'


class Builder:

    def __init__(self, state=_BUILDER_INIT, *, validator=None,
                 items=None, params=None, last_attr=None):
        self._state = state
        self._schema = Schema(validator=validator, items=items, params=params)
        self._last_attr = last_attr

    @property
    def __schema__(self):
        return self._schema

    def __repr__(self):
        return self._schema.repr()

    def __str__(self):
        return self._schema.__str__()

    def __eq__(self, other):
        if hasattr(other, '__schema__'):
            other = other.__schema__
        return self._schema == other

    def __hash__(self):
        return self._schema.__hash__()

    def __getitem__(self, keys):
        if not self._schema.validator:
            raise ValueError('can not slice empty schema')
        if self._schema.validator != 'dict':
            raise ValueError('can not slice non-dict schema')
        if not isinstance(keys, (list, tuple)):
            keys = (keys,)
        schema = Schema(validator=self._schema.validator,
                        params=self._schema.params.copy())
        schema.items = {}
        items = self._schema.items or {}
        for k in keys:
            if k not in items:
                raise ValueError('key {!r} is not exists'.format(k))
            schema.items[k] = items[k]
        return T(schema)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError('{!r} object has no attribute {!r}'.format(
                type(self).__name__, name))
        if self._state == _BUILDER_INIT:
            return Builder(_EXP_ATTR_OR_ITEMS, validator=name)
        else:
            params = self._schema.params.copy()
            params[name] = True
            return Builder(
                _EXP_ATTR_OR_CALL, validator=self._schema.validator,
                items=self._schema.items, params=params, last_attr=name)

    def __call__(self, *args, **kwargs):
        if self._state == _BUILDER_INIT:
            return self._load_schema(*args, **kwargs)
        if self._state not in [_EXP_ATTR_OR_ITEMS, _EXP_ATTR_OR_CALL]:
            raise SchemaError('current state not callable')
        if self._state == _EXP_ATTR_OR_ITEMS:
            if args and kwargs:
                raise SchemaError("can't call with both positional argument and keyword argument")
            if len(args) > 1:
                raise SchemaError("can't call with more than one positional argument")
            if self._schema.validator == 'dict':
                items = args[0] if args else kwargs
            else:
                if kwargs:
                    raise SchemaError("can't call with keyword argument")
                if not args:
                    raise SchemaError('require one positional argument')
                items = args[0]
            items = self._check_items(items)
            params = self._schema.params
        else:
            if kwargs:
                raise SchemaError("can't call with keyword argument")
            if not args:
                raise SchemaError('require one positional argument')
            if len(args) > 1:
                raise SchemaError("can't call with more than one positional argument")
            param_value = self._check_param_value(args[0])
            items = self._schema.items
            params = self._schema.params.copy()
            params[self._last_attr] = param_value
        return Builder(_EXP_ATTR, validator=self._schema.validator,
                       items=items, params=params, last_attr=None)

    def _load_schema(self, obj):
        if hasattr(obj, '__schema__'):
            obj = obj.__schema__
        if isinstance(obj, Schema):
            obj = obj.copy()
        elif isinstance(obj, (str, list, dict)):
            obj = Schema.parse_isomorph_schema(obj)
        else:
            raise SchemaError('{} object is not schema'.format(type(obj)))
        if not obj.validator:
            state = _BUILDER_INIT
        elif not obj.items and not obj.params:
            state = _EXP_ATTR_OR_ITEMS
        else:
            state = _EXP_ATTR
        return Builder(state, validator=obj.validator,
                       items=obj.items, params=obj.params, last_attr=None)

    def _check_items(self, items):
        if self._schema.validator == 'dict':
            if not isinstance(items, dict):
                raise SchemaError('items must be dict')
            ret = {}
            for k, v in items.items():
                if hasattr(v, '__schema__'):
                    v = v.__schema__
                if not isinstance(v, Schema):
                    raise SchemaError('items[{}] is not schema'.format(k))
                ret[k] = v
        elif self._schema.validator == 'list':
            if hasattr(items, '__schema__'):
                items = items.__schema__
            if not isinstance(items, Schema):
                raise SchemaError('items is not schema')
            ret = items
        else:
            if not isinstance(items, (bool, int, float, str)):
                raise SchemaError('items must be bool, int, float or str')
            ret = items
        return ret

    def _check_param_value(self, value):
        if not isinstance(value, (bool, int, float, str)):
            raise SchemaError('param value must be bool, int, float or str')
        return value


T = Builder()
