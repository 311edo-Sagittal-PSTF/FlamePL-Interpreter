"""Registry of built-in standard library modules."""
from . import (
    math_lib, string_lib, list_lib, dict_lib,
    io_lib, random_lib, time_lib, os_lib,
)

_BUILTIN_MODULES = {
    'math':   math_lib.build,
    'string': string_lib.build,
    'list':   list_lib.build,
    'dict':   dict_lib.build,
    'io':     io_lib.build,
    'random': random_lib.build,
    'time':   time_lib.build,
    'os':     os_lib.build,
}


def has_builtin_module(name):
    return name in _BUILTIN_MODULES


def get_builtin_module(name, global_env):
    if name not in _BUILTIN_MODULES:
        raise ImportError(f"Unknown built-in module: {name}")
    return _BUILTIN_MODULES[name](global_env)