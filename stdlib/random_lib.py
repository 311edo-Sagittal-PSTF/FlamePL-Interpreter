"""Standard random library."""
import random as _py
from ..environment import Environment


def build(global_env):
    env = Environment(global_env)

    def seed(x=None):
        if x is None:
            _py.seed()
        else:
            _py.seed(int(x))
        return None
    def random():
        from decimal import Decimal
        return Decimal(str(_py.random()))
    def randint(a, b):
        from decimal import Decimal
        return Decimal(_py.randint(int(a), int(b)))
    def choice(lst):
        return _py.choice(lst)
    def shuffle(lst):
        _py.shuffle(lst); return lst
    def sample(lst, k):
        return _py.sample(lst, int(k))
    def uniform(a, b):
        from decimal import Decimal
        return Decimal(str(_py.uniform(float(a), float(b))))

    env.define("seed", seed)
    env.define("random", random)
    env.define("randint", randint)
    env.define("choice", choice)
    env.define("shuffle", shuffle)
    env.define("sample", sample)
    env.define("uniform", uniform)
    return env