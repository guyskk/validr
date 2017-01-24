from voluptuous import Required, Schema

schema = Schema({
    Required('user'): {'userid': int},
    Required('tags'): [int],
    Required('style'): {
        Required("width"): int,
        Required("height"): int,
        Required("border_width"): int,
        Required("border_style"): str,
        Required("border_color"): str,
        Required("color"): str
    },
    "unknown": str
})

validates = [schema]
