import json, random

from pathlib import Path
from datetime import datetime
from enum import Enum


# ----- File Manipulation -----
LINES_PATH = Path(__file__).resolve().parents[1] / "assets" / "data" / "miku_speech.json"

def load_lines(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)  # returns a list of dicts

def random_line(lines: list[dict]) -> dict:
    """Chooses a random entry from the list of dicts."""
    return random.choice(lines)

SPEECH_LINES = load_lines(LINES_PATH)


# ----- Time Stuff -----
class TimePeriod(Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"

def get_day_period(return_str: bool = True) -> TimePeriod | str:
    """
    Returns a `TimePeriod` based on local system time. Set `return_str` to `True` for a lowercase str.
    """
    hour = datetime.now().hour
    def str_or_enum(period: TimePeriod):
        nonlocal return_str
        return period.value.lower() if return_str else TimePeriod.value
    
    if 5 <= hour < 12:
        return str_or_enum(TimePeriod.MORNING)
    elif 12 <= hour < 18:
        return str_or_enum(TimePeriod.AFTERNOON)
    else:
        return str_or_enum(TimePeriod.EVENING)