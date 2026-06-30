import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import asyncio
import nodriver as uc

from browser.login import get_profile_path
from browser.scraper import collect_raffles_from_page, process_unprocessed_raffles
from db.manager import RaffleDatabase


async def run_scanner(worker=None):
    db = RaffleDatabase()
    profile_path = get_profile_path()

    scan_delay_min = int(db.get_setting('scan_delay_min'))
    scan_delay_max = int(db.get_setting('scan_delay_max'))
    wait_minutes_min = int(db.get_setting('wait_minutes_min'))
    wait_minutes_max = int(db.get_setting('wait_minutes_max'))

    browser = await uc.start(
        headless=False,
        user_data_dir=profile_path,
        no_sandbox=True
    )

    tab = await browser.get("https://scrap.tf/")
    await asyncio.sleep(5)

    while True:
        if worker:
            worker.status_changed.emit({'state': 'scanning'})

        tab = await browser.get("https://scrap.tf/raffles")
        await asyncio.sleep(random.uniform(scan_delay_min, scan_delay_max))
        await collect_raffles_from_page(tab, db)

        tab = await browser.get("https://scrap.tf/raffles/ending")
        await asyncio.sleep(random.uniform(scan_delay_min, scan_delay_max))
        await collect_raffles_from_page(tab, db)

        if worker:
            worker.status_changed.emit({'state': 'processing'})

        await process_unprocessed_raffles(browser, db, worker)

        wait_minutes = random.uniform(wait_minutes_min, wait_minutes_max)
        wait_seconds = int(wait_minutes * 60)
        await asyncio.sleep(wait_seconds)
