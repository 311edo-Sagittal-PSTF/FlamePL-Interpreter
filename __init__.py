"""FlamePL programming language — public entry point."""
import os
from .environment import Environment
from .lexer import Lexer
from .parser import Parser
from .evaluator import Evaluator


def run_flame(source, filename="<stdin>"):
    base_dir = (
        os.path.dirname(os.path.abspath(filename))
        if filename != "<stdin>" else os.getcwd()
    )

    tokens = Lexer(source).tokenize()
    tree = Parser(tokens).parse()

    global_env = Environment()

    def print_fn(*args):
        print(' '.join(str(a) for a in args))
    def input_fn(prompt):
        return input(str(prompt))

    global_env.define('print', print_fn)
    global_env.define('input', input_fn)

    evaluator = Evaluator(global_env)
    evaluator.current_file_dir = base_dir
    evaluator.evaluate_block(tree, global_env)