"""Standard I/O library (file operations)."""
import os
from ..environment import Environment


def build(global_env):
    env = Environment(global_env)

    def read_file(path):
        with open(path, 'r') as f:
            return f.read()
    def write_file(path, content):
        with open(path, 'w') as f:
            f.write(str(content))
        return None
    def append_file(path, content):
        with open(path, 'a') as f:
            f.write(str(content))
        return None
    def exists(path): return os.path.exists(path)
    def is_file(path): return os.path.isfile(path)
    def is_dir(path): return os.path.isdir(path)
    def remove_file(path):
        os.remove(path); return None
    def read_lines(path):
        with open(path, 'r') as f:
            return [line.rstrip('\n') for line in f.readlines()]

    env.define("read_file", read_file)
    env.define("write_file", write_file)
    env.define("append_file", append_file)
    env.define("exists", exists)
    env.define("is_file", is_file)
    env.define("is_dir", is_dir)
    env.define("remove_file", remove_file)
    env.define("read_lines", read_lines)
    return env