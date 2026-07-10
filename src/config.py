import os
import sys


def get_application_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(relative):
    # Bundled files (e.g. icon.ico added via PyInstaller --add-data) are unpacked
    # into the temp dir _MEIPASS when frozen; use the project root from source.
    base = getattr(sys, '_MEIPASS', None)
    if base is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)
