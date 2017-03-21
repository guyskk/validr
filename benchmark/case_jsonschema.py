from jsonschema import Draft3Validator, Draft4Validator

schema = {
    'type': 'object',
    'properties': {
        'user': {
            'type': 'object',
            'properties': {
                'userid': {'type': 'number'}
            },
            'required': ['userid']
        },
        'tags': {
            'type': 'array',
            'items': {'type': 'number'}
        },
        'style': {
            'type': 'object',
            'properties': {
                'width': {'type': 'number'},
                'height': {'type': 'number'},
                'border_width': {'type': 'number'},
                'border_style': {'type': 'string'},
                'border_color': {'type': 'string'},
                'color': {'type': 'string'},
            },
            'required': [
                'width', 'height', 'border_width',
                'border_style', 'border_color', 'color'
            ]
        },
        'optional': {'type': 'string'},
    },
    'required': ['user', 'tags', 'style']
}

d3 = Draft3Validator(schema)
d4 = Draft4Validator(schema)


def draft3(data):
    d3.validate(data)
    return data


def draft4(data):
    d4.validate(data)
    return data


CASES = {
    'draft3': draft3,
    'draft4': draft4,
}
