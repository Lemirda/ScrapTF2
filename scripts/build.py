import os
import shutil
import subprocess
import sys


def cleanup():
    if os.path.exists("build"):
        shutil.rmtree("build")

    if os.path.exists("ScrapTF2.spec"):
        os.remove("ScrapTF2.spec")


def run_cmd(args):
    print("> " + " ".join(args))
    subprocess.check_call(args)


def ensure_deps():
    python = sys.executable
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    req_path = os.path.join(project_dir, "requirements.txt")
    run_cmd([python, "-m", "pip", "install", "--upgrade", "pip"])
    if os.path.exists(req_path):
        run_cmd([python, "-m", "pip", "install", "-r", req_path])
    else:
        run_cmd([python, "-m", "pip", "install", "pyinstaller", "PyQt6"])


def build_exe():
    if os.path.exists("dist"):
        shutil.rmtree("dist")

    if os.path.exists("build"):
        shutil.rmtree("build")

    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_path = os.path.join(project_dir, "main.py")

    pyinstaller_args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "ScrapTF2",
        "--icon", os.path.join(project_dir, "icon.ico"),
        "--add-data", os.path.join(project_dir, "icon.ico") + os.pathsep + ".",
        "--hidden-import", "PyQt6.QtChart",
        "--hidden-import", "ui",
        "--hidden-import", "ui.styles",
        "--hidden-import", "ui.workers",
        "--hidden-import", "ui.i18n",
        "--hidden-import", "ui.app",
        "--hidden-import", "browser",
        "--hidden-import", "browser.login",
        "--hidden-import", "browser.scanner",
        "--hidden-import", "browser.scraper",
        "--hidden-import", "db",
        "--hidden-import", "db.manager",
        "--hidden-import", "config",
        "--collect-all", "PyQt6",
        "--paths", project_dir,
        "--paths", os.path.join(project_dir, "src"),
        main_path
    ]

    run_cmd(pyinstaller_args)


if __name__ == "__main__":
    ensure_deps()
    build_exe()
    cleanup()
