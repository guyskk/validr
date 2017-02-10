from schema import And, Optional, Schema, Use

schema = Schema({
    "user": {"userid": And(Use(int), lambda x: 0 <= x <= 9)},
    "tags": [And(Use(int), lambda x: 0 <= x)],
    "style": {
        "width": Use(int),
        "height": Use(int),
        "border_width": Use(int),
        "border_style": str,
        "border_color": str,
        "color": str
    },
    Optional("optional"): str
})


CASES = {
    "default": schema.validate
}
