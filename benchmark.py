from timeit import timeit

setup = """
from io import BytesIO
import json
from ijson.backends.python import basic_parse
from validater import parse, validate
schema = parse([{"userid": "int"}])
data_normal = json.dumps([{"userid": "123"}], ensure_ascii=False)
data_deep = '[' * 8000 + ']' * 8000
obj_normal = BytesIO(data_normal.encode('utf-8'))
obj_deep = BytesIO(data_deep.encode('utf-8'))
"""

print('ijson'.center(60, '-'))
s = """
obj_normal.seek(0)
for event, value in basic_parse(obj_normal):
    pass
"""
print("normal data: %.6f sec" % timeit(s, setup, number=1000))

s = """
obj_deep.seek(0)
try:
    for event, value in basic_parse(obj_deep):
        pass
except RecursionError:
    pass
"""
print("deep data: %.6f sec" % timeit(s, setup, number=1000))


print('validater'.center(60, '-'))
s = """
obj_normal.seek(0)
err, val = validate(obj_normal, schema)
"""
print("normal data: %.6f sec" % timeit(s, setup, number=1000))
s = """
obj_deep.seek(0)
err, val = validate(obj_deep, schema)
"""
print("deep data: %.6f sec" % timeit(s, setup, number=1000))


print('standard json'.center(60, '-'))
s = """
obj_normal.seek(0)
json.loads(data_normal)
"""
print("normal data: %.6f sec" % timeit(s, setup, number=1000))
s = """
obj_deep.seek(0)
try:
    json.loads(data_deep)
except RecursionError:
    pass
"""
print("deep data: %.6f sec" % timeit(s, setup, number=1000))
