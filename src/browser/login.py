import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import get_application_path


def get_profile_path():
    profile_dir = os.path.join(get_application_path(), "browser_profile")
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
    return profile_dir
