"""Standard list library."""
from ..environment import Environment


def build(global_env):
    env = Environment(global_env)

    def length(lst): return len(lst)
    def push(lst, item): lst.append(item); return lst
    def pop(lst): return lst.pop() if lst else None
    def pop_at(lst, i): return lst.pop(int(i))
    def insert(lst, i, item): lst.insert(int(i), item); return lst
    def remove_at(lst, i): return lst.pop(int(i))
    def contains(lst, item): return item in lst
    def index_of(lst, item):
        try: return lst.index(item)
        except ValueError: return -1
    def reverse(lst): return list(reversed(lst))
    def sort(lst):
        try:
            return sorted(lst)
        except TypeError:
            return sorted(lst, key=lambda x: str(x))
    def slice(lst, start, end=None):
        start = int(start)
        if end is None:
            return lst[start:]
        return lst[start:int(end)]
    def concat(a, b): return list(a) + list(b)
    def range_fn(*args):
        args = [int(a) for a in args]
        return list(range(*args))
    def sum_fn(lst):
        total = 0
        for x in lst:
            total = total + x
        return total
    def map_list(fn, lst, evaluator=None):
        return [fn([x], evaluator) for x in lst]
    def filter_list(fn, lst, evaluator=None):
        return [x for x in lst if fn([x], evaluator)]
    def reduce_list(fn, lst, init=None, evaluator=None):
        it = iter(lst)
        if init is None:
            try:
                acc = next(it)
            except StopIteration:
                return None
        else:
            acc = init
        for x in it:
            acc = fn([acc, x], evaluator)
        return acc

    env.define("len", length)
    env.define("push", push)
    env.define("append", push)
    env.define("pop", pop)
    env.define("pop_at", pop_at)
    env.define("insert", insert)
    env.define("remove_at", remove_at)
    env.define("contains", contains)
    env.define("index_of", index_of)
    env.define("reverse", reverse)
    env.define("sort", sort)
    env.define("slice", slice)
    env.define("concat", concat)
    env.define("range", range_fn)
    env.define("sum", sum_fn)
    return env