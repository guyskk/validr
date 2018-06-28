from validr import T, Compiler


def default():
    compiler = Compiler()
    schema = T.dict(
        user=T.dict(
            userid=T.int.min(0).max(9).desc('UserID'),
        ),
        tags=T.list(T.int.min(0)),
        style=T.dict(
            width=T.int.desc('width'),
            height=T.int.desc('height'),
            border_width=T.int.desc('border_width'),
            border_style=T.str.desc('border_style'),
            border_color=T.str.desc('border_color'),
            color=T.str.desc('color')
        ),
        optional=T.str.optional.desc('unknown value')
    )
    return compiler.compile(schema)


CASES = {
    'default': default(),
}
