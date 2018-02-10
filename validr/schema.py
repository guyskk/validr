"""
Schema and Compiler

schema is instance of Schema or object which has __schema__ attribute,
and the __schema__ is instance of Schema.

compiler can compile schema:

    compiler.compile(schema) -> validate function.

validate function also has __schema__ attribute, so it's also a schema.

the Builder is a subclass of Schema, we use it's instance T to build schema.
in addition, T can be called directly, which convert schema-like things to
instance of Schema:

    T(JSON) -> IsomorphSchema
    T(func) -> Schema of validate func
    T(Schema) -> Copy of Schema
    T(Model) -> Schema of Model
"""
import json
from collections import OrderedDict
from copy import copy

from pyparsing import (
    Group, Keyword, Optional, StringEnd, StringStart, Suppress,
    ZeroOrMore, quotedString, removeQuotes, replaceWith,
    pyparsing_common, ParseBaseException,
)

from ._validator import builtin_validators
from ._exception import SchemaError, mark_index, mark_key


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

    def __init__(self):
        self.validator = None
        self.items = None
        self.params = OrderedDict()

    def __eq__(self, other):
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

    def __repr__(self, simplify=False):
        if not self.validator:
            return '' if simplify else 'T'
        ret = [] if simplify else ['T']
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
            if simplify and k == 'desc':
                continue
            if v is False:
                continue
            if v is True:
                ret.append(k)
            else:
                ret.append(_pair(k, v))
        return '.'.join(ret)

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

    def copy(self):
        ret = Schema()
        ret.validator = self.validator
        ret.params = OrderedDict((k, copy(v)) for k, v in self.params.items())
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
            items = None
        ret.items = items
        return ret


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
            raise SchemaError(f'{type(schema)} object is not schema')
        if not schema.validator:
            raise SchemaError('incomplete schema')
        validator = self.validators.get(schema.validator)
        if not validator:
            raise SchemaError('validator {!r} not found'.format(schema.validator))
        return validator(self, schema)


class Element(Schema):

    def __init__(self, text):
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
        self.validator = result['validator']
        self.items = None
        if 'items' in result:
            self.items = result['items']
        self.params = {}
        for item in result['params']:
            value = True
            if 'value' in item:
                value = item['value']
            self.params[item['key']] = value


_BUILDER_INIT = 'init'
_EXP_ATTR = 'expect-attr'
_EXP_ATTR_OR_ITEMS = 'expect-attr-or-items'
_EXP_ATTR_OR_CALL = 'expect-attr-or-call'


class Builder(Schema):

    def __init__(self, state=_BUILDER_INIT, validator=None,
                 items=None, params=None, last_attr=None):
        self._state = state
        self.validator = validator
        self.items = items
        if params is None:
            self.params = OrderedDict()
        else:
            self.params = params
        self._last_attr = last_attr

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError('{!r} object has no attribute {!r}'.format(
                type(self).__name__, name))
        if self._state == _BUILDER_INIT:
            return Builder(_EXP_ATTR_OR_ITEMS, validator=name)
        else:
            if name in self.params:
                raise SchemaError('duplicated param {!r}'.format(name))
            params = self.params.copy()
            params[name] = True
            return Builder(_EXP_ATTR_OR_CALL, validator=self.validator,
                           items=self.items, params=params, last_attr=name)

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
            if self.validator == 'dict':
                items = args[0] if args else kwargs
            else:
                if kwargs:
                    raise SchemaError("can't call with keyword argument")
                if not args:
                    raise SchemaError('require one positional argument')
                items = args[0]
            items = self._check_items(items)
            params = self.params
        else:
            if kwargs:
                raise SchemaError("can't call with keyword argument")
            if not args:
                raise SchemaError('require one positional argument')
            if len(args) > 1:
                raise SchemaError("can't call with more than one positional argument")
            param_value = self._check_param_value(args[0])
            items = self.items
            params = self.params.copy()
            params[self._last_attr] = param_value
        return Builder(_EXP_ATTR, validator=self.validator,
                       items=items, params=params, last_attr=None)

    def _load_schema(self, obj):
        if hasattr(obj, '__schema__'):
            obj = obj.__schema__
        if isinstance(obj, Schema):
            return obj.copy()
        if isinstance(obj, (str, list, dict)):
            return IsomorphSchema(obj)
        raise SchemaError(f'{type(obj)} object is not schema')

    def _check_items(self, items):
        if self.validator == 'dict':
            if not isinstance(items, dict):
                raise SchemaError('items must be dict')
            ret = {}
            for k, v in items.items():
                if hasattr(v, '__schema__'):
                    v = v.__schema__
                if not isinstance(v, Schema):
                    raise SchemaError('items[{}] is not schema'.format(k))
                ret[k] = v
        elif self.validator == 'list':
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


class IsomorphSchema(Schema):

    def __init__(self, obj):
        if isinstance(obj, str):
            e = Element(obj)
            self.validator = e.validator
            self.items = e.items
            self.params = e.params
        elif isinstance(obj, dict):
            e = Element(obj.pop('$self', 'dict'))
            self.validator = e.validator
            self.params = e.params
            self.items = {}
            for k, v in obj.items():
                with mark_key(k):
                    self.items[k] = IsomorphSchema(v)
        elif isinstance(obj, list):
            if len(obj) == 1:
                e = Element('list')
                items = obj[0]
            elif len(obj) == 2:
                e = Element(obj[0])
                items = obj[1]
            else:
                raise SchemaError('invalid list schema')
            self.validator = e.validator
            self.params = e.params
            with mark_index():
                self.items = IsomorphSchema(items)
        else:
            raise SchemaError(f'{type(obj)} object is not schema')
