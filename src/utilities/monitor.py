import flet as ft
import screeninfo

from typing import Optional
from utilities.debug import debug_msg


import flet as ft
import screeninfo
from typing import Optional, Tuple, List
from utilities.debug import debug_msg


def get_all_monitors() -> List[screeninfo.Monitor]:
    """Return a list of monitors detected in the system."""
    try:
        return screeninfo.get_monitors()
    except Exception as e:
        print("Error detecting monitors:", e)
        return []


def get_monitor_for_window(
    left: Optional[float] = None, top: Optional[float] = None,
    width: Optional[float] = None, height: Optional[float] = None,
    page: Optional[ft.Page] = None
) -> Optional[screeninfo.Monitor]:
    """
    Return the monitor where the window is located (largest overlap).
    Accepts explicit window geometry or derives it from a `page`.
    """
    monitors = get_all_monitors()
    if not monitors:
        return None

    if page is None:
        if None in (left, top, width, height):
            raise ValueError("Either provide a page, or all of left, top, width, and height.")
        win_rect = (left, top, left + width, top + height)
    else:
        win = page.window
        win_rect = (win.left, win.top, win.left + win.width, win.top + win.height)

    best_monitor = None
    best_area = 0

    for m in monitors:
        mon_rect = (m.x, m.y, m.x + m.width, m.y + m.height)

        # intersection rectangle
        ix1 = max(win_rect[0], mon_rect[0])
        iy1 = max(win_rect[1], mon_rect[1])
        ix2 = min(win_rect[2], mon_rect[2])
        iy2 = min(win_rect[3], mon_rect[3])

        if ix1 < ix2 and iy1 < iy2:
            area = (ix2 - ix1) * (iy2 - iy1)
            if area > best_area:
                best_area = area
                best_monitor = m

    return best_monitor


def clamp_to_monitor(
    monitor: screeninfo.Monitor, page: Optional[ft.Page] = None,
    left: Optional[float] = None, top: Optional[float] = None,
    width: Optional[float] = None, height: Optional[float] = None
) -> Tuple[int, int]:
    """
    Clamp window inside given monitor.
    Accepts explicit window geometry or derives it from a `page`.
    """
    m = monitor
    if page is None:
        if None in (left, top, width, height):
            raise ValueError("Either provide a page, or all of left, top, width, and height.")
        win_left, win_top, win_width, win_height = left, top, width, height
    else:
        win = page.window
        win_left, win_top, win_width, win_height = win.left, win.top, win.width, win.height

    max_left = m.x + m.width - win_width
    max_top = m.y + m.height - win_height
    clamped_left = max(m.x, min(win_left, max_left))
    clamped_top = max(m.y, min(win_top, max_top))

    return int(clamped_left), int(clamped_top)


def check_and_adjust_bounds(
    page: Optional[ft.Page] = None, debug: bool = False,
    left: Optional[float] = None, top: Optional[float] = None,
    width: Optional[float] = None, height: Optional[float] = None
) -> bool:
    """
    Automatically adjust window within boundaries of the monitor it is in.
    Returns True if a valid monitor was found.
    Accepts explicit window geometry or derives it from a `page`.
    """
    if page is None:
        if None in (left, top, width, height):
            raise ValueError("Either provide a page, or all of left, top, width, and height.")
        win_left, win_top, win_width, win_height = left, top, width, height
    else:
        win = page.window
        win_left, win_top, win_width, win_height = win.left, win.top, win.width, win.height

    monitor = get_monitor_for_window(left=win_left, top=win_top, width=win_width, height=win_height, page=page)
    if not monitor:
        debug_msg("DANGER! NO MONITOR!", debug=debug)
        return False

    clamped_left, clamped_top = clamp_to_monitor(
        monitor=monitor, page=page, left=win_left, top=win_top,
        width=win_width, height=win_height
    )

    if page is not None and (clamped_left != win_left or clamped_top != win_top):
        page.window.left, page.window.top = clamped_left, clamped_top
        page.window.update()

    return True