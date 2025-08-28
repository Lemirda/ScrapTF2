import random
import asyncio
import nodriver as uc
import login

from db_manager import RaffleDatabase


async def collect_raffles_from_page(tab, db):
    """Собирает раздачи с текущей страницы"""
    await tab.wait_for('#raffles-list', timeout=30)
    await asyncio.sleep(random.uniform(5.0, 10.0))

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
            link = f"https://scrap.tf{link}"

        if not db.is_raffle_exists(link):
            if db.add_raffle(link):
                new_raffles += 1
        else:
            existing_raffles += 1

    return new_raffles, existing_raffles


async def main():
    print("=== Проверка авторизации ===")
    login_result, profile_path = await login.check_and_login()

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

        # Собираем раздачи с /raffles
        print("\nСканируем все раздачи...")
        tab = await browser.get("https://scrap.tf/raffles")
        await asyncio.sleep(random.uniform(5.0, 10.0))
        all_new, all_existing = await collect_raffles_from_page(tab, db)
        print(
            f"С основной страницы: {all_new} новых раздач, {all_existing} существующих")

        # Собираем раздачи с /raffles/ending
        print("\nСканируем раздачи, которые скоро закончатся...")
        tab = await browser.get("https://scrap.tf/raffles/ending")
        await asyncio.sleep(random.uniform(5.0, 10.0))
        ending_new, ending_existing = await collect_raffles_from_page(tab, db)
        print(
            f"С ending: {ending_new} новых раздач, {ending_existing} существующих")

        total_new = ending_new + all_new
        total_existing = ending_existing + all_existing
        print(
            f"\nВсего собрано: {total_new} новых раздач, {total_existing} уже существующих")

        stats_after = db.get_stats()

        print("\n--- Начинаем обработку необработанных раздач ---")
        await process_unprocessed_raffles(browser, db)

        stats_final = db.get_stats()
        print("\nИтоговая статистика:")
        print(f"Всего раздач в базе: {stats_final['total']}")
        print(f"Необработанных раздач: {stats_final['unprocessed']}")
        print(f"Обработанных раздач: {stats_final['processed']}")
        print(
            f"Обработано за этот запуск: {stats_final['processed'] - stats_after['processed']}")

        wait_minutes = random.uniform(5, 20)
        wait_seconds = int(wait_minutes * 60)
        print(f"Следующая проверка через {wait_minutes:.1f} минут")

        print(
            f"Ожидаем {wait_minutes:.1f} минут перед следующим сканированием")

        await asyncio.sleep(wait_seconds)


async def process_unprocessed_raffles(browser, db):
    unprocessed_raffles = db.get_unprocessed_raffles()

    if not unprocessed_raffles:
        print("Нет необработанных раздач для участия.")
        return

    print(
        f"Найдено {len(unprocessed_raffles)} необработанных раздач для участия.")

    processed_count = 0
    failed_count = 0

    for raffle in unprocessed_raffles:
        url = raffle['url']
        print(f"\nПереход по ссылке: {url}")

        tab = await browser.get(url)
        await asyncio.sleep(random.uniform(5.0, 10.0))

        try:
            await tab.wait_for('.raffle-row-full-width', timeout=5)

            print("Раздача уже закончилась. Удаляем из базы данных.")
            db.delete_raffle(url)
            continue
        except Exception:
            pass

        try:
            # Пробуем вступить в раздачу
            enter_button = await tab.wait_for('button.btn-info.btn-lg[onclick*="EnterRaffle"]:not([id="raffle-enter"])', timeout=5)
            print("Найдена кнопка 'Enter Raffle'. Нажимаем...")
            await enter_button.click()
            await asyncio.sleep(random.uniform(5.0, 10.0))
        except Exception:
            print("Не удалось найти кнопку Enter Raffle")

        try:
            # Проверяем успешность вступления
            await tab.wait_for('button.btn-danger.btn-lg[onclick*="LeaveRaffle"]', timeout=40)
            print("Успешно вступили в раздачу!")
            db.mark_as_processed(url)
            processed_count += 1
        except Exception:
            print("Не удалось найти кнопку LeaveRaffle")
            failed_count += 1

        await asyncio.sleep(random.uniform(3.0, 5.0))

    print(
        f"\nОбработка раздач завершена: успешно обработано {processed_count}, не удалось обработать {failed_count}")

if __name__ == "__main__":
    uc.loop().run_until_complete(main())
