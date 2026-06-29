import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import asyncio
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from db.manager import RaffleDatabase
from browser.scanner import run_scanner


class ConsoleOutput(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        if text.strip():
            self.text_written.emit(text.strip())

    def flush(self):
        pass


class MainWorker(QThread):
    status_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        self.status_changed.emit("running")
        asyncio.run(run_scanner())
        self.status_changed.emit("stopped")

    def stop(self):
        self.running = False
        self.terminate()
        self.wait()


class RaffleStatsWorker(QThread):
    stats_updated = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        while self.running:
            db = RaffleDatabase()
            stats = db.get_stats()
            db.close()
            self.stats_updated.emit(stats)
            time.sleep(5)

    def stop(self):
        self.running = False
        self.terminate()
        self.wait()
