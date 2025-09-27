import json
import random

from pathlib import Path


LINES_PATH = Path(__file__).resolve().parents[1] / "assets" / "data" / "miku_speech.json"


def load_lines(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)  # returns a list of dicts

def random_line(lines: list[dict]) -> dict:
    return random.choice(lines)

speech_lines = load_lines(LINES_PATH)