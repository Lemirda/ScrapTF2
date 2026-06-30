import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from db.manager import RaffleDatabase
from browser.scanner import run_scanner_with_browser


class AppWorker(QThread):
    browser_ready = pyqtSignal()
    login_required = pyqtSignal()
    status_changed = pyqtSignal(dict)

    def __init__(self, profile_path, db, parent=None):
        super().__init__(parent)
        self.profile_path = profile_path
        self.db = db
        self.running = True
        self._logged_in = False
        self._should_relogin = False
        self.browser = None

    def run(self):
        asyncio.run(self._main())

    async def _main(self):
        import nodriver as uc
        db = RaffleDatabase()

        while self.running:
            self._should_relogin = False
            self._logged_in = False

            browser = await uc.start(
                headless=False,
                user_data_dir=self.profile_path,
                no_sandbox=True
            )
            self.browser = browser

            try:
                await browser.get("https://scrap.tf/")
                for _ in range(6):
                    if not self.running or self._should_relogin:
                        break
                    await asyncio.sleep(0.5)
                self.browser_ready.emit()

                logged_in = db.get_setting('logged_in')
                if logged_in != '1':
                    self.login_required.emit()
                    while not self._logged_in and self.running and not self._should_relogin:
                        await asyncio.sleep(0.3)

                if not self.running or self._should_relogin:
                    continue

                await run_scanner_with_browser(browser, db, self)
            finally:
                if browser:
                    browser.stop()
                    self.browser = None

            if self._should_relogin:
                profile_path = self.profile_path
                import shutil
                if os.path.exists(profile_path):
                    shutil.rmtree(profile_path, ignore_errors=True)
                os.makedirs(profile_path, exist_ok=True)
                db.set_setting('logged_in', '0')

    def login_done(self):
        self._logged_in = True
        self.db.set_setting('logged_in', '1')

    def relogin(self):
        self._should_relogin = True
        self._logged_in = True

    def stop(self):
        self.running = False
        self._logged_in = True
        self.wait(5000)
        if self.isRunning():
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
