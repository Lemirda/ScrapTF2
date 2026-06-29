import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
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


async def main():
    print("=== Проверка авторизации ===")
    login_result, profile_path = await check_and_login()

    if not login_result:
        print("Ошибка авторизации. Работа программы остановлена.")
        return

    print("=== Авторизация успешна, запускаем основной скрипт ===")

    db = RaffleDatabase()

    browser = await uc.start(
        headless=False,
        user_data_dir=profile_path
    )

    print("\n=== Запускаем браузер с локальным профилем ===")
    print(f"Путь к профилю: {profile_path}")

    tab = await browser.get("https://scrap.tf/")
    await asyncio.sleep(5)

    while True:
        stats_before = db.get_stats()
        print("\n=== Новая итерация сканирования ===")
        print(
            f"Статистика перед сканированием: Всего раздач: {stats_before['total']}, Необработанных: {stats_before['unprocessed']}, Обработанных: {stats_before['processed']}")

        print("\nСканируем все раздачи...")
        tab = await browser.get(RAFFLES_URL)
        await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))
        all_new, all_existing = await collect_raffles_from_page(tab, db)
        print(f"С основной страницы: {all_new} новых раздач, {all_existing} существующих")

        print("\nСканируем раздачи, которые скоро закончатся...")
        tab = await browser.get(RAFFLES_ENDING_URL)
        await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))
        ending_new, ending_existing = await collect_raffles_from_page(tab, db)
        print(f"С ending: {ending_new} новых раздач, {ending_existing} существующих")

        total_new = ending_new + all_new
        total_existing = ending_existing + all_existing
        print(f"\nВсего собрано: {total_new} новых раздач, {total_existing} уже существующих")

        stats_after = db.get_stats()

        print("\n--- Начинаем обработку необработанных раздач ---")
        await process_unprocessed_raffles(browser, db)

        stats_final = db.get_stats()
        print("\nИтоговая статистика:")
        print(f"Всего раздач в базе: {stats_final['total']}")
        print(f"Необработанных раздач: {stats_final['unprocessed']}")
        print(f"Обработанных раздач: {stats_final['processed']}")
        print(f"Обработано за этот запуск: {stats_final['processed'] - stats_after['processed']}")

        wait_minutes = random.uniform(WAIT_MINUTES_MIN, WAIT_MINUTES_MAX)
        wait_seconds = int(wait_minutes * 60)
        print(f"Следующая проверка через {wait_minutes:.1f} минут")

        print(f"Ожидаем {wait_minutes:.1f} минут перед следующим сканированием")

        await asyncio.sleep(wait_seconds)


if __name__ == "__main__":
    uc.loop().run_until_complete(main())
