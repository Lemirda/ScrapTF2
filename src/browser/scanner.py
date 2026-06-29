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
    RAFFLES_URL, RAFFLES_ENDING_URL,
    SCAN_DELAY_MIN, SCAN_DELAY_MAX,
    WAIT_MINUTES_MIN, WAIT_MINUTES_MAX
)


async def run_scanner():
    login_result, profile_path = await check_and_login()

    if not login_result:
        print("Ошибка авторизации. Работа программы остановлена.")
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
        print(f"Статистика: Всего: {stats_before['total']}, Необработанных: {stats_before['unprocessed']}, Обработанных: {stats_before['processed']}")

        tab = await browser.get(RAFFLES_URL)
        await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))
        all_new, all_existing = await collect_raffles_from_page(tab, db)
        print(f"С основной страницы: {all_new} новых, {all_existing} существующих")

        tab = await browser.get(RAFFLES_ENDING_URL)
        await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))
        ending_new, ending_existing = await collect_raffles_from_page(tab, db)
        print(f"С ending: {ending_new} новых, {ending_existing} существующих")

        total_new = ending_new + all_new
        total_existing = ending_existing + all_existing
        print(f"Всего: {total_new} новых, {total_existing} существующих")

        stats_after = db.get_stats()

        await process_unprocessed_raffles(browser, db)

        stats_final = db.get_stats()
        print(f"Итого: {stats_final['total']} в базе, {stats_final['unprocessed']} ожидают, {stats_final['processed']} обработано")

        wait_minutes = random.uniform(WAIT_MINUTES_MIN, WAIT_MINUTES_MAX)
        wait_seconds = int(wait_minutes * 60)
        print(f"Следующая проверка через {wait_minutes:.1f} минут")

        await asyncio.sleep(wait_seconds)
