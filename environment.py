"""Lexical environments for variable lookup and closures."""

class Environment:
    def __init__(self, outer=None):
        self.outer = outer
        self.data = {}

    def get(self, name):
        if name in self.data:
            return self.data[name]
        if self.outer:
            return self.outer.get(name)
        raise NameError(f"Undefined variable: {name}")

    def set(self, name, value):
        self.data[name] = value

    def define(self, name, value):
        self.data[name] = value

    def extend(self):
        return Environment(self)