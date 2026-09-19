"""Recursive-descent parser for FlamePL."""
from .tokens import Token
from . import ast_nodes as ast


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_type=None, expected_value=None):
        tok = self.peek()
        if expected_type is not None and tok.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {tok.type} at line {tok.line}")
        if expected_value is not None and tok.value != expected_value:
            raise SyntaxError(f"Expected '{expected_value}', got '{tok.value}' at line {tok.line}")
        self.pos += 1
        return tok

    def match(self, type_, value=None):
        tok = self.peek()
        if tok.type == type_ and (value is None or tok.value == value):
            self.pos += 1
            return True
        return False

    # ----- top level -----
    def parse(self):
        stmts = []
        while not self.match('EOF'):
            stmts.append(self.parse_statement())
        return stmts

    def parse_statement(self):
        tok = self.peek()
        if tok.type == 'KEYWORD':
            if tok.value == 'fn':        return self.parse_function_def()
            elif tok.value == 'class':   return self.parse_class_def()
            elif tok.value == 'if':      return self.parse_if()
            elif tok.value == 'while':   return self.parse_while()
            elif tok.value == 'for':     return self.parse_for()
            elif tok.value == 'return':
                self.consume('KEYWORD', 'return')
                return ast.Return(self.parse_expression())
            elif tok.value == 'import':  return self.parse_import()
            elif tok.value == 'from':    return self.parse_from_import()

        left = self.parse_expression()
        if self.match('ASSIGN'):
            if not isinstance(left, ast.Var):
                raise SyntaxError("Left side of assignment must be a variable")
            return ast.Assign(left.name, self.parse_expression())
        return left

    # ----- imports -----
    def parse_import(self):
        self.consume('KEYWORD', 'import')
        tok = self.peek()
        if tok.type == 'STRING':
            module_name = self.consume('STRING').value
        elif tok.type == 'IDENTIFIER':
            module_name = self.consume('IDENTIFIER').value
        else:
            raise SyntaxError("Expected string or identifier after import")
        alias = None
        if self.match('KEYWORD', 'as'):
            alias = self.consume('IDENTIFIER').value
        return ast.Import(module_name, alias)

    def parse_from_import(self):
        self.consume('KEYWORD', 'from')
        tok = self.peek()
        if tok.type == 'STRING':
            module_name = self.consume('STRING').value
        elif tok.type == 'IDENTIFIER':
            module_name = self.consume('IDENTIFIER').value
        else:
            raise SyntaxError("Expected string or identifier after from")
        self.consume('KEYWORD', 'import')
        imports = []
        while True:
            orig = self.consume('IDENTIFIER').value
            alias = None
            if self.match('KEYWORD', 'as'):
                alias = self.consume('IDENTIFIER').value
            imports.append((orig, alias))
            if not self.match('OP', ','):
                break
        return ast.FromImport(module_name, imports)

    # ----- function / class -----
    def parse_function_def(self):
        self.consume('KEYWORD', 'fn')
        name = self.consume('IDENTIFIER').value
        self.consume('OP', '(')
        params = []
        if not self.match('OP', ')'):
            while True:
                params.append(self.consume('IDENTIFIER').value)
                if self.match('OP', ','):
                    continue
                self.consume('OP', ')')
                break
        body = self.parse_block()
        self.consume('KEYWORD', 'end')          # <-- fix: consume closing 'end'
        return ast.FunctionDef(name, params, body)

    def parse_lambda(self):
        self.consume('KEYWORD', 'lambda')
        self.consume('OP', '(')
        params = []
        if not self.match('OP', ')'):
            while True:
                params.append(self.consume('IDENTIFIER').value)
                if self.match('OP', ','):
                    continue
                self.consume('OP', ')')
                break
        self.consume('OP', '->')
        body = self.parse_expression()
        return ast.LambdaDef(params, [body])

    def parse_class_def(self):
        self.consume('KEYWORD', 'class')
        name = self.consume('IDENTIFIER').value
        parent = None
        if self.match('OP', ':'):
            parent = self.consume('IDENTIFIER').value
        methods = {}
        while True:
            tok = self.peek()
            if tok.type == 'KEYWORD' and tok.value == 'end':
                self.consume('KEYWORD', 'end'); break
            if tok.type == 'KEYWORD' and tok.value == 'fn':
                fn = self.parse_function_def()
                methods[fn.name] = fn
            else:
                raise SyntaxError(f"Expected method definition inside class, got {tok}")
        return ast.ClassDef(name, parent, methods)

    # ----- blocks and control flow -----
    def parse_block(self):
        stmts = []
        while True:
            tok = self.peek()
            if tok.type == 'KEYWORD' and tok.value in ('end', 'else', 'elseif'):
                break
            if tok.type == 'EOF':
                break
            stmts.append(self.parse_statement())
        return stmts

    def parse_if(self):
        self.consume('KEYWORD', 'if')
        cond = self.parse_expression()
        self.consume('KEYWORD', 'then')
        then_block = []
        while True:
            tok = self.peek()
            if tok.type == 'KEYWORD' and tok.value in ('else', 'elseif', 'end'):
                break
            then_block.append(self.parse_statement())
        elif_clauses = []
        while self.match('KEYWORD', 'elseif'):
            ec = self.parse_expression()
            self.consume('KEYWORD', 'then')
            eb = []
            while True:
                tok = self.peek()
                if tok.type == 'KEYWORD' and tok.value in ('else', 'elseif', 'end'):
                    break
                eb.append(self.parse_statement())
            elif_clauses.append((ec, eb))
        else_block = []
        if self.match('KEYWORD', 'else'):
            while True:
                tok = self.peek()
                if tok.type == 'KEYWORD' and tok.value == 'end':
                    break
                else_block.append(self.parse_statement())
        self.consume('KEYWORD', 'end')
        return ast.If(cond, then_block, elif_clauses, else_block)

    def parse_while(self):
        self.consume('KEYWORD', 'while')
        cond = self.parse_expression()
        self.consume('KEYWORD', 'do')
        body = []
        while True:
            tok = self.peek()
            if tok.type == 'KEYWORD' and tok.value == 'end':
                break
            body.append(self.parse_statement())
        self.consume('KEYWORD', 'end')
        return ast.While(cond, body)

    def parse_for(self):
        self.consume('KEYWORD', 'for')
        var = self.consume('IDENTIFIER').value
        self.consume('KEYWORD', 'in')
        iterable = self.parse_expression()
        self.consume('KEYWORD', 'do')
        body = []
        while True:
            tok = self.peek()
            if tok.type == 'KEYWORD' and tok.value == 'end':
                break
            body.append(self.parse_statement())
        self.consume('KEYWORD', 'end')
        return ast.ForLoop(var, iterable, body)

    # ----- expressions -----
    def parse_expression(self): return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match('KEYWORD', 'or'):
            left = ast.BinaryOp('or', left, self.parse_and())
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.match('KEYWORD', 'and'):
            left = ast.BinaryOp('and', left, self.parse_not())
        return left

    def parse_not(self):
        if self.match('KEYWORD', 'not'):
            return ast.UnaryOp('not', self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_additive()
        if self.match('OP', '=') or self.match('OP', '<') or self.match('OP', '>') \
           or self.match('OP', '<=') or self.match('OP', '>=') or self.match('OP', '!='):
            op = self.tokens[self.pos-1].value
            return ast.BinaryOp(op, left, self.parse_additive())
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.match('OP', '+') or self.match('OP', '-'):
            op = self.tokens[self.pos-1].value
            left = ast.BinaryOp(op, left, self.parse_multiplicative())
        return left

    def parse_multiplicative(self):
        left = self.parse_power()
        while self.match('OP', '*') or self.match('OP', '/') \
           or self.match('OP', '//') or self.match('OP', '%'):
            op = self.tokens[self.pos-1].value
            left = ast.BinaryOp(op, left, self.parse_power())
        return left

    def parse_power(self):
        left = self.parse_unary()
        if self.match('OP', '^'):
            return ast.BinaryOp('^', left, self.parse_power())
        return left

    def parse_unary(self):
        if self.match('OP', '-') or self.match('OP', '+'):
            op = self.tokens[self.pos-1].value
            return ast.UnaryOp(op, self.parse_unary())
        return self.parse_postfix()

    def parse_postfix(self):
        expr = self.parse_atom()
        while True:
            if self.match('OP', '['):
                idx = self.parse_expression(); self.consume('OP', ']')
                expr = ast.Index(expr, idx)
            elif self.match('OP', '('):
                args = []
                if not self.match('OP', ')'):
                    while True:
                        args.append(self.parse_expression())
                        if self.match('OP', ','): continue
                        self.consume('OP', ')'); break
                expr = ast.Call(expr, args)
            elif self.match('OP', '.'):
                mname = self.consume('IDENTIFIER').value
                self.consume('OP', '(')
                args = []
                if not self.match('OP', ')'):
                    while True:
                        args.append(self.parse_expression())
                        if self.match('OP', ','): continue
                        self.consume('OP', ')'); break
                expr = ast.MethodCall(expr, mname, args)
            else:
                break
        return expr

    def parse_atom(self):
        tok = self.peek()
        if tok.type == 'NUMBER':
            self.consume('NUMBER'); return ast.Number(tok.value)
        if tok.type == 'IMAG':
            self.consume('IMAG');   return ast.ImagLiteral(tok.value)
        if tok.type == 'STRING':
            self.consume('STRING'); return ast.String(tok.value)
        if tok.type == 'KEYWORD' and tok.value in ('true', 'false'):
            self.consume('KEYWORD'); return ast.BooleanLiteral(tok.value == 'true')
        if tok.type == 'IDENTIFIER':
            self.consume('IDENTIFIER')
            if tok.value == 'null':       return ast.NullLiteral()
            if tok.value == 'to_int':
                self.consume('OP', '('); e = self.parse_expression(); self.consume('OP', ')')
                return ast.Convert('int', e)
            if tok.value == 'to_float':
                self.consume('OP', '('); e = self.parse_expression(); self.consume('OP', ')')
                return ast.Convert('float', e)
            if tok.value == 'to_str':
                self.consume('OP', '('); e = self.parse_expression(); self.consume('OP', ')')
                return ast.Convert('str', e)
            if tok.value == 'type_of':
                self.consume('OP', '('); e = self.parse_expression(); self.consume('OP', ')')
                return ast.TypeOf(e)
            return ast.Var(tok.value)
        if tok.type == 'OP' and tok.value == '(':
            self.consume('OP', '(')
            expr = self.parse_expression()
            if self.match('OP', ','):
                second = self.parse_expression(); self.consume('OP', ')')
                return ast.PairLiteral(expr, second)
            self.consume('OP', ')')
            return expr
        if tok.type == 'OP' and tok.value == '[':
            self.consume('OP', '[')
            elements = []
            if not self.match('OP', ']'):
                while True:
                    elements.append(self.parse_expression())
                    if self.match('OP', ','): continue
                    self.consume('OP', ']'); break
            return ast.ListLiteral(elements)
        if tok.type == 'OP' and tok.value == '{':
            self.consume('OP', '{')
            items = []
            if not self.match('OP', '}'):
                while True:
                    k = self.parse_expression(); self.consume('OP', ':')
                    v = self.parse_expression()
                    items.append((k, v))
                    if self.match('OP', ','): continue
                    self.consume('OP', '}'); break
            return ast.DictLiteral(items)
        if tok.type == 'KEYWORD' and tok.value == 'lambda':
            return self.parse_lambda()
        raise SyntaxError(f"Unexpected token {tok}")