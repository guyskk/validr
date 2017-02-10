from util import case


@case({
    "bool": [
        (True, True),
        (False, False),
        [None, "", "true", "false", "True", "False", 0, 1]
    ],
    "bool&default=false": [
        (None, False),
        ["", 0]
    ],
})
def test_bool():
    pass
