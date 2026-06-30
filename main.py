import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
from PyQt6.QtWidgets import QApplication
from ui.app import ScrapTF2App


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScrapTF2App()
    window.show()
    sys.exit(app.exec())
