import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import asyncio
import nodriver as uc
from config import get_application_path, LOGIN_TIMEOUT_MINUTES


async def check_and_login():
    browser_profile_dir = os.path.join(get_application_path(), "browser_profile")
    
    if os.path.exists(browser_profile_dir):
        return True, browser_profile_dir

    os.makedirs(browser_profile_dir)

    login_successful = await perform_login(browser_profile_dir)
    return login_successful, browser_profile_dir


async def perform_login(profile_dir):
    print("\n=== AUTHORIZATION REQUIRED ===")
    print("A browser window will open. Please log in to your Steam account on scrap.tf")
    print(f"You have {LOGIN_TIMEOUT_MINUTES} minutes to authorize.")

    browser = await uc.start(
        headless=False,
        user_data_dir=profile_dir,
        no_sandbox=True
    )

    await browser.get("https://scrap.tf/")

    print(f"\nWaiting for authorization: {LOGIN_TIMEOUT_MINUTES} minutes")
    for i in range(LOGIN_TIMEOUT_MINUTES, 0, -1):
        print(f"Time remaining: {i} minutes...")
        await asyncio.sleep(60)

    print("\n=== Authorization time expired ===")
    print("Hope you managed to log in.")
    print("Browser will be closed. Profile saved.")

    browser.stop()
    return True
