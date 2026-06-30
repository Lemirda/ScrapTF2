import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import asyncio

from browser.login import get_profile_path
from browser.scraper import collect_raffles_from_page, process_unprocessed_raffles
from db.manager import RaffleDatabase


async def run_scanner_with_browser(browser, db, worker=None):
    scan_delay_min = int(db.get_setting('scan_delay_min'))
    scan_delay_max = int(db.get_setting('scan_delay_max'))
    wait_minutes_min = int(db.get_setting('wait_minutes_min'))
    wait_minutes_max = int(db.get_setting('wait_minutes_max'))

    tab = await browser.get("https://scrap.tf/")
    for _ in range(10):
        if not worker or not worker.running or worker._should_relogin:
            return
        await asyncio.sleep(0.5)

    while worker and worker.running and not worker._should_relogin:
        worker.status_changed.emit({'state': 'scanning'})

        tab = await browser.get("https://scrap.tf/raffles")
        await _sleep_check(scan_delay_min, scan_delay_max, worker)
        await collect_raffles_from_page(tab, db)

        if not worker.running or worker._should_relogin:
            break

        tab = await browser.get("https://scrap.tf/raffles/ending")
        await _sleep_check(scan_delay_min, scan_delay_max, worker)
        await collect_raffles_from_page(tab, db)

        worker.status_changed.emit({'state': 'processing'})

        await process_unprocessed_raffles(browser, db, worker)

        if not worker.running or worker._should_relogin:
            break

        wait_minutes = random.uniform(wait_minutes_min, wait_minutes_max)
        wait_seconds = int(wait_minutes * 60)
        for _ in range(wait_seconds):
            if not worker.running or worker._should_relogin:
                break
            await asyncio.sleep(1)


async def _sleep_check(min_val, max_val, worker):
    duration = random.uniform(min_val, max_val)
    step = 0.3
    elapsed = 0.0
    while elapsed < duration:
        if worker and (not worker.running or worker._should_relogin):
            break
        await asyncio.sleep(step)
        elapsed += step
