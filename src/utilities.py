import flet as ft

import screeninfo
import random
import json
import asyncio

from typing import Optional
from pathlib import Path


LINES_PATH = Path(__file__).resolve().parent / "assets" / "data" / "miku_speech.json"


# -------- Monitor Functions --------
def get_all_monitors():
    try:
        return screeninfo.get_monitors()
    except Exception as e:
        print("Error detecting monitors:", e)
        return []
    
def get_monitor_for_window(left: float, top: float, width: float, height: float) -> Optional[screeninfo.Monitor]:
    """Return the monitor where the window is located (largest overlap)."""
    monitors = get_all_monitors()
    if not monitors:
        return None

    best_monitor = None
    best_area = 0
    win_rect = (left, top, left + width, top + height)

    for m in monitors:
        mon_rect = (m.x, m.y, m.x + m.width, m.y + m.height)

        # compute intersection
        ix1 = max(win_rect[0], mon_rect[0])
        iy1 = max(win_rect[1], mon_rect[1])
        ix2 = min(win_rect[2], mon_rect[2])
        iy2 = min(win_rect[3], mon_rect[3])

        if ix1 < ix2 and iy1 < iy2:  # overlap exists
            area = (ix2 - ix1) * (iy2 - iy1)
            if area > best_area:
                best_area = area
                best_monitor = m

    return best_monitor

def clamp_to_monitor(m: screeninfo.Monitor, left: float, top: float, width: float, height: float):
    """Clamp window inside given monitor."""
    max_left = m.x + m.width - width
    max_top = m.y + m.height - height
    clamped_left = max(m.x, min(left, max_left))
    clamped_top = max(m.y, min(top, max_top))
    return int(clamped_left), int(clamped_top)

def check_and_adjust_bounds(page: ft.Page):
    window: ft.Window = page.window
    
    m = get_monitor_for_window(
        window.left, window.top, window.width, window.height
    )
    if not m:
        return

    clamped_left, clamped_top = clamp_to_monitor(
        m, window.left, window.top, window.width, window.height
    )
    if clamped_left != window.left or clamped_top != window.top:
        window.left, window.top = clamped_left, clamped_top
        window.update()


# -------- Data Loaders --------
def load_lines(file_path: str) -> list[dict]:
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)  # returns a list of dicts

def random_line(lines: list[dict]) -> dict:
    return random.choice(lines)

speech_lines = load_lines(LINES_PATH)


# -------- Debug Stuff --------
def debug_msg(msg: str, handler: str = "DEBUG", debug: bool = False):
    if debug:
        print(f"[{handler}] {msg}")
        
        
# -------- Task Helpers --------
def cancel_task(task: asyncio.Task | None):
    if task and not task.done():
        task.cancel()

async def await_task_completion(task: asyncio.Task | None):
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass