import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import asyncio
from config import BASE_URL, SCAN_DELAY_MIN, SCAN_DELAY_MAX


async def collect_raffles_from_page(tab, db):
    await tab.wait_for('#raffles-list', timeout=30)
    await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))

    raffle_links = await tab.evaluate('''
        Array.from(document.querySelectorAll('.panel-raffle .panel-heading a'))
            .map(a => a.href)
            .filter(href => href && href.includes('/raffles/'));
    ''')

    if not raffle_links:
        print("Не удалось найти ни одной ссылки на раздачу!")
        return 0, 0

    new_raffles = 0
    existing_raffles = 0

    for link in raffle_links:
        if isinstance(link, dict) and 'value' in link:
            link = link['value']

        if not link.startswith('https://scrap.tf'):
            link = f"{BASE_URL}{link}"

        if not db.is_raffle_exists(link):
            if db.add_raffle(link):
                new_raffles += 1
        else:
            existing_raffles += 1

    return new_raffles, existing_raffles


async def process_unprocessed_raffles(browser, db):
    unprocessed_raffles = db.get_unprocessed_raffles()

    if not unprocessed_raffles:
        print("Нет необработанных раздач для участия.")
        return

    print(f"Найдено {len(unprocessed_raffles)} необработанных раздач для участия.")

    processed_count = 0
    failed_count = 0

    for raffle in unprocessed_raffles:
        url = raffle['url']
        print(f"\nПереход по ссылке: {url}")

        tab = await browser.get(url)
        await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))

        try:
            await tab.wait_for('.raffle-row-full-width', timeout=5)
            print("Раздача уже закончилась. Удаляем из базы данных.")
            db.delete_raffle(url)
            continue
        except Exception:
            pass

        try:
            enter_button = await tab.wait_for('button.btn-info.btn-lg[onclick*="EnterRaffle"]:not([id="raffle-enter"])', timeout=5)
            print("Найдена кнопка 'Enter Raffle'. Нажимаем...")
            await enter_button.click()
            await asyncio.sleep(random.uniform(SCAN_DELAY_MIN, SCAN_DELAY_MAX))
        except Exception:
            print("Не удалось найти кнопку Enter Raffle")

        try:
            await tab.wait_for('button.btn-danger.btn-lg[onclick*="LeaveRaffle"]', timeout=40)
            print("Успешно вступили в раздачу!")
            db.mark_as_processed(url)
            processed_count += 1
        except Exception:
            print("Не удалось найти кнопку LeaveRaffle")
            failed_count += 1

        await asyncio.sleep(random.uniform(3.0, 5.0))

    print(f"\nОбработка раздач завершена: успешно обработано {processed_count}, не удалось обработать {failed_count}")
