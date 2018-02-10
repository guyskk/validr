from .schema import Compiler, T, Schema
from ._exception import Invalid, mark_key


def modelclass(cls=None, *, compiler=None):
    """
    @modelclass
    @modelclass(compiler=xxx)
    class Model:
        pass
    """
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
            with mark_key(self.name):
                self.validate = compiler.compile(schema)

        def __repr__(self):
            return f'Field(name={self.name}, schema={self.schema!r})'

        def __get__(self, obj, obj_type):
            if obj is None:
                return self
            return obj.__dict__.get(self.name, None)

        def __set__(self, obj, value):
            with mark_key(self.name):
                value = self.validate(value)
            obj.__dict__[self.name] = value

    class ModelMeta(type):
        def __new__(cls, cls_name, bases, namespace):
            for name, schema in _extract_schemas(namespace).items():
                namespace[name] = Field(name, schema)
            return super().__new__(cls, cls_name, bases, namespace)

        def __init__(cls, *args, **kwargs):
            super().__init__(*args, **kwargs)
            fields = {}
            for base in reversed(cls.__mro__):
                for k, v in vars(base).items():
                    if isinstance(v, Field):
                        fields[k] = v.validate
            cls.__schema__ = T.dict(fields)
            cls.__fields__ = frozenset(fields)

        def __repr__(cls):
            return f'{cls.__name__}<{cls.__schema__!r}>'

    class Model(model_cls, metaclass=ModelMeta):
        def __init__(self, **params):
            for k in self.__fields__:
                setattr(self, k, params.pop(k, None))
            if params:
                unknown = ', '.join(params)
                raise Invalid(f'unknown params {unknown}')

        def __asdict__(self, *, keys=None):
            if not keys:
                keys = self.__fields__
            else:
                keys = set(keys) & self.__fields__
            return {k: getattr(self, k) for k in keys}

    def __repr__(self):
        params = ', '.join(
            [f'{k}={v!r}' for k, v in self.__asdict__().items()])
        return f'{type(self).__qualname__}({params})'

    if '__repr__' not in Model.__dict__:
        Model.__repr__ = __repr__

    def __eq__(self, other):
        __fields__ = getattr(other, '__fields__')
        if not __fields__:
            return False
        if self.__fields__ != __fields__:
            return False
        for k in self.__fields__:
            if getattr(self, k, None) != getattr(other, k, None):
                return False
        return True

    if '__eq__' not in Model.__dict__:
        Model.__eq__ = __eq__

    Model.__name__ = f'{model_cls.__name__}@modelclass'
    Model.__qualname__ = f'{model_cls.__qualname__}@modelclass'
    Model.__doc__ = model_cls.__doc__

    return Model


def fields(m):
    return list(m.__fields__)


def asdict(m, *, keys=None):
    return m.__asdict__(keys=keys)


@modelclass
class ModelX:
    pass
