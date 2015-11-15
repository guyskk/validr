# coding:utf-8

from __future__ import unicode_literals
from __future__ import absolute_import
import six
from validater import validaters
from validater import ProxyDict

class SchemaError(Exception):

    """SchemaError indicate schema invalid"""


def _build_msg(vali, desc):
    if desc:
        desc = ": " + desc
    else:
        desc = ""
    return "must be '%s'%s" % (vali, desc)


def is_schema(obj):
    if isinstance(obj, dict):
        vali = obj.get("validate")
        if isinstance(vali, six.string_types) or six.callable(vali):
            return True
    return False


def schema_info(obj):
    """schema_info"""
    assert is_schema(obj)
    required = bool(obj.get("required"))
    desc = obj.get("desc")
    vali = obj.get("validate")
    desc = _build_msg(vali, desc)
    has_default = "default" in obj
    default = obj.get("default")
    if six.callable(default):
        default = default()
    if six.callable(vali):
        valier = vali
    else:
        valier = validaters.get(vali)
    if valier is None:
        raise SchemaError("can't find validater '%s'" % vali)
    return (desc, required, has_default, default, vali, valier)


def _set_value(value, val, key):
    if isinstance(value, list):
        # keep list order
        value.insert(0, val)
    else:
        value[key] = val


def validate(obj, schema, proxy_types=None):
    """validate

    :param obj: the object to be validate
    :param schema: dict_like schema
    :param proxy_types: list of types which should be wraped in ProxyDict

    Demand::

        1. No modify of obj and schema
        2. No deepcopy of obj and schema
           because not every object can be deepcopyed
        3. Can validate all structs below

    There are 7 structs of Obj and Schame::

        1. O -> S
        2. [O, ...] -> [S]
        3. [{...}] -> [{...}]
        4. {key:O} -> {key:S}
        5. {key:[O, ...]} -> {key:[S]}
        6. {key:[{...}]} -> {key:[{...}]}
        7. {key:{...}} -> {key:{...}}
    """
    if proxy_types is None:
        proxy_types = []
    # The 7 structs of Obj and Schame actually is 3 structs
    #
    # 1. O -> S
    # 2. [{...}] -> [{...}]
    # 3. {key:{...}} -> {key:{...}}
    #
    # 2,3 can converted to 1 finally
    #
    # In order to unify operation,
    # I convert all structs to {"obj":{...}},
    # Then build validated_value
    if schema is None:
        raise SchemaError("schema can't be None")
    obj = {"obj": obj}
    schema = {"obj": schema}
    validated_value = {"obj": None}
    errors = []
    # Init state
    # (obj, schema, value, key, fullkey)
    # key: used in set_value
    # fullkey: used in errors
    stack = [(obj["obj"], schema["obj"], validated_value, "obj", "obj")]
    while stack:
        (obj, schema, value, key, fullkey) = stack.pop()
        if isinstance(schema, list):
            if len(schema) != 1:
                raise SchemaError("invalid list schema '%s'" % schema)
            if not isinstance(obj, list):
                errors.append((fullkey[4:], "must be list"))
            else:
                new_value = []
                _set_value(value, new_value, key)
                # add list item to stack
                for k, v in enumerate(obj):
                    full_k = "%s.[%d]" % (fullkey, k)
                    stack.append((v, schema[0], new_value, k, full_k))
        elif isinstance(schema, dict):
            if not is_schema(schema):
                new_value = {}
                # must aways do _set_value
                _set_value(value, new_value, key)
                if not isinstance(obj, dict):
                    if not isinstance(obj, tuple(proxy_types)):
                        errors.append((fullkey[4:], "must be dict"))
                        continue
                    else:
                        # wrap obj in ProxyDict
                        obj = ProxyDict(obj, proxy_types)
                # add dict item to stack
                for k in schema:
                    full_k = "%s.%s" % (fullkey, k)
                    stack.append((obj.get(k), schema[k], new_value, k, full_k))
            else:
                (desc, required, has_default, default, vali, valier) = schema_info(schema)
                # work with default and required
                # treat "" as NULL, this is more practical
                # and most framworks behave this way.

                # obj may can't be decode to unicode,
                # so use b"" to avoid UnicodeWarning:
                # Unicode equal comparison failed to convert both arguments to
                # Unicode - interpreting them as being unequal
                if obj is None or obj == b"" and has_default:
                    obj = default
                # validate obj
                # also call valier to set NULL value if obj is None or empty
                ok, val = valier(obj)
                _set_value(value, val, key)
                if obj is None or obj == b"":
                    if required:
                        errors.append((fullkey[4:], "required"))
                else:
                    if not ok:
                        errors.append((fullkey[4:], desc))

    return errors, validated_value["obj"]


def parse_schema(info):
    """convert tuple_like schema to dict_like schema

    tuple_like schema can has 1~3 items: ``(validate&required, default, desc)``
    validate_required is needed, default and desc is opinion.
    validate_required is a string like ``"+int&required"``, the ``&required`` is opinion.

    For example::

        "+int&required", 1, "the page number"

    will be converted to::

        {
            "default": 1,
            "validate": "+int",
            "required": True,
            "desc": "the page number"
        }

    And::

        "+int", 1

    will be converted to::

        {
            "default": 1,
            "validate": "+int",
            "required": False
        }

    And::

        "+int", None, "the page number"

    will be converted to::

        {
            "validate": "+int",
            "required": False,
            "desc": "the page number"
        }

    And if the tuple_like schema is string::

        "+int&required"

    will be converted to::

        {
            "validate": "+int",
            "required": True
        }

    :param info: tuple_like schema
    """
    if isinstance(info, six.string_types):
        info = (info, None, None)
    else:
        info = info + (None,) * (3 - len(info))
    validate_required, default, desc = info
    validate_required = validate_required.split("&")
    validate = validate_required[0]
    if len(validate_required) == 2:
        if validate_required[1] != "required":
            raise SchemaError("invalid schema syntax: %s" % validate_required[1])
        required = True
    else:
        required = False
    schema = {
        "validate": validate,
        "required": required,
    }
    if default is not None:
        schema["default"] = default
    if desc is not None:
        schema["desc"] = desc
    return schema


def combine_schema(scope, *args):
    """combine tuple_like validate schema from scope

    :param scope: a dict, such as Class.__dict__
    :param args: variable names or dicts
    """
    node = {}
    for x in args:
        # deal with x like: [[["name"]]]
        list_deep = 0
        while(isinstance(x, list)):
            if len(x) != 1:
                raise SchemaError("invalid schema: list's length must be 1")
            x = x[0]
            list_deep += 1
        info = scope[x]

        # support with_name tuple schema
        if isinstance(info, tuple) and len(info) >= 2 and\
                (six.callable(info[1]) or isinstance(info[1], tuple)):
            if len(info) != 2:
                raise SchemaError("tuple_like with_name schema'length must be 2")
            x, info = info

        if six.callable(info):
            info = info(scope)
        elif isinstance(info, dict):
            info = info
        else:
            info = parse_schema(info)

        # wrap info with []
        if list_deep > 0:
            if len(args) != 1:
                raise SchemaError("can't combine list and others")
            while list_deep > 0:
                info = [info]
                list_deep -= 1
            return info
        node[x] = info
    return node


def schema(*args):
    """combine validate schema, return a function for doing combine later

    Run the code below and you will understand it::

        from validater import schema
        import json

        leaf1 = "+int&required", 1, "leaf1 desc"
        leaf2 = "unicode&required"
        leaf3 = "unicode", None, "article table of content"

        branch1 = schema("leaf1", "leaf2")
        branch2 = schema("branch1", "leaf3")

        flower = schema(["branch1"])
        tree = schema(["branch2"])

        forest1 = schema(["tree"])
        forest2 = schema([["branch2"]])
        park = schema("tree", "flower")

        scope = locals()

        def pp(obj):
            print json.dumps(obj, ensure_ascii=False, indent=4)

        pp(branch1(scope))
        pp(branch2(scope))

        pp(flower(scope))
        pp(tree(scope))

        pp(forest1(scope))
        pp(forest2(scope))
        pp(park(scope))
    """
    def lazy_combine(scope):
        return combine_schema(scope, *args)
    return lazy_combine
