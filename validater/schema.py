#!/usr/bin/env python
# coding: utf-8
from __future__ import unicode_literals, absolute_import, print_function
import six
import re
from validater import default_validaters, ProxyDict
pattern_schema = re.compile(r"^([^ \f\n\r\t\v()&]+)(\(.*\))?(&.*)?$")


class SchemaError(ValueError):

    """SchemaError indicate schema invalid"""


class Schema(object):
    """Schema

    :param data: a dict contains schema infomations

    .. code::

        {
            "validater": "int",
            "args": (0, 100),
            "required": True,
            "default": 10,
            ...
        }

    :param validaters: a dict contains all validaters
    """

    def __init__(self, data, validaters=None):
        if validaters is None:
            validaters = default_validaters
        self.data = data
        self.validaters = validaters
        if 'validater' not in self.data or not self.data['validater']:
            raise SchemaError('validater is missing: %s' % data)
        if self.data['validater'] not in self.validaters:
            raise SchemaError(
                'validater not exists: %s' % self.data['validater'])
        self.validater = self.validaters[self.data['validater']]
        self.required = self.data.get('required', False)
        self.default = self.data.get('default', None)
        self.args = self.data.get('args', tuple())
        self.kwargs = {k: v for k, v in self.data.items()
                       if k not in ['validater', 'args', 'required', 'default', 'desc']}
        if 'desc' in self.data:
            desc = ": " + self.data['desc']
        else:
            desc = ""
        name = self.data['validater']
        if self.args:
            name += str(self.args)
        self.error = "must be '%s'%s" % (name, desc)

    def _is_empty(self, obj):
        return obj is None or obj == str("") or obj == b""

    def validate(self, obj):
        """validate obj

        :return: (error,value)
        """
        if self._is_empty(obj) and not self._is_empty(self.default):
            if six.callable(self.default):
                obj = self.default()
            else:
                obj = self.default
        # empty value is not always None, depends on validater
        ok, val = self.validater(obj, *self.args, **self.kwargs)
        if ok:
            return None, val
        else:
            if self._is_empty(obj):
                if self.required:
                    return "required", val
                else:
                    # val is empty value
                    return None, val
            else:
                return self.error, val

    def __eq__(self, other):
        return self.data == other.data

    def __ne__(self, other):
        return self.data != other.data

    def __repr__(self):
        return "<Schema %s>" % repr(self.data)


def _transform_dict(data, should_call_fn, fn):
    """modify some value of a dict

    :param should_call_fn: func(v): return bool
    :param fn: func(v): return new value which will replace v
    """
    stack = [data]
    while stack:
        data = stack.pop()
        for k, v in data.items():
            if should_call_fn(v):
                data[k] = fn(v)
            else:
                stack.append(v)


def parse(schema, validaters=None):
    """parse schema, the origin schema will be modified

    usage::

        username = "email&required"
        password = "password&required"
        email = "email&required", "your email address"
        date_modify = "datetime('iso')&required"
        token = "unicode&required"
        remember_me = "bool&default=False"
        message = "unicode"
        schema_inputs = {
            'username': username,
            'password': password,
            'email': [email],
            'remember_me': remember_me,
            'message': [message],
            'inner': {
                'username': username
            }
        }
        schema_inputs = parse(schema_inputs)

        # to avoid modify the origin schema
        import copy
        schema_parsed = parse(copy.deepcopy(schema_inputs))

    :param schema: schema snippet or dict/list contains schema snippets
    :param validaters: a dict contains all validaters
    :return: a dict which endpoint is Schema object

    algorithm::

        if (schema is not dict) or (schema is dict and has 'validater' key):
            # should call fn
            if schema is dict:
                # has 'validater' key
                make a Schema object
            elif schema is list:
                parse list[0] recursivity
            else:
                # schema_snippet: tuple(string, desc) or string
                parse_snippet and make a Schema object
        else:
            # shouldn't call fn
            parse schema's items by using stack
    """
    if validaters is None:
        validaters = default_validaters

    def should_call_fn(v):
        return (not isinstance(v, dict)) or 'validater' in v

    def fn(v):
        if isinstance(v, dict):
            return Schema(v, validaters)
        elif isinstance(v, list):
            return [parse(v[0])]
        elif isinstance(v, Schema):
            # schema snippet may be parsed more than once,
            # and it will be replace by Schema object at the first time
            # eg:
            # snippet = {"name": "str"}
            # schema = {
            #     "user1": snippet,
            #     "user2": snippet,
            # }
            return v
        else:
            return Schema(parse_snippet(v), validaters)

    if should_call_fn(schema):
        return fn(schema)
    _transform_dict(schema, should_call_fn, fn)
    return schema


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

    if args:
        try:
            args = eval(args)
        except Exception as e:
            raise SchemaError(
                'invalid args: %s, %s\n%s' % (schema, args, repr(e)))
        if not isinstance(args, tuple):
            args = (args,)
    else:
        args = tuple()

    result = {'validater': validater, 'args': args}
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


def _validate_fn(obj, schema, proxy_types=None):
    """handle list and Schema object schema"""
    errors = []
    if isinstance(schema, list):
        result = []
        if not isinstance(obj, list):
            errors.append(('', 'must be list'))
        else:
            for i, x in enumerate(obj):
                err, val = validate(x, schema[0], proxy_types)
                err = [('%s[%s]' % (fullkey, i), msg) for fullkey, msg in err]
                errors.extend(err)
                result.append(val)
    else:
        # schema is Schema object
        err, val = schema.validate(obj)
        result = val
        if err:
            errors.append(('', err))
    return errors, result


def validate(obj, schema, proxy_types=None):
    """validate dict/list/object by schema

    :param obj: obj need to validate
    :param schema: a schema which endpoint is Schema object
    :param proxy_types: a list of types which need to wrap by ProxyDict

    algorithm::

        fn():
            if schema is list:
                call validate for each items
            else:
                # schema is Schema object
                call schema.validate

        validate():
            if schema is not dict:
                call fn then return
            while stack:
                pop stack
                # schema is dict
                wrap obj[k] in ProxyDict if possiable
                check obj is dict
                for k,v in schema:
                    if v is not dict:
                        call fn then merge errors and result
                    else:
                        push stack # obj[k] may not dict
    """
    if proxy_types is None:
        proxy_types = []
    if not isinstance(schema, dict):
        return _validate_fn(obj, schema, proxy_types)
    result = {}
    errors = []
    stack = [(obj, schema, result, "")]
    while stack:
        (obj, schema, value, fullkey) = stack.pop()
        if not isinstance(obj, dict):
            if isinstance(obj, tuple(proxy_types)):
                obj = ProxyDict(obj, proxy_types)
            else:
                errors.append((fullkey, 'must be dict'))
                continue
        for k, v in schema.items():
            full_k = "%s.%s" % (fullkey, k)
            obj_item = obj.get(k)
            if not isinstance(v, dict):
                err, val = _validate_fn(obj_item, v, proxy_types)
                err = [(full_k + key, msg) for key, msg in err]
                errors.extend(err)
                value[k] = val
            else:
                value[k] = {}
                stack.append((obj_item, v, value[k], full_k))
    # trim the first '.'
    errors = [(key[1:], msg) for key, msg in errors]
    return errors, result


if __name__ == '__main__':
    from pprint import pprint as print
    data = {
        "key1": "value1",
        "key2": {
            "key21": "value21"
        }
    }
    should_call_fn = lambda x: not isinstance(x, dict)
    _transform_dict(data, should_call_fn, fn=lambda x: x.upper())
    print(data)
    print('-' * 60)

    print(parse_snippet(("int(0,100)&required&default=10")))
    print(parse_snippet(("int(0,100)&required&default=10", 'desc')))
    print('-' * 60)

    userid = "int&required", "用户账号"
    schema = {
        'userid': userid,
        'userid_list': [userid],
        'inner': {'userid': userid},
        'inner_list': [{'userid': userid}]
    }

    sche = parse(schema)
    print(sche)
    print('-' * 60)

    obj = {
        'userid': '123',
        'userid_list': ['123', '456'],
        'inner': {'userid': '123'},
        'inner_list': [{'userid': '123'}]
    }
    err, val = validate(obj, sche)

    print(dict(err))
    print(val)
    print("-" * 60)

    import cProfile
    cProfile.run("""for i in range(100000):
                        validate(obj, sche)""")
