"""
Model class is a convenient way to use schema, it's inspired by data class but
works differently.
"""
from .schema import Compiler, T, Schema
from .exception import Invalid, ModelInvalid, mark_key
from .validator import is_dict, get_dict_value, get_object_value


class ImmutableInstanceError(AttributeError):
    """Raised when an attempt is modify a immutable class"""


def modelclass(cls=None, *, compiler=None, immutable=False):
    if cls is not None:
        return _create_model_class(cls, compiler, immutable)

    def decorator(cls):
        return _create_model_class(cls, compiler, immutable)

    return decorator


def _create_model_class(model_cls, compiler, immutable):

    compiler = compiler or Compiler()

    def _extract_schemas(cls):
        schemas = {}
        for k, v in vars(cls).items():
            if k == "__schema__":
                continue
            if hasattr(v, "__schema__"):
                v = v.__schema__
            if isinstance(v, Schema):
                schemas[k] = v
        return schemas

    def _extract_post_init(cls):
        f = vars(cls).get("__post_init__", None)
        if f is None or not callable(f):
            return None
        return f

    class Field:
        def __init__(self, name, schema):
            self.name = name
            self.__schema__ = schema
            with mark_key(self.name):
                self.validate = compiler.compile(schema)

        def __repr__(self):
            return "Field(name={!r}, schema={!r})".format(self.name, self.__schema__)

        def __get__(self, obj, obj_type):
            if obj is None:
                return self
            return obj.__dict__.get(self.name, None)

        def __set__(self, obj, value):
            with mark_key(self.name):
                value = self.validate(value)
            obj.__dict__[self.name] = value

    class ModelMeta(type):
        def __init__(cls, *args, **kwargs):
            super().__init__(*args, **kwargs)
            schemas = {}
            post_inits = []
            for cls_or_base in reversed(cls.__mro__):
                post_init = _extract_post_init(cls_or_base)
                if post_init is not None:
                    post_inits.append(post_init)
                for name, schema in _extract_schemas(cls_or_base).items():
                    schemas[name] = schema
            for name, schema in schemas.items():
                setattr(cls, name, Field(name, schema))
            cls.__post_inits = post_inits
            cls.__schema__ = T.dict(schemas).__schema__
            cls.__fields__ = frozenset(schemas)

        def post_init(cls, instance):
            for post_init in cls.__post_inits:
                post_init(instance)

        def __repr__(cls):
            # use __schema__ can keep fields order in python>=3.6
            fields = ", ".join(cls.__schema__.items)
            return "{}<{}>".format(cls.__name__, fields)

        def __getitem__(self, keys):
            s = self.__schema__
            items = s.items or {}
            if not isinstance(keys, (list, tuple, set, frozenset)):
                if keys not in items:
                    raise KeyError("key {!r} is not exists".format(keys))
                return items[keys]
            schema = Schema(validator=s.validator, params=s.params.copy())
            schema.items = {}
            for k in keys:
                if k not in items:
                    raise KeyError("key {!r} is not exists".format(k))
                schema.items[k] = items[k]
            return T(schema)

    class Model(model_cls, metaclass=ModelMeta):

        if "__init__" not in model_cls.__dict__:

            def __init__(self, *obj, **params):
                self.__dict__["__immutable__"] = False
                params_set = set(params)
                errors = []
                if obj:
                    if len(obj) > 1:
                        msg = (
                            "__init__() takes 2 positional arguments "
                            "but {} were given".format(len(obj) + 1)
                        )
                        raise TypeError(msg)
                    obj = obj[0]
                    if is_dict(obj):
                        getter = get_dict_value
                    else:
                        getter = get_object_value
                    for k in self.__fields__ - params_set:
                        try:
                            setattr(self, k, getter(obj, k))
                        except Invalid as ex:
                            errors.append(ex)
                else:
                    for k in self.__fields__ - params_set:
                        try:
                            setattr(self, k, None)
                        except Invalid as ex:
                            errors.append(ex)
                for k in self.__fields__ & params_set:
                    try:
                        setattr(self, k, params[k])
                    except Invalid as ex:
                        errors.append(ex)
                for k in params_set - self.__fields__:
                    errors.append(Invalid("undesired key").mark_key(k))
                if errors:
                    raise ModelInvalid(errors)
                type(self).post_init(self)
                self.__dict__["__immutable__"] = immutable

        else:

            def __init__(self, *args, **kwargs):
                self.__dict__["__immutable__"] = False
                super().__init__(*args, **kwargs)
                type(self).post_init(self)
                self.__dict__["__immutable__"] = immutable

        if immutable:

            def __setattr__(self, name, value):
                if self.__immutable__:
                    msg = "{} object is immutable!".format(model_cls.__name__)
                    raise ImmutableInstanceError(msg)
                return object.__setattr__(self, name, value)

            def __delattr__(self, name):
                if self.__immutable__:
                    msg = "{} object is immutable!".format(model_cls.__name__)
                    raise ImmutableInstanceError(msg)
                return object.__delattr__(self, name)

        if "__repr__" not in model_cls.__dict__:

            def __repr__(self):
                params = []
                # use __schema__ can keep fields order
                for k in self.__schema__.items:
                    v = getattr(self, k)
                    params.append("{}={!r}".format(k, v))
                params = ", ".join(params)
                return "{}({})".format(type(self).__name__, params)

        if "__eq__" not in model_cls.__dict__:

            def __eq__(self, other):
                fields = getattr(other, "__fields__")
                if not fields:
                    return False
                if self.__fields__ != fields:
                    return False
                for k in self.__fields__:
                    if getattr(self, k, None) != getattr(other, k, None):
                        return False
                return True

        def __asdict__(self, *, keys=None):
            if not keys:
                keys = self.__fields__
            else:
                keys = set(keys) & self.__fields__
            return {k: getattr(self, k) for k in keys}

    Model.__module__ = model_cls.__module__
    Model.__name__ = model_cls.__name__
    Model.__qualname__ = model_cls.__qualname__
    Model.__doc__ = model_cls.__doc__

    return Model


def fields(m) -> set:
    """Get fields of model or dict schema"""
    if hasattr(m, '__fields__'):  # modelclass
        return m.__fields__
    if hasattr(m, '__schema__'):
        schema = m.__schema__     # T.dict({...})
    else:
        schema = m                # Schema
    if isinstance(schema, Schema):
        if schema.validator == 'dict':
            if schema.items:
                return set(schema.items.keys())
            else:
                return set()
    raise TypeError("can not find fields of {!r}".format(m))


def asdict(m, *, keys=None) -> dict:
    """Convert model instance to dict"""
    return m.__asdict__(keys=keys)
