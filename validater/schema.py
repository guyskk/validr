import json
import re
import itertools
from numbers import Number
from ijson.backends.python import basic_parse
from validater import ProxyDict, default_validaters

pattern_schema = re.compile(r"^([^ \f\n\r\t\v()&]+)(\(.*\))?(&.*)?$")


class SchemaError(ValueError):
    pass


class ValidateError(ValueError):

    def __init__(self, *args):
        super().__init__(*args)
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


def parse_value(obj, proxy_types=None):
    if proxy_types is None:
        proxy_types = []
    if obj is None:
        yield ('null', None)
    elif obj is True:
        yield ('boolean', True)
    elif obj is False:
        yield ('boolean', False)
    elif isinstance(obj, list):
        for event in parse_array(obj, proxy_types=proxy_types):
            yield event
    elif isinstance(obj, dict):
        for event in parse_object(obj, proxy_types=proxy_types):
            yield event
    elif isinstance(obj, str):
        yield ('string', obj)
    elif isinstance(obj, Number):
        yield ('number', obj)
    else:
        if proxy_types and isinstance(obj, tuple(proxy_types)):
            obj = ProxyDict(obj, types=proxy_types)
            for event in parse_object(obj, proxy_types=proxy_types):
                yield event
        else:
            yield ('scalar', obj)


def parse_array(obj, proxy_types=None):
    yield ('start_array', None)
    for x in obj:
        for event in parse_value(x, proxy_types=proxy_types):
            yield event
    yield ('end_array', None)


def parse_object(obj, proxy_types=None):
    yield ('start_map', None)
    for k, v in obj.items():
        yield ('map_key', k)
        for event in parse_value(v, proxy_types=proxy_types):
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
    return s is None or s == ''


class Schema:

    def __init__(self, schema, validaters=None):
        # self.sub -> Schema/{key:Schema}
        self.validater_name = None
        self.validater = None
        self.args = tuple()
        self.default = None
        self.kwargs = {}
        if isinstance(schema, dict) and 'validater' not in schema:
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
            self.type = 'scalar'
            self.sub = None
            if isinstance(schema, dict):
                info = schema.copy()
            else:
                info = parse_snippet(schema)
            self.required = info.pop('required', False)
            self.desc = info.pop('desc', '')
            self.validater_name = info.pop('validater')
            if validaters is not None and self.validater_name in validaters:
                self.validater = validaters[self.validater_name]
            elif self.validater_name in default_validaters:
                self.validater = default_validaters[self.validater_name]
            else:
                raise SchemaError('validater not exists: %s' %
                                  self.validater_name)
            self.args = info.pop('args', tuple())
            self.default = info.pop('default', None)
            self.kwargs = info
        self.data = self.json()
        self.error = "must be '%s'%s" % (self.validater_name, self.desc)

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
                self.validater_name == other.validater_name and
                self.validater == other.validater and
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
                "validater": "%s%s" % (self.validater_name, self.args or ''),
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
        return json.dumps(self.json(), indent=2)

    def expect(self, event, exp):
        if event != exp:
            raise ValidateError("expect '%s', but get '%s'" % (exp, event))

    def expect_scalar(self, event):
        exp = ['null', 'boolean', 'number', 'string', 'scalar']
        if event not in exp:
            raise ValidateError("expect %s, but get '%s'" % (exp, event))

    def skip_map_key(self, parser):
        map_count = 0
        while True:
            event, value = next(parser)
            if map_count == 0:
                if event == 'end_map' or event == 'map_key':
                    parser = itertools.chain([(event, value)], parser)
                    break
                else:
                    raise ValidateError('invalid event: %s' % event)
            else:
                if event == 'start_map':
                    map_count += 1
                elif event == 'end_map':
                    map_count -= 1
        return parser

    def validate(self, parser):
        if parser is None:
            if self.type == 'map':
                if self.required:
                    raise ValidateError('required')
                else:
                    return None
            elif self.type == 'array':
                raise ValidateError('required')
            else:
                if not is_empty(self.default):
                    return self.default
                elif self.required:
                    raise ValidateError('required')
                else:
                    return None
        event, value = next(parser)
        obj = None
        key = None
        try:
            if self.type == 'map':
                self.expect(event, 'start_map')
                obj = {}
                while True:
                    event, value = next(parser)
                    if event == 'end_map':
                        missing = set(self.sub) - set(obj)
                        err = None
                        for k in missing:
                            key = k
                            try:
                                obj[k] = self.sub[k].validate(None)
                            except ValidateError as ex:
                                obj[k] = ex.value
                                err = ex
                        if err is not None:
                            raise err
                        break
                    self.expect(event, 'map_key')
                    if value in self.sub:
                        key = value
                        try:
                            obj[value] = self.sub[value].validate(parser)
                        except ValidateError as ex:
                            obj[value] = ex.value
                            raise
                    else:
                        self.skip_map_key(parser)
            elif self.type == 'array':
                self.expect(event, 'start_array')
                obj = []
                while True:
                    event, value = next(parser)
                    if event == 'end_array':
                        break
                    parser = itertools.chain([(event, value)], parser)
                    key = '[%d]' % len(obj)
                    obj.append(self.sub.validate(parser))
            else:
                self.expect_scalar(event)
                if is_empty(value):
                    if callable(self.default):
                        value = self.default()
                    else:
                        value = self.default
                empty = is_empty(value)
                valid, value = self.validater(value, *self.args, **self.kwargs)
                obj = value
                if empty:
                    if self.required:
                        raise ValidateError('required')
                    else:
                        return value
                elif valid:
                    return value
                else:
                    raise ValidateError(self.error)
            return obj
        except ValidateError as ex:
            ex.value = obj
            if key is not None:
                ex.args += (key,)
            raise


def parse(schema, validaters=None):
    if isinstance(schema, Schema):
        return schema
    return Schema(schema, validaters)


def validate(obj, schema, proxy_types=None):
    if not hasattr(obj, 'read'):
        parser = parse_value(obj, proxy_types)
    else:
        parser = basic_parse(obj)
    try:
        val = schema.validate(parser)
        return None, val
    except ValidateError as ex:
        err = [(ex.key, ex.reason)]
        return err, ex.value


if __name__ == '__main__':
    sche = {
        "array": ["int&required"],
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
    schema = parse(sche)
    result = validate(obj, schema)
    print(result)
