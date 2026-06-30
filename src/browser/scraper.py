import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import random
import asyncio
from db.manager import RaffleDatabase


async def collect_raffles_from_page(tab, db):
    scan_delay_min = int(db.get_setting('scan_delay_min'))
    scan_delay_max = int(db.get_setting('scan_delay_max'))
    
    await tab.wait_for('#raffles-list', timeout=30)
    await asyncio.sleep(random.uniform(scan_delay_min, scan_delay_max))

    raffle_links = await tab.evaluate('''
        Array.from(document.querySelectorAll('.panel-raffle .panel-heading a'))
            .map(a => a.href)
            .filter(href => href && href.includes('/raffles/'));
    ''')

    if not raffle_links:
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


async def process_unprocessed_raffles(browser, db, worker=None):
    scan_delay_min = int(db.get_setting('scan_delay_min'))
    scan_delay_max = int(db.get_setting('scan_delay_max'))
    
    unprocessed_raffles = db.get_unprocessed_raffles()

    if not unprocessed_raffles:
        return

    total_count = len(unprocessed_raffles)
    processed_count = 0
    failed_count = 0

    for idx, raffle in enumerate(unprocessed_raffles, 1):
        url = raffle['url']
        
        if worker:
            worker.status_changed.emit({
                'state': 'processing',
                'current': idx,
                'total': total_count,
                'processed': processed_count,
                'failed': failed_count
            })

        tab = await browser.get(url)
        await asyncio.sleep(random.uniform(scan_delay_min, scan_delay_max))

        try:
            await tab.wait_for('.raffle-row-full-width', timeout=5)
            db.delete_raffle(url)
            continue
        except Exception:
            pass

        try:
            enter_button = await tab.wait_for('button.btn-info.btn-lg[onclick*="EnterRaffle"]:not([id="raffle-enter"])', timeout=5)
            await enter_button.click()
            await asyncio.sleep(random.uniform(scan_delay_min, scan_delay_max))
        except Exception:
            pass

        try:
            await tab.wait_for('button.btn-danger.btn-lg[onclick*="LeaveRaffle"]', timeout=40)
            db.mark_as_processed(url)
            processed_count += 1
        except Exception:
            failed_count += 1

        await asyncio.sleep(random.uniform(3.0, 5.0))
