import flet as ft

from screeninfo import Monitor
from typing import List
from ui.styles import transparent_window
from utilities.monitor import get_all_monitors
from utilities.debug import debug_msg


def set_win_pos_bc(monitors: List[Monitor], page: ft.Page):
    """Sets the window's position to the primary monitor's bottom center."""
    if monitors:
        primary = monitors[0] # Gets the primary monitor
        window = page.window
        
        # Sets the window horizontally centered
        window.left = primary.x + (primary.width - window.width) / 2
        
        # Sets the window vertically centered
        window.top = primary.y + primary.height - window.height

async def before_main_app(page: ft.Page, debug: bool = False):
    """Serves as the setup function. Must be called before the `main`."""
    # -------- Before Main App --------
    transparent_window(page, height=260, debug=debug)
    
    # -- Set Window Position --
    monitors = get_all_monitors()
    set_win_pos_bc(monitors, page)
    
    # Attach global page/window handlers before main starts.
    def on_keyboard_event(e: ft.KeyboardEvent):
        # Keep it minimal here, actual logic handled in main
        debug_msg(f"Keyboard event captured: {e.key}", debug=True)

    def on_window_event(e: ft.WindowEvent):
        # Same here, lightweight placeholder
        debug_msg(f"Window event captured: {e.type}", debug=True)
    
    if debug:
        page.on_keyboard_event = on_keyboard_event
    
    page.window.on_event = on_window_event
    page.update()