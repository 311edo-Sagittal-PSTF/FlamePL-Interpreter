"""Callable runtime objects: functions, methods, classes, instances."""
from .environment import Environment
from .errors import ReturnException


class FlamePLFunction:
    def __init__(self, params, body, env, name=None):
        self.params = params
        self.body = body
        self.env = env
        self.name = name or "<lambda>"

    def call(self, args, evaluator):
        if len(args) != len(self.params):
            raise TypeError(f"{self.name} expects {len(self.params)} args, got {len(args)}")
        new_env = Environment(self.env)
        for p, a in zip(self.params, args):
            new_env.define(p, a)
        try:
            evaluator.evaluate_block(self.body, new_env)
        except ReturnException as e:
            return e.value
        return None


class FlamePLBoundMethod:
    def __init__(self, obj, method_fn):
        self.obj = obj
        self.method_fn = method_fn

    def call(self, args, evaluator):
        return self.method_fn.call([self.obj] + args, evaluator)


class FlamePLClass:
    def __init__(self, name, methods, parent=None):
        self.name = name
        self.methods = methods
        self.parent = parent

    def call(self, args, evaluator):
        instance = FlamePLInstance(self)
        init = self.get_method("init")
        if init:
            init.call([instance] + args, evaluator)
        return instance

    def get_method(self, name):
        if name in self.methods:
            return self.methods[name]
        if self.parent:
            return self.parent.get_method(name)
        return None


class FlamePLInstance:
    def __init__(self, klass):
        self.klass = klass
        self.fields = {}

    def get_method(self, name):
        method_fn = self.klass.get_method(name)
        if method_fn:
            return FlamePLBoundMethod(self, method_fn)
        return None