import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import asyncio
import nodriver as uc

from browser.login import check_and_login
from browser.scraper import collect_raffles_from_page, process_unprocessed_raffles
from db.manager import RaffleDatabase
from config import (
    SCAN_DELAY_MIN, SCAN_DELAY_MAX,
    WAIT_MINUTES_MIN, WAIT_MINUTES_MAX
)


async def run_scanner():
    login_result, profile_path = await check_and_login()

    if not login_result:
        print("Authorization failed. Stopping.")
        return

    db = RaffleDatabase()

    browser = await uc.start(
        headless=False,
        user_data_dir=profile_path,
        no_sandbox=True
    )

    tab = await browser.get("https://scrap.tf/")
    await asyncio.sleep(5)

    while True:
        stats_before = db.get_stats()
        print(f"Stats: Total: {stats_before['total']}, Unprocessed: {stats_before['unprocessed']}, Processed: {stats_before['processed']}")

        tab = await browser.get("https://scrap.tf/raffles")
        await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))
        all_new, all_existing = await collect_raffles_from_page(tab, db)
        print(f"Main page: {all_new} new, {all_existing} existing")

        tab = await browser.get("https://scrap.tf/raffles/ending")
        await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))
        ending_new, ending_existing = await collect_raffles_from_page(tab, db)
        print(f"Ending page: {ending_new} new, {ending_existing} existing")

        total_new = ending_new + all_new
        total_existing = ending_existing + all_existing
        print(f"Total: {total_new} new, {total_existing} existing")

        stats_after = db.get_stats()

        await process_unprocessed_raffles(browser, db)

        stats_final = db.get_stats()
        print(f"Result: {stats_final['total']} in DB, {stats_final['unprocessed']} pending, {stats_final['processed']} processed")

        wait_minutes = random.uniform(WAIT_MINUTES_MIN, WAIT_MINUTES_MAX)
        wait_seconds = int(wait_minutes * 60)
        print(f"Next scan in {wait_minutes:.1f} minutes")

        await asyncio.sleep(wait_seconds)
