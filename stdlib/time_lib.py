"""Standard time library."""
import time as _py
from decimal import Decimal
from ..environment import Environment


def build(global_env):
    env = Environment(global_env)

    def time_fn(): return Decimal(str(_py.time()))
    def sleep(seconds): _py.sleep(float(seconds)); return None
    def clock(): return Decimal(str(_py.perf_counter()))
    def monotonic(): return Decimal(str(_py.monotonic()))

    env.define("time", time_fn)
    env.define("sleep", sleep)
    env.define("clock", clock)
    env.define("monotonic", monotonic)
    return env
