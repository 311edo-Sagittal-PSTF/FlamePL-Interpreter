"""Exception types used by the interpreter."""

class ReturnException(Exception):
    """Raised by `return` to unwind to the enclosing function call."""
    def __init__(self, value):
        super().__init__()
        self.value = value

class FlamePLRuntimeError(Exception):
    """Base class for runtime errors raised by the interpreter."""
    pass