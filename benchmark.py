import json
import sys
from profile import run
from timeit import timeit
from validater import SchemaParser

shared = {
    "size": {
        "width?int": "width",
        "height?int": "height"
    },
    "border": {
        "border-width?int": "border-width",
        "border-style?str": "border-style",
        "border-color?str": "border-color"
    },
    "user": {"userid?int(0,9)": "UserID"},
}
sp = SchemaParser(shared=shared)

style = {
    "width": "400",
    "height": "400",
    "border-width": "5",
    "border-style": "solid",
    "border-color": "red",
    "color": "black"
}
value = {
    "user": {"userid": 5},
    "tags": [1, 2, 5, 9999, 1234567890],
    "style": style
}
schema = {
    "user@user": "User",
    "tags": ["int&min=0"],
    "style": {
        "$self@size@border": "style",
        "color?str": "Color"
    }
}

text = json.dumps(value)
f = sp.parse(schema)


def benchmark():
    print("json.loads: %.3f" %
          timeit("json.loads(text)", globals={"json": json, "text": text}))
    print("validater: %.3f" %
          timeit("f(value)", globals={"f": f, "value": value}))


def profile():
    run("for i in range(10000):\tf(value)")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else None
    if cmd == "-p":
        profile()
    elif cmd == "-t":
        try:
            from beeprint import pp
        except:
            from pprint import pprint as pp
        pp(f(value))
    else:
        benchmark()
