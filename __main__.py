"""CLI entry point:
    python -m flame file.flpl      # run a file
    python -m flame < file.flpl    # read from stdin
    python -m flame -c "print(1)"  # run code from argument
    python -m flame                # REPL (when stdin is a TTY)
    python -m flame --echo f.flpl  # run with auto-echo at top level
"""
import sys

from . import run_flame, build_global_env
from .environment import Environment
from .evaluator import Evaluator
from .lexer import Lexer
from .parser import Parser


# ---------- helpers for the REPL ----------
_BLOCK_OPENERS = {'fn', 'class', 'if', 'while', 'for'}
_BLOCK_CLOSERS = {'end'}
_CONTINUERS   = {'else', 'elseif', 'then', 'do', 'in'}


def _incomplete(src):
    """Heuristic: does the source need more lines? Count block keywords."""
    depth = 0
    for line in src.splitlines():
        # strip comments
        code = line.split('#', 1)[0]
        for word in code.replace('(', ' ').replace(')', ' ').split():
            if word in _BLOCK_OPENERS:
                depth += 1
            elif word in _BLOCK_CLOSERS:
                depth -= 1
    return depth > 0


def repl():
    """Interactive FlamePL REPL with self-evaluating expressions."""
    global_env = Environment()
    evaluator = Evaluator(global_env, auto_print=True)
    evaluator.current_file_dir = "."
    build_global_env(evaluator, global_env)

    print("FlamePL REPL — type :help for commands, :quit to exit.")
    buffer = []
    while True:
        prompt = ">>> " if not buffer else "... "
        try:
            line = input(prompt)
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            print("\n(interrupted)")
            buffer = []
            continue

        stripped = line.strip()
        if not buffer:
            if stripped in (':quit', ':exit', ':q'):
                break
            if stripped == ':help':
                print("Commands:")
                print("  :help         Show this help")
                print("  :quit / :q    Exit the REPL")
                print("  :clear        Clear multi-line buffer")
                continue
            if stripped == ':clear':
                buffer = []
                continue
            if stripped == '':
                continue

        buffer.append(line)
        src = '\n'.join(buffer)

        # Try to parse; if incomplete, keep reading
        try:
            tokens = Lexer(src).tokenize()
            tree = Parser(tokens).parse()
        except SyntaxError as e:
            if _incomplete(src):
                continue
            print(f"SyntaxError: {e}", file=sys.stderr)
            buffer = []
            continue

        try:
            evaluator.evaluate_program(tree, global_env)
        except SystemExit:
            raise
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
        buffer = []


# ---------- CLI ----------
def main():
    args = sys.argv[1:]
    auto_print = False

    # strip flags
    positional = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--echo':
            auto_print = True
        elif a == '--repl':
            repl()
            return
        elif a == '-c':
            if i + 1 >= len(args):
                print("Error: -c requires an argument", file=sys.stderr)
                sys.exit(1)
            source = args[i + 1]
            try:
                run_flame(source, "<-c>", auto_print=auto_print)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
            return
        else:
            positional.append(a)
        i += 1

    if positional:
        filename = positional[0]
        try:
            with open(filename, 'r') as f:
                source = f.read()
            run_flame(source, filename, auto_print=auto_print)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # No file: if stdin is a TTY, go interactive; otherwise read piped input.
    if sys.stdin.isatty():
        repl()
    else:
        source = sys.stdin.read()
        if not source.strip():
            print("FlamePL Interpreter — usage:", file=sys.stderr)
            print("  python -m flame <file.flpl>     run a file", file=sys.stderr)
            print("  python -m flame < file.flpl     read from stdin", file=sys.stderr)
            print("  python -m flame -c 'code'       run code from argument", file=sys.stderr)
            print("  python -m flame                 start the REPL", file=sys.stderr)
            sys.exit(0)
        run_flame(source, "<stdin>", auto_print=auto_print)


if __name__ == "__main__":
    main()