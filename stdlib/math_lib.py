"""Standard math library."""
import math as _py
from decimal import Decimal
from ..environment import Environment
from ..values import FlamePLComplex
from ._helpers import to_float, to_int, to_decimal


def build(global_env):
    env = Environment(global_env)

    def sqrt(x):
        return to_decimal(_py.sqrt(to_float(x)))

    def sin(x):
        return to_decimal(_py.sin(to_float(x)))

    def cos(x):
        return to_decimal(_py.cos(to_float(x)))

    def tan(x):
        return to_decimal(_py.tan(to_float(x)))

    def asin(x):
        return to_decimal(_py.asin(to_float(x)))

    def acos(x):
        return to_decimal(_py.acos(to_float(x)))

    def atan(x):
        return to_decimal(_py.atan(to_float(x)))

    def exp(x):
        return to_decimal(_py.exp(to_float(x)))

    def log(x, base=None):
        if base is None:
            return to_decimal(_py.log(to_float(x)))
        return to_decimal(_py.log(to_float(x), to_float(base)))

    def log10(x):
        return to_decimal(_py.log10(to_float(x)))

    def log2(x):
        return to_decimal(_py.log2(to_float(x)))

    def floor(x):
        return Decimal(to_int(_py.floor(to_float(x))))

    def ceil(x):
        return Decimal(to_int(_py.ceil(to_float(x))))

    def abs_fn(x):
        if isinstance(x, FlamePLComplex):
            return to_decimal(_py.hypot(float(x.real), float(x.imag)))
        if isinstance(x, Decimal):
            return abs(x)
        return to_decimal(abs(to_float(x)))

    def pow_fn(a, b):
        return to_decimal(_py.pow(to_float(a), to_float(b)))

    def hypot(a, b):
        return to_decimal(_py.hypot(to_float(a), to_float(b)))

    def min_fn(*args):
        flat = []
        for a in args:
            if isinstance(a, list):
                flat.extend(a)
            else:
                flat.append(a)
        return flat[0] if not flat else min(flat)

    def max_fn(*args):
        flat = []
        for a in args:
            if isinstance(a, list):
                flat.extend(a)
            else:
                flat.append(a)
        return flat[0] if not flat else max(flat)

    env.define("sqrt", sqrt)
    env.define("sin", sin)
    env.define("cos", cos)
    env.define("tan", tan)
    env.define("asin", asin)
    env.define("acos", acos)
    env.define("atan", atan)
    env.define("exp", exp)
    env.define("log", log)
    env.define("log10", log10)
    env.define("log2", log2)
    env.define("floor", floor)
    env.define("ceil", ceil)
    env.define("abs", abs_fn)
    env.define("pow", pow_fn)
    env.define("hypot", hypot)
    env.define("min", min_fn)
    env.define("max", max_fn)
    env.define("pi", Decimal(str(_py.pi)))
    env.define("e", Decimal(str(_py.e)))
    return env
