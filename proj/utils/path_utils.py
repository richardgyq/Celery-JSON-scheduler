import os
import sys
from pathlib import Path


class pathcontext:
    def __init__(self, filename):
        self.filename = filename
        self.path = os.path.dirname(filename)
        self.inserted = []

    def __enter__(self):
        self.add_path_to_sys_path()

    def __exit__(self, *args):
        pass

    def getfullpath(self, filename):
        result = os.path.normpath(os.path.join(self.path, filename))
        return result

    def add_path_to_sys_path(self):
        if self.path not in sys.path:
            sys.path.insert(0, self.path)


def get_module_fullname(module_name):
    if module_name is None:
        return None
    if '.' in module_name:
        return module_name
    rootdir = os.path.abspath('')
    for dir, subdir, files in os.walk(rootdir):
        if module_name + '.py' in files:
            no_root_path = dir[len(rootdir) + 1:]
            path = Path(no_root_path)
            return '.'.join(path.parts) + '.' + module_name
    return None
