from jsonschema import Draft3Validator, Draft4Validator, validate

schema = {
    "type": "object",
    "properties": {
        "user": {
            "type": "object",
            "properties": {
                "userid": {"type": "number"}
            },
            "required": ["userid"]
        },
        "tags": {
            "type": "array",
            "items": {"type": "number"}
        },
        "style": {
            "type": "object",
            "properties": {
                "width": {"type": "number"},
                "height": {"type": "number"},
                "border_width": {"type": "number"},
                "border_style": {"type": "string"},
                "border_color": {"type": "string"},
                "color": {"type": "string"},
            },
            "required": [
                "width", "height", "border_width",
                "border_style", "border_color", "color"
            ]
        },
        "unknown": {"type": "string"},
    },
    "required": ["user", "tags", "style"]
}


def _validate_0(data):
    validate(data, schema)
    return data


d3 = Draft3Validator(schema)


def _validate_1(data):
    d3.validate(data)
    return data


d4 = Draft4Validator(schema)


def _validate_2(data):
    d4.validate(data)
    return data


validates = [_validate_0, _validate_1, _validate_2]
