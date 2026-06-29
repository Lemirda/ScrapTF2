import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import nodriver as uc
from config import get_application_path, LOGIN_TIMEOUT_MINUTES


async def check_and_login():
    browser_profile_dir = os.path.join(get_application_path(), "browser_profile")
    
    if os.path.exists(browser_profile_dir):
        print("\n=== Папка профиля браузера уже существует ===")
        print(f"Путь к профилю: {browser_profile_dir}")
        return True, browser_profile_dir

    os.makedirs(browser_profile_dir)
    print(f"\n=== Создана директория для профиля браузера: {browser_profile_dir} ===")

    login_successful = await perform_login(browser_profile_dir)
    return login_successful, browser_profile_dir


async def perform_login(profile_dir):
    print("\n=== ТРЕБУЕТСЯ АВТОРИЗАЦИЯ ===")
    print("Сейчас откроется браузер. Вам необходимо войти в аккаунт Steam на сайте scrap.tf")
    print(f"У вас есть {LOGIN_TIMEOUT_MINUTES} минут для авторизации.")

    browser = await uc.start(
        headless=False,
        user_data_dir=profile_dir
    )

    await browser.get("https://scrap.tf/")

    print(f"\nОжидание авторизации: {LOGIN_TIMEOUT_MINUTES} минут")
    for i in range(LOGIN_TIMEOUT_MINUTES, 0, -1):
        print(f"Осталось времени: {i} минут...")
        await asyncio.sleep(60)

    print("\n=== Время на авторизацию истекло ===")
    print("Надеемся, вы успели войти в аккаунт.")
    print("Браузер будет закрыт. Профиль сохранен.")

    browser.stop()
    return True
