import re
from glob import glob


def pyx_to_py(text: str, debug=False):
    """Only support validr's usage."""
    lines = []
    for i, line in enumerate(text.splitlines(keepends=True), 1):
        origin = line
        if line.lstrip().startswith('cdef class'):
            line = line.replace('cdef class', 'class')
        for pre in ['cpdef inline', 'cdef inline', 'cpdef', 'cdef']:
            for pre_type in ['bint', 'str', 'int', 'float', 'dict', 'list', '']:
                t = (pre + ' ' + pre_type).strip()
                if line.lstrip().startswith(t) and line.rstrip().endswith(':'):
                    line = line.replace(t, 'def')
        for pre in ['cdef', 'cpdef']:
            for t in ['bint', 'str', 'int', 'float', 'dict', 'list']:
                cdef_t = '{} {} '.format(pre, t)
                if line.lstrip().startswith(cdef_t):
                    if '=' in line:
                        line = line.replace(cdef_t, '')
                    else:
                        line = re.sub(r'(\s*)(\S.*)', r'\1# \2', line)
        if re.match(r'\s*\w*def\s\w+\(.*(,|\):)', line) or re.match(r'\s+.*=.*(\):$|,$)', line):
            line = re.sub(r'(bint|str|int|float|dict|list)\s(\w+)', r'\2', line)
        if debug and origin != line:
            print('{:>3d}- '.format(i) + origin, end='')
            print('{:>3d}+ '.format(i) + line, end='')
        lines.append(line)
    return ''.join(lines)


def compile_pyx_to_py(filepaths, debug=False):
    """Compile *.pyx to pure python using regex and string replaces."""
    for filepath in filepaths:
        py_filepath = filepath.replace('_c.pyx', '_py.py')
        with open(filepath, encoding='utf-8') as f:
            text = f.read()
        pure_py = pyx_to_py(text, debug=debug)
        with open(py_filepath, 'w', encoding='utf-8') as f:
            f.write(pure_py)


if __name__ == "__main__":
    compile_pyx_to_py(glob('src/validr/*.pyx'), debug=True)
