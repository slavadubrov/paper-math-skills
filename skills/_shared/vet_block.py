#!/usr/bin/env python3
"""Refuse a Python check block that uses anything outside a small allowlist.

Usage:
    python3 vet_block.py check.py      # prints OK, or the reasons it refuses
    python3 vet_block.py --self-test

A block passes only if it imports nothing but math, fractions, itertools,
functools and numpy, uses no name containing "__", calls only the builtins in
BUILTINS, and reads only the attributes in ATTRS (NumPy functions, array
methods and the like that small numeric checks need). Anything else is refused,
even if harmless; rewrite the check with allowed names. A block that passes is
not proven safe: this is a filter, not a sandbox, so read a block before you
run it. Write check.py without the indentation of the Markdown fence.
"""

import ast
import builtins
import sys

MODULES = {"math", "fractions", "itertools", "functools", "numpy"}

BUILTINS = {
    "abs", "all", "any", "bool", "complex", "dict", "divmod", "enumerate",
    "filter", "float", "format", "frozenset", "int", "isinstance", "iter",
    "len", "list", "map", "max", "min", "next", "pow", "print", "range",
    "repr", "reversed", "round", "set", "slice", "sorted", "str", "sum",
    "tuple", "type", "zip", "True", "False", "None",
    "ArithmeticError", "AssertionError", "Exception", "FloatingPointError",
    "OverflowError", "ValueError", "ZeroDivisionError",
}

ATTRS = {
    # NumPy functions and constants
    "abs", "all", "allclose", "any", "append", "arange", "arccos", "arcsin",
    "arctan", "arctan2", "argmax", "argmin", "argsort", "argwhere", "around",
    "array", "array_equal", "asarray", "atleast_2d", "bincount", "broadcast_to",
    "ceil", "clip", "column_stack", "concatenate", "conj", "conjugate",
    "corrcoef", "cos", "cosh", "cov", "cross", "cumprod", "cumsum", "diag",
    "diagonal", "diff", "dot", "e", "einsum", "empty", "empty_like", "errstate",
    "exp", "exp2", "expand_dims", "expm1", "eye", "finfo", "flip", "floor",
    "full", "full_like", "hstack", "hypot", "identity", "inf", "inner",
    "isclose", "isfinite", "isinf", "isnan", "kron", "linspace", "log",
    "log10", "log1p", "log2", "logaddexp", "matmul", "max", "maximum", "mean",
    "median", "min", "minimum", "mod", "nan", "nanmax", "nanmean", "nanmin",
    "nansum", "ndindex", "newaxis", "nonzero", "ones", "ones_like", "outer",
    "pad", "percentile", "pi", "polyfit", "polyval", "power", "prod",
    "quantile", "ravel", "repeat", "reshape", "roll", "round", "set_printoptions",
    "sign", "sin", "sinh", "sort", "sqrt", "square", "squeeze", "stack", "std",
    "sum", "swapaxes", "take", "take_along_axis", "tanh", "tensordot", "tile",
    "trace", "transpose", "tril", "tril_indices", "triu", "triu_indices",
    "trunc", "unique", "var", "vdot", "vstack", "where", "zeros", "zeros_like",
    # dtypes
    "bool_", "complex128", "float16", "float32", "float64", "int32", "int64",
    # numpy.linalg and numpy.random
    "linalg", "cholesky", "det", "eig", "eigh", "eigvals", "eigvalsh", "inv",
    "matrix_power", "matrix_rank", "norm", "qr", "solve", "svd",
    "random", "default_rng", "binomial", "choice", "dirichlet", "exponential",
    "integers", "multinomial", "normal", "permutation", "poisson", "shuffle",
    "standard_normal", "uniform",
    # array attributes and methods
    "T", "astype", "copy", "dtype", "fill", "flatten", "imag", "item", "ndim",
    "real", "shape", "size", "tolist",
    # math, fractions, itertools, functools
    "comb", "copysign", "erf", "erfc", "fabs", "factorial", "fsum", "gamma",
    "gcd", "isqrt", "lcm", "lgamma", "perm", "Fraction",
    "denominator", "limit_denominator", "numerator", "accumulate", "chain",
    "combinations", "combinations_with_replacement", "permutations", "product",
    "partial", "reduce",
    # list, dict, set and str methods
    "add", "count", "extend", "get", "index", "items", "join", "keys", "pop",
    "split", "strip", "update", "values",
}


def problems(source: bytes) -> list[str]:
    try:
        tree = ast.parse(source)
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
                if a.name not in ATTRS:
                    out.append(f"line {line}: from {node.module} import {a.name}")
        elif isinstance(node, ast.Name):
            if "__" in node.id:
                out.append(f"line {line}: name {node.id}")
            elif hasattr(builtins, node.id) and node.id not in BUILTINS:
                out.append(f"line {line}: builtin {node.id}")
        elif isinstance(node, ast.Attribute):
            if node.attr not in ATTRS:
                out.append(f"line {line}: attribute .{node.attr}")
    return out


def self_test() -> None:
    ok = b"import numpy as np\nfrom math import log\nx = np.array([0, log(3)])\nprint(np.exp(x).sum())\n"
    assert problems(ok) == [], problems(ok)
    loop = b"for _ in range(2):\n    _v = 1\nprint(type(_v))\n"
    assert problems(loop) == [], problems(loop)
    bad = [
        b"import os",
        b"import numpy.ctypeslib",
        b"from numpy import ctypeslib",
        b"import numpy as np\nnp.zeros(1).ctypes",
        b"import numpy as np\nnp.zeros(1)._ctypes",
        b"open('x')",
        b"getattr(1, 'real')",
        b"locals()",
        b"__import__('os')",
        b"import numpy as np\nnp.load('x.npy')",
        b"import numpy as np\nnp.lib.format",
        b"import numpy as np\nnp.fromfile",
        b"from . import x",
        b"__builtins__",
        b"    import numpy",  # an indented block must be written unindented
    ]
    for b in bad:
        assert problems(b), b
    print("self-test passed")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    elif len(sys.argv) == 2:
        with open(sys.argv[1], "rb") as f:
            found = problems(f.read())
        print("\n".join(found) if found else "OK")
        sys.exit(1 if found else 0)
    else:
        sys.exit(__doc__)
