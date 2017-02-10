from validr import SchemaParser


def use_refer_mixin():
    shared = {
        "size": {
            "width?int": "width",
            "height?int": "height"
        },
        "border": {
            "border_width?int": "border_width",
            "border_style?str": "border_style",
            "border_color?str": "border_color"
        },
        "user": {"userid?int(0,9)": "UserID"},
    }
    sp = SchemaParser(shared=shared)
    schema = {
        "user@user": "User",
        "tags": ["int&min=0"],
        "style": {
            "$self@size@border": "style",
            "color?str": "Color"
        },
        "optional?str&optional": "unknown value"
    }
    return sp.parse(schema)


def default():
    sp = SchemaParser()
    schema = {
        "user": {"userid?int(0,9)": "UserID"},
        "tags": ["int&min=0"],
        "style": {
            "width?int": "width",
            "height?int": "height",
            "border_width?int": "border_width",
            "border_style?str": "border_style",
            "border_color?str": "border_color",
            "color?str": "Color"
        },
        "optional?str&optional": "unknown value"
    }
    return sp.parse(schema)

CASES = {
    "default": default(),
    "use-refer-mixin": use_refer_mixin(),
}
