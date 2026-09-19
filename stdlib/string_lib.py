"""Standard string library."""
from ..environment import Environment


def build(global_env):
    env = Environment(global_env)

    def length(s): return len(s)
    def upper(s): return s.upper()
    def lower(s): return s.lower()
    def trim(s): return s.strip()
    def ltrim(s): return s.lstrip()
    def rtrim(s): return s.rstrip()
    def split(s, sep=None): return s.split(sep) if sep is not None else s.split()
    def join(parts, sep): return sep.join(str(p) for p in parts)
    def replace(s, old, new): return s.replace(old, new)
    def contains(s, sub): return sub in s
    def startswith(s, prefix): return s.startswith(prefix)
    def endswith(s, suffix): return s.endswith(suffix)
    def index_of(s, sub):
        i = s.find(sub)
        return i
    def char_at(s, i): return s[int(i)]
    def substring(s, start, end=None):
        start = int(start)
        if end is None:
            return s[start:]
        return s[start:int(end)]
    def repeat(s, n): return s * int(n)
    def reverse(s): return s[::-1]
    def is_empty(s): return len(s) == 0
    def to_upper_first(s):
        return s[:1].upper() + s[1:] if s else s

    env.define("len", length)
    env.define("upper", upper)
    env.define("lower", lower)
    env.define("trim", trim)
    env.define("ltrim", ltrim)
    env.define("rtrim", rtrim)
    env.define("split", split)
    env.define("join", join)
    env.define("replace", replace)
    env.define("contains", contains)
    env.define("startswith", startswith)
    env.define("endswith", endswith)
    env.define("index_of", index_of)
    env.define("char_at", char_at)
    env.define("substring", substring)
    env.define("repeat", repeat)
    env.define("reverse", reverse)
    env.define("is_empty", is_empty)
    env.define("capitalize", to_upper_first)
    return env