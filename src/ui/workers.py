import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from db.manager import RaffleDatabase
from browser.scanner import run_scanner


class LoginWorker(QThread):
    login_finished = pyqtSignal()

    def __init__(self, profile_dir, parent=None):
        super().__init__(parent)
        self.profile_dir = profile_dir
        self._should_stop = False
        self.browser = None

    def run(self):
        asyncio.run(self._run())

    async def _run(self):
        import nodriver as uc
        self.browser = await uc.start(
            headless=False,
            user_data_dir=self.profile_dir,
            no_sandbox=True
        )
        await self.browser.get("https://scrap.tf/")

        while not self._should_stop:
            await asyncio.sleep(0.5)

        if self.browser:
            self.browser.stop()

        self.login_finished.emit()

    def stop(self):
        self._should_stop = True


class MainWorker(QThread):
    status_changed = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True

    def run(self):
        asyncio.run(run_scanner(self))

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
