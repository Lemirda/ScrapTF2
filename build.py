"""Сборка кода в exe файл"""
import os
import shutil
import subprocess
import sys


def cleanup():
    """Очистка временных файлов"""
    if os.path.exists("build"):
        shutil.rmtree("build")

    if os.path.exists("ScrapTF_Raffles.spec"):
        os.remove("ScrapTF_Raffles.spec")


def run_cmd(args):
    print("> " + " ".join(args))
    subprocess.check_call(args)


def ensure_deps():
    """Ensure pip and install dependencies needed for the build."""
    python = sys.executable
    project_dir = os.path.dirname(os.path.abspath(__file__))
    req_path = os.path.join(project_dir, "requirements.txt")
    # Upgrade pip to avoid resolver edge cases on CI
    run_cmd([python, "-m", "pip", "install", "--upgrade", "pip"])
    if os.path.exists(req_path):
        run_cmd([python, "-m", "pip", "install", "-r", req_path])
    else:
        # Minimal fallback set to build on CI even without requirements.txt
        run_cmd([python, "-m", "pip", "install", "pyinstaller", "PyQt6"])


def build_exe():
    """Сборка .exe файла"""
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    if os.path.exists("build"):
        shutil.rmtree("build")

    desktop_app_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), "desktop_app.py")

    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "ScrapTF_Raffles",
        "--icon", "icon.ico",
        "--hidden-import", "PyQt6.QtChart",
        "--collect-all", "PyQt6",
        desktop_app_path
    ]

    run_cmd(pyinstaller_args)


if __name__ == "__main__":
    ensure_deps()
    build_exe()
    cleanup()
