from schematics.models import Model
from schematics.types import IntType, ListType, ModelType, StringType


class User(Model):
    userid = IntType(required=True)


class Style(Model):
    width = IntType(required=True)
    height = IntType(required=True)
    border_width = IntType(required=True)
    border_style = StringType(required=True)
    border_color = StringType(required=True)
    color = StringType(required=True)


class Data(Model):
    user = ModelType(User, required=True)
    tags = ListType(IntType)
    style = ModelType(Style, required=True)
    unknown = StringType(required=False)


def _validate_0(data):
    m = Data(data)
    m.validate()
    return m.to_primitive()


validates = [_validate_0]
