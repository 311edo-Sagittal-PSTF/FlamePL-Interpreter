"""Shared helpers for standard library modules."""
from decimal import Decimal
from ..values import FlamePLComplex


def to_float(x):
    if isinstance(x, FlamePLComplex):
        raise TypeError("Cannot convert complex to float")
    if isinstance(x, Decimal):
        return float(x)
    if isinstance(x, bool):
        return float(x)
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        return float(x)
    raise TypeError(f"Cannot convert {type(x).__name__} to float")


def to_int(x):
    if isinstance(x, FlamePLComplex):
        raise TypeError("Cannot convert complex to int")
    if isinstance(x, Decimal):
        return int(x)
    if isinstance(x, bool):
        return int(x)
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, str):
        return int(x)
    raise TypeError(f"Cannot convert {type(x).__name__} to int")


def to_decimal(x):
    return Decimal(str(to_float(x)))


def to_str(x):
    return str(x)