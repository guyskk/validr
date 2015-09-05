# coding:utf-8

import copy
from . import validaters


class SchemaError(Exception):

    """docstring for SchemaError"""


def _build_msg(vali, desc):
    if desc:
        desc = ": " + desc
    else:
        desc = ""
    return u"must be '%s'%s" % (vali, desc)


def _schema_info(obj):
    """
    return (is_schema, is_list, info)
    """
    if isinstance(obj, dict):
        if isinstance(obj.get("validate"), basestring):
            return (True, False, obj)
    elif isinstance(obj, list):
        if len(obj) == 1 and isinstance(obj[0], dict)\
                and isinstance(obj[0].get("validate"), basestring):
            return (True, True, obj[0])
    return (False, False, None)


def _check_keys(obj, schema):
    """check missing keys and common keys
    return (miss, keys)
    """
    keys = []
    miss = []
    assert isinstance(schema, dict)
    assert isinstance(obj, dict)
    for k in schema:
        is_schema, is_list, info = _schema_info(schema[k])
        # -is_schema
        #   -is_list(also means key is required)
        #       -default(1st item when required and list is empty)
        #       -required(means list not empty)
        #       -not required
        #   -not_list
        #       -default(default value when required)
        #       -required (means key is required)
        #       -not required
        # -not_schema(also means key is required)
        if (not is_schema):
            if k in obj:
                keys.append(k)
            else:
                miss.append((k, "required"))
                schema[k] = None
        elif is_list:
            if k in obj:
                keys.append(k)
                # validate list not empty
                if len(obj[k]) == 0 and info.get("required"):
                    default = info.get("default")
                    if default is not None:
                        if callable(default):
                            default = default()
                        obj[k][0] = default
                    else:
                        miss.append((k, "list shouldn't be empty"))
                        schema[k].pop()
            else:
                miss.append((k, "required"))
                schema[k].pop()
        else:  # not_list
            default = info.get("default")
            if callable(default):
                default = default()
            if k in obj:
                keys.append(k)
                if obj[k] is None and default is not None:
                    obj[k] = default
            elif info.get("required"):
                if default is not None:
                    obj[k] = default
                    keys.append(k)
                else:
                    miss.append((k, "required"))
                    schema[k] = None
            else:
                schema[k] = None
    return (miss, keys)


def _get_info(info):
    desc = info.get("desc")
    vali = info.get("validate")
    valier = validaters.get(vali)
    if valier is None:
        raise SchemaError("can't find validater '%s'" % vali)
    return (desc, vali, valier)


def validate(obj, schema):
    """validate obj according to schema
    return:
        tuple(errors,validated_value)
        - errors is a list of tupe(key,err_msg)
        - validated_value is a dict
    schema format:
        {
            "key1":{
                "desc":"desc of the key",
                "required":True,
                "validate":"validater, eg datetime",
                "default":"default_value",
            },
            "key2":{
                "key_nest":{
                    "desc":"desc of the key",
                    "required":True,
                    "validate":"datetime",
                    "default":"default_value",
                },
                ...
            },
            "key_list":[{
                    "desc":"desc of the key",
                    "required":True,
                    "validate":"datetime",
                    "default":"default_value",
                }]
            ...
        }
    - validate is required, desc/required/default is optional
    - nest is supported
    - list contain (only) one sub_schema
    - built-in validater
        name            valid value
        ---------------------------------
        any             anything
        basestring      basestring
        unicode         unicode
        str             str
        list            list
        dict            dict
        bool            bool
        int             int
        long            long
        float           float
        datetime        isoformat datetime.datetime
        objectid        bson.objectid.ObjectId
        re_email        email
        re_ipv4         ipv4
        re_pnone        phone_number
        re_idcard       身份证号
        re_url          url, support urls without 'http://'
        re_name         common_use_name [a-z|A-Z|0-9|_] and 5~16 chars
    """

    # there are 6 structs of Obj and Schame
    # 1. O -> S    treat as {'obj':O} -> {'obj':S}
    # 2. [O, ...] -> [S]
    # 3. {key:O} -> {key:S}
    # 4. {key:[O, ...]} -> {key:[S]}
    # 5. {key:{...}} -> {key:{...}}
    # 6. [{...}] -> [{...}]
    #
    # 1,2 should be treat as special case
    # 3,4 is base struct
    # 5 can be convert to 3,4 by recursion
    # 6 can be convert to 5, and should be treat as special case
    # list can be treat as dict, key is '[index]'

    if schema is None:
        raise SchemaError("schema can't be None")

    # validate 1,2,6 stuct
    errors, validated_value = validate_1_2_6(obj, schema)
    if errors is not None or validated_value is not None:
        return (errors, validated_value)

    errors = []
    # make deepcopy of schema, then update it with valid value.
    validated_value = copy.deepcopy(schema)
    # use stack other than recursion to enhance performance.
    stack = [("", obj, validated_value)]

    # validate 3,4,5
    while stack:
        (k, o, s) = stack.pop()
        if not isinstance(s, dict):
            raise SchemaError("%s not a valid schema" % s)
        if not isinstance(o, dict):
            errors.append((k[:-1], "must be a dict"))
            continue

        # find missing keys and common keys
        miss, keys = _check_keys(o, s)
        # import pdb
        # pdb.set_trace()
        if miss:
            errors.extend([(k + mis, msg) for mis, msg in miss])
            # continue
        for key in keys:
            is_schema, is_list, info = _schema_info(s[key])
            if not is_schema:
                stack.append(("%s%s." % (k, key), o[key], s[key]))
                continue
            desc, vali, valier = _get_info(info)
            if is_list:
                if not isinstance(o[key], list):
                    errors.append(k + key, "not a list")
                    continue
                s[key].pop()
                for i, v in enumerate(o[key]):
                    new_key = "%s%s.[%d]" % (k, key, i)
                    ok, value = valier(v)
                    if not ok:
                        errors.append((new_key, _build_msg(vali, desc)))
                        s[key].append(None)
                    else:
                        # replace schema with valid value
                        s[key].append(value)
            else:
                new_key = "%s%s" % (k, key)
                ok, value = valier(o[key])
                if not ok:
                    errors.append((new_key, _build_msg(vali, desc)))
                    s[key] = None
                else:
                    # replace schema with valid value
                    s[key] = value

    return (errors, validated_value)


def validate_1_2_6(obj, schema):
    errors = []
    # make deepcopy of schema, then update it with valid value.
    validated_value = copy.deepcopy(schema)
    is_schema, is_list, info = _schema_info(validated_value)
    # import pdb
    # pdb.set_trace()
    # 1,2
    if is_schema:
        desc, vali, valier = _get_info(info)
        # 2
        if is_list:
            if not isinstance(obj, list):
                errors.append(("obj", "not a list"))
            else:
                validated_value.pop()
                for i, v in enumerate(obj):
                    new_key = "[%d]" % i
                    ok, value = valier(v)
                    if not ok:
                        errors.append((new_key, _build_msg(vali, desc)))
                        validated_value.append(None)
                    else:
                        # replace schema with valid value
                        validated_value.append(value)
        # 1
        else:
            ok, value = valier(obj)
            if not ok:
                errors.append(("obj", _build_msg(vali, desc)))
                validated_value = None
            else:
                # replace schema with valid value
                validated_value = value

        return (errors, validated_value)
    # 6
    elif isinstance(validated_value, list):
        if not isinstance(obj, list):
            errors.append(('obj', "not a list"))
        else:
            s = validated_value.pop()
            for i, v in enumerate(obj):
                errs, val = validate(v, s)
                errors.extend([("[%d].%s" % (i, k), msg)for k, msg in errs])
                validated_value.append(val)
        return (errors, validated_value)
    else:
        return (None, None)
