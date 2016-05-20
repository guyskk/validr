#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
import re
import json
from numbers import Number
from collections import defaultdict
from ijson.backends.python import basic_parse
from validater import default_validaters

pattern_schema = re.compile(r"^([^ \f\n\r\t\v()&]+)(\(.*\))?(&.*)?$")


class SchemaError(Exception):
    """Schema error"""


class Invalid(Exception):
    """Invalid data error"""

    def __init__(self, *args):
        super(Exception, self).__init__(*args)
        self.value = None

    @property
    def key(self):
        return '.'.join(self.args[1:][::-1])

    @property
    def reason(self):
        if self.args:
            return self.args[0]
        return ''

    def __str__(self):
        return '%s %s' % (self.key, self.reason)


class Parser:
    """Parse dict,list,scalar value,python object, yield (event, value)

    Usage::

        parser = Parser(schema).parse_value(obj)
        for event,value in parser:
            # do somthing

    The (event, value) has the same means as ijson.basic_parse. In addition,
    event can be 'scalar', which means scalar value.

    This parser will call schema.expect() to get expected keys of the schema,
    if expected keys exists, parser will yield expected keys other than
    all keys.

    When parse raw python object, the expected keys is attribute names of
    the object, parser will call getattr of the object. If no expected keys
    from schema, parser won't yield anything, because raw python object has
    lots of built-in attrs, most of them are not expectd.
    """

    def __init__(self, schema):
        self.schema = schema

    def parse_value(self, obj):
        expect = self.schema.expect()
        if expect is None:
            if obj is None:
                yield ('null', None)
            elif obj is True:
                yield ('boolean', True)
            elif obj is False:
                yield ('boolean', False)
            elif isinstance(obj, str):
                yield ('string', obj)
            elif isinstance(obj, Number):
                yield ('number', obj)
            elif isinstance(obj, list):
                for event in self.parse_array(obj):
                    yield event
            elif isinstance(obj, dict):
                for event in self.parse_object(obj):
                    yield event
            else:
                yield ('scalar', obj)
        else:
            for event in self.parse_object(obj):
                yield event

    def parse_array(self, obj):
        yield ('start_array', None)
        for x in obj:
            for event in self.parse_value(x):
                yield event
        yield ('end_array', None)

    def parse_object(self, obj):
        expect = self.schema.expect()
        yield ('start_map', None)
        if expect is None:
            if isinstance(obj, dict):
                for k, v in obj.items():
                    yield ('map_key', k)
                    for event in self.parse_value(v):
                        yield event
            else:
                pass
        else:
            for k in expect:
                yield ('map_key', k)
                if isinstance(obj, dict):
                    v = obj.get(k, None)
                else:
                    v = getattr(obj, k, None)
                for event in self.parse_value(v):
                    yield event
        yield ('end_map', None)


def parse_snippet(schema):
    """parse snippet

    usage::

        parse_snippet("int(0,100)&required&default=10")
        parse_snippet(("int(0,100)&required&default=10", desc))

    :param schema: schema snippet
    :return: a dict
    """
    if isinstance(schema, tuple):
        if len(schema) == 2:
            schema, desc = schema
            return _parse_string(schema, extra={'desc': desc})
        else:
            raise SchemaError('invalid schema snippet: tuple length must be 2')
    else:
        return _parse_string(schema)


def _parse_string(schema, extra=None):
    try:
        # if schema is dict but don't have 'validater' key,
        # will cause TypeError: expected string or buffer
        find = pattern_schema.findall(schema)
    except TypeError as e:
        raise SchemaError("invalid schema: possibly schema is dict but don't "
                          "have 'validater' key. \n%s" % repr(e))
    if not find:
        raise SchemaError('invalid schema: %s' % schema)
    validater, args, kwargs = find[0]

    result = {'validater': validater}
    if args:
        try:
            args = eval(args)
        except Exception as e:
            raise SchemaError(
                'invalid args: %s, %s\n%s' % (schema, args, repr(e)))
        if not isinstance(args, tuple):
            args = (args,)
        result['args'] = args

    if extra:
        result.update(extra)

    if kwargs:
        for kv in kwargs[1:].split('&'):
            kv = kv.split('=')
            if len(kv) == 1:
                k, v = kv[0], 'True'
            elif len(kv) == 2:
                k, v = kv
            else:
                raise SchemaError('invalid kwargs: %s, %s' % (schema, kv))
            if k == '':
                raise SchemaError('invalid kwargs: %s, %s' % (schema, kv))
            try:
                result[k] = eval(v)
            except Exception as e:
                raise SchemaError(
                    'invalid kwargs: %s, %s\n%s' % (schema, kv, repr(e)))
    return result


def is_empty(s):
    return s is None or s == str('')


class Schema:
    """Schema describe the struct of data, and keep validate state

    Usage::

        sche = Schema({"userid": "int"})
        # tell which keys it need
        print(sche.expect())  # ["userid"]
        sche.feed(('start_map', None))
        sche.feed(('map_key', 'userid'))
        sche.feed(('scalar', '123'))
        sche.feed(('end_map', None))
        print(sche.state)  # "stop"
        # print the result
        print(sche.obj)  # {"userid": 123}
        sche.reset()
        # the schema can be feed again

    Schema has a tree struct which is the same of the struct of data,
    every schema object is a node. Schema.data and Schema.json() can
    tell the struct of schema.

    There are 4 types of schema:

    - map, dict or key-value struct
    - array, list or array struct
    - scalar, scalar value
    - any, data struct determined after receive data

    Schema.sub is sub schema of this schema, for 'map' type schema, it's a
    dict of key:schema, for other type, it's schema object. for 'any' type
    schema, it's sub determined after receive data.

    Each schema is a state machine, there 7 state, see the figure on this
    folder. You can imagine each schema as a bag, the bag may has a hole
    (Schema.inner) pipe to another bag, and anything the bag received will
    drop into the inner bag until the inner bag is full.

    Once a bag received invalid data, it will raise a Invalid exception
    which contains error message and position(Schema.key).The outter bag
    catch the exception, append it's position then reraise, when the root
    schema catch the exception, looks it's positions and known where the
    invalid data in.

    'scalar' state will determined the actual data type, 'skip' state is
    used to skip(ignore) undesired key-value in 'map' type schema, 'inner'
    state will pipe any event to inner schema until inner schema stoped.
    In 'map_key' state and 'array' state, will link current Schema.obj
    with Schema.inner.obj, so the root schema's obj can link to all sub
    schema's obj.

    In addition, Schema.expect() can tell which keys it currently need,
    this allow outsides to choose better action.
    """

    def __init__(self, schema, validaters=None):
        self.validater = None
        self.fn = None
        self.args = tuple()
        self.default = None
        self.kwargs = {}
        if isinstance(schema, Schema):
            for k in ['validater', 'fn', 'args', 'default', 'kwargs',
                      'type', 'required', 'desc', 'sub']:
                if hasattr(schema, k):
                    setattr(self, k, getattr(schema, k))
        elif isinstance(schema, dict) and 'validater' not in schema:
            self.type = 'map'
            self.required = schema.get('$required', True)
            self.desc = schema.get('$desc', '')
            self.sub = {k: Schema(v, validaters) for k, v in schema.items()
                        if k not in ['$required', '$desc']}
        elif isinstance(schema, list):
            self.type = 'array'
            self.required = False
            self.desc = ''
            assert len(schema) == 1
            self.sub = Schema(schema[0], validaters)
        else:
            if isinstance(schema, dict):
                info = schema.copy()
            else:
                info = parse_snippet(schema)
            self.required = info.pop('required', False)
            self.desc = info.pop('desc', '')
            self.validater = info.pop('validater')
            if validaters is not None and self.validater in validaters:
                self.fn = validaters[self.validater]
            elif self.validater in default_validaters:
                self.fn = default_validaters[self.validater]
            else:
                raise SchemaError('validater not exists: %s' % self.validater)
            self.args = info.pop('args', tuple())
            self.default = info.pop('default', None)
            self.kwargs = info
            self.sub = None
            if self.validater in ['dict', 'list', 'any']:
                self.type = 'any'
            else:
                self.type = 'scalar'
        self.data = self.json()
        self.error = "must be '%s': %s" % (self.validater, self.desc)
        # state machine
        self.obj = None
        self.state = 'scalar'
        self.data_type = self.type if self.type != 'any' else None
        self.key = None
        self.skip_count = 0
        self.inner = None
        self.state_fn = {
            'scalar': self.on_scalar,
            'map': self.on_map,
            'map_key': self.on_map_key,
            'array': self.on_array,
            'inner': self.on_inner,
            'stop': self.on_stop,
            'skip': self.on_skip
        }

    def __getitem__(self, key):
        if self.type == 'map':
            return self.sub[key]
        elif self.type == 'array':
            if key == 0:
                return self.sub
        raise KeyError(key)

    def __eq__(self, other):
        try:
            return (
                self.type == other.type and
                self.required == other.required and
                self.desc == other.desc and
                self.sub == other.sub and
                self.validater == other.validater and
                self.fn == other.fn and
                self.args == other.args and
                self.default == other.default and
                self.kwargs == other.kwargs
            )
        except AttributeError:
            return False

    def json(self):
        if self.type == 'map':
            sche = {k: v.json() for k, v in self.sub.items()}
            if not self.required:
                sche['$required'] = self.required
            if self.desc:
                sche['$desc'] = self.desc
            return sche
        elif self.type == 'array':
            return [self.sub.json()]
        else:
            sche = {
                "validater": "%s%s" % (self.validater, self.args or ''),
            }
            if self.required:
                sche["required"] = True
            if self.desc:
                sche["desc"] = self.desc
            if not is_empty(self.default):
                sche["default"] = self.default
            if self.kwargs:
                sche["kwargs"] = self.kwargs
            return sche

    def __repr__(self):
        return 'Schema(%s)' % json.dumps(self.data, indent=2)

    def validate(self, value):
        """validate scalar value"""
        if is_empty(value):
            if callable(self.default):
                value = self.default()
            else:
                value = self.default
        empty = is_empty(value)
        valid, value = self.fn(value, *self.args, **self.kwargs)
        if empty:
            if self.required:
                return 'required', value
            else:
                return None, value
        elif valid:
            return None, value
        else:
            return self.error, value

    def on_scalar(self, event, value):
        if self.type == 'any':
            if self.validater == 'dict':
                if event == 'start_map':
                    self.data_type = 'map'
                    self.sub = defaultdict(lambda: Schema('any'))
                else:
                    raise Invalid('expect start_map')
            elif self.validater == 'list':
                if event == 'start_array':
                    self.data_type = 'array'
                    self.sub = Schema('any')
                else:
                    raise Invalid('expect start_array')
            else:
                if event == 'start_map':
                    self.data_type = 'map'
                    self.sub = defaultdict(lambda: Schema('any'))
                elif event == 'start_array':
                    self.data_type = 'array'
                    self.sub = Schema('any')
                elif event == 'scalar':
                    self.data_type = 'scalar'
                else:
                    raise Invalid('expect start_map/start_array/scalar')
        else:
            self.data_type = self.type
        if self.data_type == 'map':
            if event == 'start_map':
                self.state = 'map'
                self.obj = {}
            else:
                raise Invalid('expect start_map')
        elif self.data_type == 'array':
            if event == 'start_array':
                self.state = 'array'
                self.obj = []
                self.inner = self.sub
            else:
                raise Invalid('expect start_array')
        else:
            if event == 'scalar':
                self.state = 'stop'
                err, val = self.validate(value)
                self.obj = val
                if err is not None:
                    raise Invalid(err)
            else:
                raise Invalid('expect scalar')

    def on_map(self, event, value):
        if event == 'map_key':
            if value in self.sub:
                self.state = 'map_key'
                self.key = value
                self.inner = self.sub[self.key]
            else:
                self.state = 'skip'
                self.key = None
                self.skip_count = 0
        elif event == 'end_map':
            self.state = 'stop'
            missing = set(self.sub) - set(self.obj)
            for k in missing:
                self.obj[k] = self.sub[k].validate(None)
        else:
            raise Invalid('expect map_key or end_map')

    def on_map_key(self, event, value):
        self.inner.reset()
        state = self.inner.feed(event, value)
        self.obj[self.key] = self.inner.obj
        if state == 'stop':
            self.state = 'map'
        else:
            self.state = 'inner'

    def on_array(self, event, value):
        if event == 'end_array':
            self.state = 'stop'
        else:
            self.inner.reset()
            self.key = '[%d]' % len(self.obj)
            state = self.inner.feed(event, value)
            self.obj.append(self.inner.obj)
            if state == 'stop':
                self.state = 'array'
            else:
                self.state = 'inner'

    def on_inner(self, event, value):
        state = self.inner.feed(event, value)
        if state == 'stop':
            self.state = self.data_type

    def on_stop(self, event, value):
        raise Invalid('stop')

    def on_skip(self, event, value):
        if self.skip_count == 0 and event == 'end_map':
            self.state = 'map'
        else:
            if event == 'start_map' or event == 'start_array':
                self.skip_count += 1
            elif event == 'end_map' or event == 'end_array':
                self.skip_count -= 1
            else:
                pass

    def reset(self):
        """reset the state machine"""
        self.obj = None
        self.state = 'scalar'
        self.data_type = None
        self.key = None
        self.skip_count = 0
        self.inner = None

    def feed(self, event, value):
        """feed (event, value) to build struct data"""
        try:
            self.state_fn[self.state](event, value)
        except Invalid as ex:
            if self.key is not None:
                ex.args += (self.key,)
            raise
        return self.state

    def expect(self):
        """tell which keys current needed"""
        if self.state in ['inner', 'array', 'map_key']:
            return self.inner.expect()
        else:
            if self.type == 'map':
                return self.sub.keys()
            else:
                return None


def parse(schema, validaters=None):
    """parse schema, return Schema object"""
    return Schema(schema, validaters)


def validate(obj, schema, proxy_types=None):
    """
    validate obj by schema, return (error, value)

    Usage::
        sche = parse({"userid": "int&required"})
        err, val = validate({"userid": "abc"})
        key, reason = err[0]  # "userid", "must be int"
        err, val = validate({"userid": "123"})
        # err is None
        print(val)  # {"userid": 123}

    Note the error is a list of tuple(key, reason), in validater<=0.9
    it contains all errors, now it only contains one error.

    :param obj: file-like object(has 'read' attribute) is parsed by ijson,
                dict, list, scalar value, raw object is parsed by Parser
    :param schema: Schema object which could tell which keys it need
    :proxy_types: not used, place here to keep compat with validater<=0.9
    """
    if not hasattr(obj, 'read'):
        p = Parser(schema)
        parser = p.parse_value(obj)
    else:
        parser = basic_parse(obj)
    err = None
    try:
        for event, value in parser:
            if event in ['null', 'boolean', 'number', 'string']:
                event = 'scalar'
            schema.feed(event, value)
            if schema.state == 'stop':
                break
    except Invalid as ex:
        err = [(ex.key, ex.reason)]
    val = schema.obj
    schema.reset()
    return err, val


if __name__ == '__main__':
    sche = {
        "array": 'any',
        "map": {
            "key": "str&required"
        }
    }
    obj = {
        "array": [1, 2],
        "map": {
            "key": "value"
        }
    }
    schema = Schema(sche)
    result = validate(obj, schema)
    print(result)
    result = validate([{}], parse('any'))
    print(result)
