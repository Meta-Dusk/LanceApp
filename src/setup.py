import flet as ft

from styles import transparent_window
from utilities import get_all_monitors, debug_msg


def before_main_app(page: ft.Page, debug: bool = False):
    # -------- Before Main App --------
    transparent_window(page, height=260, debug=debug)
    
    # Window position
    monitors = get_all_monitors()
    if monitors:
        primary = monitors[0]
        page.window.left = primary.x + (primary.width - page.window.width) / 2
        page.window.top = primary.y + primary.height - page.window.height
    
    # Attach global page/window handlers before main starts.
    def on_keyboard_event(e: ft.KeyboardEvent):
        # Keep it minimal here, actual logic handled in main
        debug_msg(f"Keyboard event captured: {e.key}", debug=True)

    def on_window_event(e: ft.WindowEvent):
        # Same here, lightweight placeholder
        debug_msg(f"Window event captured: {e.type}", debug=True)

    page.on_keyboard_event = on_keyboard_event
    page.window.on_event = on_window_event
    page.update()