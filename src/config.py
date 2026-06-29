import os
import sys


def get_application_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


BASE_URL = "https://scrap.tf"
RAFFLES_URL = "https://scrap.tf/raffles"
RAFFLES_ENDING_URL = "https://scrap.tf/raffles/ending"

SCAN_DELAY_MIN = 5.0
SCAN_DELAY_MAX = 10.0
WAIT_MINUTES_MIN = 5
WAIT_MINUTES_MAX = 20
LOGIN_TIMEOUT_MINUTES = 5
