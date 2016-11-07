import json
import sys
from profile import run
from timeit import timeit

from schema import And, Optional, Schema, Use

from validr import SchemaParser


def validr_validate():
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
    schema = {
        "user@user": "User",
        "tags": ["int&min=0"],
        "style": {
            "$self@size@border": "style",
            "color?str": "Color"
        },
        "unknown?str&optional": "unknown value"
    }
    return sp.parse(schema)


def validr_simple_validate():
    sp = SchemaParser()
    schema = {
        "user": {"userid?int(0,9)": "UserID"},
        "tags": ["int&min=0"],
        "style": {
            "width?int": "width",
            "height?int": "height",
            "border-width?int": "border-width",
            "border-style?str": "border-style",
            "border-color?str": "border-color",
            "color?str": "Color"
        },
        "unknown?str&optional": "unknown value"
    }
    return sp.parse(schema)


def schema_validate():
    return Schema({
        "user": {"userid": And(Use(int), lambda x: 0 <= x <= 9)},
        "tags": [And(Use(int), lambda x: 0 <= x)],
        "style": {
            "width": Use(int),
            "height": Use(int),
            "border-width": Use(int),
            "border-style": str,
            "border-color": str,
            "color": str
        },
        Optional("unknown"): str
    }).validate

style = {
    "width": 400,
    "height": 400,
    "border-width": 5,
    "border-style": "solid",
    "border-color": "red",
    "color": "black"
}
value = {
    "user": {"userid": 5},
    "tags": [1, 2, 5, 9999, 1234567890],
    "style": style
}


text = json.dumps(value)
f_validr = validr_validate()
f_validr_simple = validr_simple_validate()
f_schema = schema_validate()


def benchmark():
    print("json.loads: %.3f" %
          timeit("json.loads(text)", number=100000,
                 globals={"json": json, "text": text}))
    print("validr: %.3f" %
          timeit("f(value)", number=100000,
                 globals={"f": f_validr, "value": value}))
    print("validr_simple: %.3f" %
          timeit("f(value)", number=100000,
                 globals={"f": f_validr_simple, "value": value}))
    print("schema: %.3f" %
          timeit("f(value)", number=100000,
                 globals={"f": f_schema, "value": value}))


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
        pp(f_validr(value))
        pp(f_validr_simple(value))
        pp(f_schema(value))
    else:
        benchmark()
