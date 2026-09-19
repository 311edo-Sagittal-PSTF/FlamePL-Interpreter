"""AST node classes (pure data holders)."""

class ASTNode: pass

class Number(ASTNode):
    def __init__(self, value): self.value = value
class ImagLiteral(ASTNode):
    def __init__(self, value): self.value = value
class String(ASTNode):
    def __init__(self, value): self.value = value
class BooleanLiteral(ASTNode):
    def __init__(self, value): self.value = value
class NullLiteral(ASTNode): pass
class ListLiteral(ASTNode):
    def __init__(self, elements): self.elements = elements
class PairLiteral(ASTNode):
    def __init__(self, first, second): self.first = first; self.second = second
class DictLiteral(ASTNode):
    def __init__(self, items): self.items = items
class Var(ASTNode):
    def __init__(self, name): self.name = name
class BinaryOp(ASTNode):
    def __init__(self, op, left, right): self.op = op; self.left = left; self.right = right
class UnaryOp(ASTNode):
    def __init__(self, op, expr): self.op = op; self.expr = expr
class Assign(ASTNode):
    def __init__(self, name, expr): self.name = name; self.expr = expr
class If(ASTNode):
    def __init__(self, cond, then_block, elif_clauses, else_block):
        self.cond = cond; self.then_block = then_block
        self.elif_clauses = elif_clauses; self.else_block = else_block
class While(ASTNode):
    def __init__(self, cond, body): self.cond = cond; self.body = body
class ForLoop(ASTNode):
    def __init__(self, var_name, iterable, body):
        self.var_name = var_name; self.iterable = iterable; self.body = body
class Return(ASTNode):
    def __init__(self, expr): self.expr = expr
class FunctionDef(ASTNode):
    def __init__(self, name, params, body): self.name = name; self.params = params; self.body = body
class LambdaDef(ASTNode):
    def __init__(self, params, body): self.params = params; self.body = body
class ClassDef(ASTNode):
    def __init__(self, name, parent_name, methods):
        self.name = name; self.parent_name = parent_name; self.methods = methods
class Call(ASTNode):
    def __init__(self, func, args): self.func = func; self.args = args
class MethodCall(ASTNode):
    def __init__(self, obj, method, args): self.obj = obj; self.method = method; self.args = args
class Index(ASTNode):
    def __init__(self, obj, index): self.obj = obj; self.index = index
class Print(ASTNode):
    def __init__(self, expr): self.expr = expr
class Input(ASTNode):
    def __init__(self, prompt): self.prompt = prompt
class TypeOf(ASTNode):
    def __init__(self, expr): self.expr = expr
class Convert(ASTNode):
    def __init__(self, kind, expr): self.kind = kind; self.expr = expr
class Import(ASTNode):
    def __init__(self, module_name, alias=None):
        self.module_name = module_name; self.alias = alias
class FromImport(ASTNode):
    def __init__(self, module_name, imports):
        self.module_name = module_name; self.imports = imports