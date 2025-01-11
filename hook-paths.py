
import os
import sys

def get_app_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.abspath(".")

os.environ["ABE_ROOT"] = get_app_path()
