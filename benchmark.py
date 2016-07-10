import json
import sys
from profile import run
from timeit import timeit
from validater import SchemaParser

sp = SchemaParser()
value = {
    "user": {"userid": 5},
    "tags": [1, 2, 5]
}
schema = {
    "user": {"userid?int(0,9)": "UserID"},
    "tags": ["int(0,9)"]
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
    if len(sys.argv) > 1 and sys.argv[1] == "-p":
        profile()
    else:
        benchmark()
