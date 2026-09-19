"""Standard OS library."""
import os as _os
from ..environment import Environment


def build(global_env):
    env = Environment(global_env)

    def getcwd(): return _os.getcwd()
    def listdir(path="."): return list(_os.listdir(path))
    def mkdir(path): _os.mkdir(path); return None
    def makedirs(path): _os.makedirs(path, exist_ok=True); return None
    def rmdir(path): _os.rmdir(path); return None
    def remove(path): _os.remove(path); return None
    def rename(a, b): _os.rename(a, b); return None
    def exists(path): return _os.path.exists(path)
    def join(*parts): return _os.path.join(*parts)
    def basename(path): return _os.path.basename(path)
    def dirname(path): return _os.path.dirname(path)
    def abspath(path): return _os.path.abspath(path)
    def getenv(key, default=None): return _os.environ.get(key, default)

    env.define("getcwd", getcwd)
    env.define("listdir", listdir)
    env.define("mkdir", mkdir)
    env.define("makedirs", makedirs)
    env.define("rmdir", rmdir)
    env.define("remove", remove)
    env.define("rename", rename)
    env.define("exists", exists)
    env.define("join", join)
    env.define("basename", basename)
    env.define("dirname", dirname)
    env.define("abspath", abspath)
    env.define("getenv", getenv)
    return env