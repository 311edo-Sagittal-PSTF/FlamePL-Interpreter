"""FlamePL programming language — public entry point."""
import os
from .environment import Environment
from .lexer import Lexer
from .parser import Parser
from .evaluator import Evaluator


def build_global_env(evaluator, global_env):
    """Install built-in callables into the global environment."""

    def print_fn(*args):
        print(' '.join(str(a) for a in args))

    def input_fn(prompt):
        return input(str(prompt))

    # ---- self-executing commands ----
    def eval_fn(expr_str):
        return evaluator.eval_string(str(expr_str), global_env, as_expression=True)

    def exec_fn(prog_str):
        return evaluator.eval_string(str(prog_str), global_env, as_expression=False)

    def eval_file_fn(path):
        with open(str(path), 'r') as f:
            return evaluator.eval_string(f.read(), global_env, as_expression=False)

    def run_file_fn(path):
        """Execute a file as a fresh program (same global env)."""
        with open(str(path), 'r') as f:
            return evaluator.eval_string(f.read(), global_env, as_expression=False)

    global_env.define('print', print_fn)
    global_env.define('input', input_fn)
    global_env.define('eval', eval_fn)
    global_env.define('exec', exec_fn)
    global_env.define('eval_file', eval_file_fn)
    global_env.define('run_file', run_file_fn)


def run_flame(source, filename="<stdin>", auto_print=False):
    base_dir = (
        os.path.dirname(os.path.abspath(filename))
        if filename != "<stdin>" else os.getcwd()
    )

    tokens = Lexer(source).tokenize()
    tree = Parser(tokens).parse()

    global_env = Environment()
    evaluator = Evaluator(global_env, auto_print=auto_print)
    evaluator.current_file_dir = base_dir
    build_global_env(evaluator, global_env)
    evaluator.evaluate_program(tree, global_env)