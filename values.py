"""Runtime value types and first-class type objects."""
from decimal import Decimal


class FlamePLType:
    """First-class type objects (int, float, list, ...)."""
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name


INT_TYPE     = FlamePLType("int")
FLOAT_TYPE   = FlamePLType("float")
COMPLEX_TYPE = FlamePLType("complex")
LIST_TYPE    = FlamePLType("list")
PAIR_TYPE    = FlamePLType("pair")
DICT_TYPE    = FlamePLType("dict")
STR_TYPE     = FlamePLType("str")
NULL_TYPE    = FlamePLType("null")
FUNCTION_TYPE= FlamePLType("function")
CLASS_TYPE   = FlamePLType("class")
BOOL_TYPE    = FlamePLType("bool")
MODULE_TYPE  = FlamePLType("module")


class FlamePLComplex:
    """Arbitrary-precision complex number (real, imag as Decimal)."""
    def __init__(self, real, imag):
        self.real = Decimal(real)
        self.imag = Decimal(imag)

    def __repr__(self):
        if self.imag < 0:
            return f"{self.real} - {abs(self.imag)}i"
        return f"{self.real} + {self.imag}i"

    def __add__(self, o):
        if isinstance(o, FlamePLComplex):
            return FlamePLComplex(self.real + o.real, self.imag + o.imag)
        return FlamePLComplex(self.real + Decimal(o), self.imag)

    def __sub__(self, o):
        if isinstance(o, FlamePLComplex):
            return FlamePLComplex(self.real - o.real, self.imag - o.imag)
        return FlamePLComplex(self.real - Decimal(o), self.imag)

    def __mul__(self, o):
        if isinstance(o, FlamePLComplex):
            r = self.real * o.real - self.imag * o.imag
            i = self.real * o.imag + self.imag * o.real
            return FlamePLComplex(r, i)
        return FlamePLComplex(self.real * Decimal(o), self.imag * Decimal(o))

    def __truediv__(self, o):
        if isinstance(o, FlamePLComplex):
            d = o.real ** 2 + o.imag ** 2
            r = (self.real * o.real + self.imag * o.imag) / d
            i = (self.imag * o.real - self.real * o.imag) / d
            return FlamePLComplex(r, i)
        return FlamePLComplex(self.real / Decimal(o), self.imag / Decimal(o))

    def __mod__(self, o):
        if isinstance(o, FlamePLComplex):
            return FlamePLComplex(self.real % o.real, self.imag % o.imag)
        return FlamePLComplex(self.real % Decimal(o), self.imag % Decimal(o))

    def __eq__(self, o):
        return isinstance(o, FlamePLComplex) and self.real == o.real and self.imag == o.imag


class FlamePLPair:
    """Ordered pair."""
    def __init__(self, first, second):
        self.first = first
        self.second = second
    def __repr__(self):
        return f"({self.first}, {self.second})"


class FlamePLModule:
    """Wrapper exposing a module's environment via attribute access."""
    def __init__(self, env, name):
        self.env = env
        self.name = name
    def __getattr__(self, name):
        if name == "env":
            return self.env
        try:
            return self.env.get(name)
        except NameError:
            raise AttributeError(f"module {self.name} has no attribute {name}")
    def __repr__(self):
        return f"<module {self.name}>"