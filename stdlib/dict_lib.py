"""Standard dictionary library."""
from ..environment import Environment


def build(global_env):
    env = Environment(global_env)

    def keys(d): return list(d.keys())
    def values(d): return list(d.values())
    def items(d): return [[k, v] for k, v in d.items()]
    def has_key(d, k): return k in d
    def get(d, k, default=None): return d.get(k, default)
    def set(d, k, v): d[k] = v; return d
    def remove(d, k):
        if k in d:
            del d[k]
        return d
    def length(d): return len(d)
    def clear(d): d.clear(); return d
    def merge(a, b):
        result = dict(a)
        result.update(b)
        return result
    def is_empty(d): return len(d) == 0

    env.define("keys", keys)
    env.define("values", values)
    env.define("items", items)
    env.define("has_key", has_key)
    env.define("get", get)
    env.define("set", set)
    env.define("remove", remove)
    env.define("len", length)
    env.define("clear", clear)
    env.define("merge", merge)
    env.define("is_empty", is_empty)
    return env