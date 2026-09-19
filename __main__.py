"""CLI entry point: python -m flame [file]"""
import sys
from . import run_flame


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        try:
            with open(filename, 'r') as f:
                source = f.read()
            run_flame(source, filename)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        source = sys.stdin.read()
        if not source:
            print("FlamePL Interpreter — usage:", file=sys.stderr)
            print("  python -m flame <filename>   # run a file", file=sys.stderr)
            print("  python -m flame              # read from stdin (pipe/redirect)", file=sys.stderr)
            sys.exit(0)
        run_flame(source, "<stdin>")


if __name__ == "__main__":
    main()