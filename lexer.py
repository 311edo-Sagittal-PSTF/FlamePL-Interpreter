"""Tokenizer for the FlamePL language."""
import re
from .tokens import Token


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []

    def tokenize(self):
        while self.pos < len(self.source):
            ch = self.source[self.pos]
            if ch in ' \t\r':
                self.pos += 1; continue
            if ch == '\n':
                self.line += 1; self.pos += 1; continue

            # Comments
            if ch == '#':
                self.pos += 1
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.pos += 1
                continue

            # Multi-line string
            if ch == '"' and self.source[self.pos:self.pos+3] == '"""':
                self.pos += 3
                start_line = self.line
                start_pos = self.pos
                while self.pos < len(self.source):
                    if self.source[self.pos:self.pos+3] == '"""':
                        self.pos += 3
                        content = self.source[start_pos:self.pos-3]
                        self.tokens.append(Token('STRING', content, start_line))
                        break
                    if self.source[self.pos] == '\n':
                        self.line += 1
                    self.pos += 1
                continue

            # Single-line string
            if ch == '"':
                self.pos += 1
                start_pos = self.pos
                while self.pos < len(self.source) and self.source[self.pos] != '"':
                    if self.source[self.pos] == '\n':
                        self.line += 1
                    self.pos += 1
                if self.pos >= len(self.source):
                    raise SyntaxError("Unterminated string")
                content = self.source[start_pos:self.pos]
                self.pos += 1
                self.tokens.append(Token('STRING', content, self.line))
                continue

            # Assignment <-
            if ch == '<' and self.source[self.pos:self.pos+2] == '<-':
                self.tokens.append(Token('ASSIGN', '<-', self.line))
                self.pos += 2; continue

            # Integer division //
            if ch == '/' and self.source[self.pos:self.pos+2] == '//':
                self.tokens.append(Token('OP', '//', self.line))
                self.pos += 2; continue

            # Multi-char comparison operators
            if ch == '<' and self.source[self.pos:self.pos+2] == '<=':
                self.tokens.append(Token('OP', '<=', self.line))
                self.pos += 2; continue
            if ch == '>' and self.source[self.pos:self.pos+2] == '>=':
                self.tokens.append(Token('OP', '>=', self.line))
                self.pos += 2; continue
            if ch == '!' and self.source[self.pos:self.pos+2] == '!=':
                self.tokens.append(Token('OP', '!=', self.line))
                self.pos += 2; continue
            if ch == '≠':
                self.tokens.append(Token('OP', '!=', self.line))
                self.pos += 1; continue

            # Exponent ^
            if ch == '^':
                self.tokens.append(Token('OP', '^', self.line))
                self.pos += 1; continue

            # Imaginary literal
            m = re.match(r'^(\d+)i', self.source[self.pos:])
            if m:
                self.tokens.append(Token('IMAG', m.group(1), self.line))
                self.pos += len(m.group(0)); continue

            # Number
            m = re.match(r'^(\d+\.\d+|\d+)', self.source[self.pos:])
            if m:
                self.tokens.append(Token('NUMBER', m.group(1), self.line))
                self.pos += len(m.group(0)); continue

            # Operators / delimiters
            if ch in '+-*/=(){}[],:<>.':
                self.tokens.append(Token('OP', ch, self.line))
                self.pos += 1; continue

            # Identifiers / keywords
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)', self.source[self.pos:])
            if m:
                word = m.group(1)
                keywords = {
                    'fn', 'class', 'if', 'then', 'else', 'elseif', 'end',
                    'while', 'do', 'return', 'null', 'lambda', 'and', 'or',
                    'not', 'true', 'false', 'for', 'in', 'import', 'from', 'as'
                }
                kind = 'KEYWORD' if word in keywords else 'IDENTIFIER'
                self.tokens.append(Token(kind, word, self.line))
                self.pos += len(word); continue

            raise SyntaxError(f"Unexpected char '{ch}' at line {self.line}")

        self.tokens.append(Token('EOF', None, self.line))
        return self.tokens