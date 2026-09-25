"""Tree-walking evaluator for FlamePL."""
import os
from decimal import Decimal

from . import ast_nodes as ast
from .values import (
    INT_TYPE, FLOAT_TYPE, COMPLEX_TYPE, LIST_TYPE, PAIR_TYPE,
    DICT_TYPE, STR_TYPE, NULL_TYPE, FUNCTION_TYPE, CLASS_TYPE,
    BOOL_TYPE, MODULE_TYPE, FlamePLType, FlamePLComplex, FlamePLPair, FlamePLModule,
)
from .environment import Environment
from .callables import FlamePLFunction, FlamePLClass, FlamePLInstance, FlamePLBoundMethod
from .errors import ReturnException
from .lexer import Lexer
from .parser import Parser
from .stdlib import get_builtin_module, has_builtin_module


class Evaluator:
    def __init__(self, global_env, auto_print=False):
        self.global_env = global_env
        self.loaded_modules = {}
        self.loading = set()
        self.current_file_dir = "."
        self.auto_print = auto_print

    # ---------- NEW: string evaluation ----------
    def eval_string(self, source, env, as_expression=True):
        """Parse and evaluate a source string in the given environment."""
        tokens = Lexer(source).tokenize()
        parser = Parser(tokens)
        if as_expression:
            expr = parser.parse_expression()
            if not parser.match('EOF'):
                raise SyntaxError("eval(): trailing tokens after expression")
            return self.evaluate(expr, env)
        stmts = parser.parse()
        return self.evaluate_block(stmts, env)

    # ---------- NEW: top-level program runner with auto-echo ----------
    _NO_ECHO = (
        ast.Assign, ast.If, ast.While, ast.ForLoop,
        ast.FunctionDef, ast.ClassDef, ast.Return,
        ast.Import, ast.FromImport,
    )

    def evaluate_program(self, statements, env):
        """Evaluate a top-level program. Echo expression results if auto_print."""
        result = None
        for stmt in statements:
            # Print() handles its own output; skip it to avoid double-echo.
            is_print = isinstance(stmt, ast.Print)
            is_statement = isinstance(stmt, self._NO_ECHO)
            value = self.evaluate(stmt, env)
            if self.auto_print and not is_print and not is_statement:
                print(_repr_value(value))
            result = value
        return result

    # ---------- module loading ----------
    def resolve_module_path(self, name, base_dir):
        if isinstance(name, str) and name.endswith('.ae'):
            if os.path.isabs(name):
                return name
            return os.path.normpath(os.path.join(base_dir, name))
        return name

    def load_module(self, name, base_dir):
        path = self.resolve_module_path(name, base_dir)
        if path in self.loaded_modules:
            return self.loaded_modules[path]
        if path in self.loading:
            raise RuntimeError(f"Circular import detected: {name}")
        self.loading.add(path)

        # Built-in module?
        if not (isinstance(path, str) and path.endswith('.ae')) and has_builtin_module(path):
            mod_env = get_builtin_module(path, self.global_env)
            self.loaded_modules[path] = mod_env
            self.loading.remove(path)
            return mod_env

        # Otherwise, try file
        if not os.path.exists(path) and not path.endswith('.ae'):
            alt = path + '.ae'
            if os.path.exists(alt):
                path = alt
        if not os.path.exists(path):
            self.loading.remove(path)
            raise ImportError(f"Module not found: {name} (resolved as {path})")

        with open(path, 'r') as f:
            source = f.read()

        mod_env = Environment(self.global_env)
        tree = Parser(Lexer(source).tokenize()).parse()
        for stmt in tree:
            self.evaluate(stmt, mod_env)

        self.loaded_modules[path] = mod_env
        self.loading.remove(path)
        return mod_env

    # ---------- main dispatch ----------
    def evaluate(self, node, env):
        if isinstance(node, ast.Number):         return node.value
        if isinstance(node, ast.ImagLiteral):    return FlamePLComplex(0, node.value)
        if isinstance(node, ast.String):         return node.value
        if isinstance(node, ast.BooleanLiteral): return node.value
        if isinstance(node, ast.NullLiteral):    return None
        if isinstance(node, ast.Var):            return env.get(node.name)

        if isinstance(node, ast.Assign):
            val = self.evaluate(node.expr, env)
            env.set(node.name, val)
            return val

        if isinstance(node, ast.BinaryOp):
            left = self.evaluate(node.left, env)
            right = self.evaluate(node.right, env)
            op = node.op
            if op == 'and': return bool(left and right)
            if op == 'or':  return bool(left or right)
            if op == '^':   return left ** right
            if op == '//':  return left // right
            if op == '%':   return left % right
            if op == '+':   return left + right
            if op == '-':   return left - right
            if op == '*':   return left * right
            if op == '/':   return left / right
            if op == '=':   return left == right
            if op == '<':   return left < right
            if op == '>':   return left > right
            if op == '<=':  return left <= right
            if op == '>=':  return left >= right
            if op == '!=':  return left != right
            raise RuntimeError(f"Unknown binary op: {op}")

        if isinstance(node, ast.UnaryOp):
            v = self.evaluate(node.expr, env)
            if node.op == '-':   return -v
            if node.op == '+':   return v
            if node.op == 'not': return not bool(v)
            raise RuntimeError(f"Unknown unary op: {node.op}")

        if isinstance(node, ast.If):
            if self.evaluate(node.cond, env):
                return self.evaluate_block(node.then_block, env)
            for c, b in node.elif_clauses:
                if self.evaluate(c, env):
                    return self.evaluate_block(b, env)
            return self.evaluate_block(node.else_block, env)

        if isinstance(node, ast.While):
            while self.evaluate(node.cond, env):
                self.evaluate_block(node.body, env)
            return None

        if isinstance(node, ast.ForLoop):
            it = self.evaluate(node.iterable, env)
            if isinstance(it, list):   items = it
            elif isinstance(it, dict): items = list(it.keys())
            elif isinstance(it, str):  items = list(it)
            else: raise TypeError(f"Cannot iterate over {type(it)}")
            for item in items:
                env.set(node.var_name, item)
                self.evaluate_block(node.body, env)
            return None

        if isinstance(node, ast.Return):
            raise ReturnException(self.evaluate(node.expr, env))

        if isinstance(node, ast.FunctionDef):
            fn = FlamePLFunction(node.params, node.body, env, node.name)
            env.set(node.name, fn)
            return fn

        if isinstance(node, ast.LambdaDef):
            return FlamePLFunction(node.params, node.body, env)

        if isinstance(node, ast.ClassDef):
            parent = None
            if node.parent_name:
                parent = env.get(node.parent_name)
                if not isinstance(parent, FlamePLClass):
                    raise TypeError(f"Parent {node.parent_name} is not a class")
            methods = {}
            for mname, fn in node.methods.items():
                methods[mname] = FlamePLFunction(fn.params, fn.body, env, f"{node.name}.{mname}")
            klass = FlamePLClass(node.name, methods, parent)
            env.set(node.name, klass)
            return klass

        if isinstance(node, ast.Call):
            fn = self.evaluate(node.func, env)
            args = [self.evaluate(a, env) for a in node.args]
            if isinstance(fn, FlamePLFunction):  return fn.call(args, self)
            if isinstance(fn, FlamePLClass):     return fn.call(args, self)
            if callable(fn):                    return fn(*args)
            raise TypeError(f"{fn} is not callable")

        if isinstance(node, ast.MethodCall):
            obj = self.evaluate(node.obj, env)
            args = [self.evaluate(a, env) for a in node.args]
            if isinstance(obj, FlamePLInstance):
                method = obj.get_method(node.method)
                if method:
                    return method.call(args, self)
                raise TypeError(f"No method {node.method} on instance of {obj.klass.name}")
            if isinstance(obj, FlamePLModule):
                try:
                    attr = getattr(obj, node.method)
                except AttributeError:
                    raise TypeError(f"Module {obj.name} has no attribute {node.method}")
                if callable(attr):
                    return attr(*args)
                if not args:
                    return attr
                raise TypeError(f"{node.method} in module {obj.name} is not callable")
            raise TypeError(f"No method {node.method} on {obj}")

        if isinstance(node, ast.Index):
            obj = self.evaluate(node.obj, env)
            idx = self.evaluate(node.index, env)
            if isinstance(obj, (list, dict, str)):
                return obj[idx]
            raise TypeError(f"Cannot index {obj}")

        if isinstance(node, ast.ListLiteral):
            return [self.evaluate(e, env) for e in node.elements]
        if isinstance(node, ast.PairLiteral):
            return FlamePLPair(self.evaluate(node.first, env), self.evaluate(node.second, env))
        if isinstance(node, ast.DictLiteral):
            d = {}
            for k, v in node.items:
                d[self.evaluate(k, env)] = self.evaluate(v, env)
            return d

        if isinstance(node, ast.Print):
            print(self.evaluate(node.expr, env)); return None
        if isinstance(node, ast.Input):
            return input(str(self.evaluate(node.prompt, env)))

        if isinstance(node, ast.TypeOf):
            return self._type_of(self.evaluate(node.expr, env))

        if isinstance(node, ast.Convert):
            v = self.evaluate(node.expr, env)
            if node.kind == 'int':   return int(v)
            if node.kind == 'float': return Decimal(str(v))
            if node.kind == 'str':   return str(v)
            raise RuntimeError(f"Unknown conversion: {node.kind}")

        if isinstance(node, ast.Import):
            mod_env = self.load_module(node.module_name, self.current_file_dir)
            mod_obj = FlamePLModule(mod_env, node.module_name)
            alias = node.alias
            if not alias:
                if isinstance(node.module_name, str):
                    base = os.path.basename(node.module_name)
                    alias = base[:-3] if base.endswith('.ae') else base
                else:
                    alias = node.module_name
            env.set(alias, mod_obj)
            return mod_obj

        if isinstance(node, ast.FromImport):
            mod_env = self.load_module(node.module_name, self.current_file_dir)
            for orig, alias in node.imports:
                try:
                    value = mod_env.get(orig)
                except NameError:
                    raise ImportError(f"Module {node.module_name} has no attribute {orig}")
                env.set(alias or orig, value)
            return None

        raise RuntimeError(f"Unknown AST node: {type(node)}")

    def evaluate_block(self, block, env):
        result = None
        for stmt in block:
            result = self.evaluate(stmt, env)
        return result

    def _type_of(self, val):
        if isinstance(val, bool):              return BOOL_TYPE
        if isinstance(val, Decimal):
            return INT_TYPE if val.as_tuple().exponent >= 0 else FLOAT_TYPE
        if isinstance(val, int):               return INT_TYPE
        if isinstance(val, float):             return FLOAT_TYPE
        if isinstance(val, FlamePLComplex):     return COMPLEX_TYPE
        if isinstance(val, list):              return LIST_TYPE
        if isinstance(val, FlamePLPair):        return PAIR_TYPE
        if isinstance(val, dict):              return DICT_TYPE
        if isinstance(val, str):               return STR_TYPE
        if val is None:                        return NULL_TYPE
        if isinstance(val, (FlamePLFunction, FlamePLBoundMethod)): return FUNCTION_TYPE
        if isinstance(val, (FlamePLClass, FlamePLInstance)):       return CLASS_TYPE
        if isinstance(val, FlamePLModule):      return MODULE_TYPE
        return FlamePLType(type(val).__name__)

def _repr_value(v):
    """User-facing representation for REPL auto-echo."""
    if v is None:
        return "null"
    if isinstance(v, str):
        return repr(v)       # quotes so strings stand out
    return str(v)