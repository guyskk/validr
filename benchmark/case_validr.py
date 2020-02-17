from validr import T, Compiler, modelclass, asdict, builtin_validators


@modelclass
class Model:
    user = T.dict(userid=T.int.min(0).max(9).desc("UserID"))
    tags = T.union([
        T.int.min(0),
        T.list(T.int.min(0)),
    ])
    style = T.dict(
        width=T.int.desc("width"),
        height=T.int.desc("height"),
        border_width=T.int.desc("border_width"),
        border_style=T.str.desc("border_style"),
        border_color=T.str.desc("border_color"),
        color=T.str.desc("color"),
    )
    optional = T.str.optional.desc("unknown value")


compiler = Compiler()
default = compiler.compile(T(Model))

any_validators = {}
for name, v in builtin_validators.items():
    if name in ('list', 'dict'):
        continue
    any_validators[name] = builtin_validators['any']

any_compiler = Compiler(validators=any_validators)
any_case = any_compiler.compile(T(Model))


def model(value):
    return asdict(Model(value))


CASES = {"default": default, "model": model, "any": any_case}
