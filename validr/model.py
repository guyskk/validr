"""
Model

model class is a convenient way to use schema, it's inspired by data class but
works differently, it's much simpler and easy to use.

define a base model:

    @modelclass
    class Model:
        # define common fields and methods here
        # __init__, __repr__ and __eq__ will auto created if not exists

or

    @modelclass(compiler=xxx)
    class Model:
        pass

define models:

    class User:
        id = T.int
        age = T.int.default(18)
        name = T.str

schema slice:

    Lite = User['id', 'name']

use the model:

    user = User(id=1, name='test')
    # convert model to dict
    asdict(user)
    # get fields
    fields(user)  # or fields(User)
    # get the schema
    T(user)  # or T(User)
"""
from terminaltables import AsciiTable

from .schema import Compiler, T, Schema
from ._exception import Invalid, mark_key


def modelclass(cls=None, *, compiler=None):
    if cls is not None:
        return _create_model_class(cls, compiler=compiler)

    def decorator(cls):
        return _create_model_class(cls, compiler=compiler)

    return decorator


def _extract_schemas(namespace):
    schemas = {}
    for k, v in namespace.items():
        if hasattr(v, '__schema__'):
            v = v.__schema__
        if isinstance(v, Schema):
            schemas[k] = v
    return schemas


def _create_model_class(model_cls, compiler=None):

    compiler = compiler or Compiler()

    class Field:
        def __init__(self, name, schema):
            self.name = name
            self.schema = schema
            self.on_change = schema.on_change_callback
            with mark_key(self.name):
                self.validate = compiler.compile(schema)

        def __repr__(self):
            return f'Field(name={self.name!r}, schema={self.schema!r})'

        def __get__(self, obj, obj_type):
            if obj is None:
                return self
            return obj.__dict__.get(self.name, None)

        def __set__(self, obj, value):
            with mark_key(self.name):
                value = self.validate(value)
            if self.on_change is None:
                obj.__dict__[self.name] = value
            else:
                origin = obj.__dict__.get(self.name, None)
                if value != origin:
                    self.on_change(obj, value)
                obj.__dict__[self.name] = value

    # common fields
    for name, schema in _extract_schemas(vars(model_cls)).items():
        setattr(model_cls, name, Field(name, schema))

    class ModelMeta(type):
        def __new__(cls, cls_name, bases, namespace):
            for name, schema in _extract_schemas(namespace).items():
                namespace[name] = Field(name, schema)
            return super().__new__(cls, cls_name, bases, namespace)

        def __init__(cls, *args, **kwargs):
            super().__init__(*args, **kwargs)
            schemas = {}
            for base in reversed(cls.__mro__):
                for k, v in base.__dict__.items():
                    if isinstance(v, Field):
                        schemas[k] = v.schema
            cls.__schema__ = T.dict(schemas).__schema__
            cls.__fields__ = frozenset(schemas)

        def __repr__(cls):
            # use __schema__ can keep fields order
            fields = ', '.join(cls.__schema__.items)
            return f'{cls.__name__}<{fields}>'

        def __getitem__(self, keys):
            if not isinstance(keys, (list, tuple)):
                keys = (keys,)
            s = self.__schema__
            schema = Schema(validator=s.validator, params=s.params.copy())
            schema.items = {}
            items = s.items or {}
            for k in keys:
                if k not in items:
                    raise ValueError(f'key {k!r} is not exists')
                schema.items[k] = items[k]
            return T(schema)

    class Model(model_cls, metaclass=ModelMeta):

        if '__init__' not in model_cls.__dict__:
            def __init__(self, *obj, **params):
                errors = []
                if obj:
                    if len(obj) > 1:
                        msg = (f'__init__() takes 2 positional arguments '
                               f'but {len(obj) + 1} were given')
                        raise TypeError(msg)
                    obj = obj[0]
                    for k in self.__fields__ - set(params):
                        try:
                            setattr(self, k, getattr(obj, k, None))
                        except Invalid as ex:
                            errors.append((ex.position, ex.message))
                else:
                    for k in self.__fields__ - set(params):
                        try:
                            setattr(self, k, None)
                        except Invalid as ex:
                            errors.append((ex.position, ex.message))
                for k in self.__fields__ & set(params):
                    try:
                        setattr(self, k, params[k])
                    except Invalid as ex:
                        errors.append((ex.position, ex.message))
                for k in set(params) - self.__fields__:
                    errors.append((k, 'undesired key'))
                if errors:
                    table = [('Key', 'Error')] + errors
                    raise Invalid('\n' + AsciiTable(table).table)

        if '__repr__' not in model_cls.__dict__:
            def __repr__(self):
                params = []
                # use __schema__ can keep fields order
                for k in self.__schema__.items:
                    v = getattr(self, k)
                    params.append(f'{k}={v!r}')
                params = ', '.join(params)
                return f'{type(self).__name__}({params})'

        if '__eq__' not in model_cls.__dict__:
            def __eq__(self, other):
                fields = getattr(other, '__fields__')
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


def fields(m):
    return m.__fields__


def asdict(m, *, keys=None):
    return m.__asdict__(keys=keys)
