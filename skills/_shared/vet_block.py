#!/usr/bin/env python3
"""Refuse a Python check block that reaches beyond arithmetic.

Usage:
    python3 vet_block.py check.py      # prints OK, or the reasons it refuses
    python3 vet_block.py --self-test

A block passes only if it imports nothing but math, fractions, itertools,
functools and numpy, uses no name containing "__" and no attribute starting
with "_", and uses none of the builtins or NumPy members that read or write
files, run code or reach native libraries. This is a filter, not a sandbox: a block that passes
still runs with your permissions, so run it only after reading it.
"""

import ast
import sys
import textwrap

MODULES = {"math", "fractions", "itertools", "functools", "numpy"}
NAMES = {
    "open", "exec", "eval", "compile", "getattr", "setattr", "delattr",
    "globals", "locals", "vars", "dir", "help", "input", "breakpoint",
}
ATTRS = {
    "ctypes", "ctypeslib", "lib", "core", "f2py", "testing", "memmap",
    "load", "save", "savez", "savez_compressed", "loadtxt", "savetxt",
    "genfromtxt", "fromfile", "tofile", "fromregex", "DataSource", "dump",
    "dumps", "show_config", "show_runtime", "os", "sys",
}


def problems(source: str) -> list[str]:
    try:
        tree = ast.parse(textwrap.dedent(source))
    except SyntaxError as e:
        return [f"syntax error: {e}"]
    out = []
    for node in ast.walk(tree):
        line = getattr(node, "lineno", "?")
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name not in MODULES:
                    out.append(f"line {line}: import {a.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module not in MODULES or node.level:
                out.append(f"line {line}: from {node.module} import ...")
            for a in node.names:
                if a.name == "*" or a.name.startswith("_") or a.name in ATTRS:
                    out.append(f"line {line}: from {node.module} import {a.name}")
        elif isinstance(node, ast.Name):
            if "__" in node.id or node.id in NAMES:
                out.append(f"line {line}: name {node.id}")
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith("_") or node.attr in ATTRS:
                out.append(f"line {line}: attribute .{node.attr}")
    return out


def self_test() -> None:
    ok = "import numpy as np\nfrom math import log\nx = np.array([0, log(3)])\nprint(np.exp(x).sum())\n"
    assert problems(ok) == [], problems(ok)
    loop = "    for _ in range(2):\n        _v = 1\n    print(type(_v))\n"
    assert problems(loop) == [], problems(loop)
    bad = [
        "import os",
        "import numpy.ctypeslib",
        "from numpy import ctypeslib",
        "import numpy as np\nnp.zeros(1).ctypes",
        "import numpy as np\nnp.zeros(1)._ctypes",
        "open('x')",
        "getattr(1, 'real')",
        "locals()",
        "__import__('os')",
        "import numpy as np\nnp.load('x.npy')",
        "import numpy as np\nnp.lib.format",
        "from . import x",
        "__builtins__",
    ]
    for b in bad:
        assert problems(b), b
    print("self-test passed")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    elif len(sys.argv) == 2:
        found = problems(open(sys.argv[1], encoding="utf-8").read())
        print("\n".join(found) if found else "OK")
        sys.exit(1 if found else 0)
    else:
        sys.exit(__doc__)
