import flet as ft
import time

from src.styles import transparent_window
from src.images import DynamicMiku, Miku
from src.utilities import get_all_monitors, check_and_adjust_bounds


def test(page: ft.Page):
    # ------- Setup -------
    DEBUG = True
    transparent_window(page, debug=DEBUG)

    # Place window on primary monitor bottom center
    monitors = get_all_monitors()
    if monitors:
        primary = monitors[0]
        page.window.left = primary.x + (primary.width - page.window.width) / 2
        page.window.top = primary.y + primary.height - page.window.height

    # ------- Event Handlers -------
    def movement(e: ft.KeyboardEvent):
        step = 20
        if e.key == "D":
            main_miku.set_flipped(False)
            page.window.left += step
        elif e.key == "A":
            main_miku.set_flipped(True)
            page.window.left -= step

        check_and_adjust_bounds(page)
        page.update()

    def on_event(e: ft.WindowEvent):
        if e.type == ft.WindowEventType.MOVED:
            main_miku.set_state(Miku.NEUTRAL)
            main_miku.set_pan_start(False)
        elif e.type == ft.WindowEventType.BLUR:
            main_miku.set_state(Miku.AMGRY)
        elif e.type == ft.WindowEventType.FOCUS:
            main_miku.set_state(Miku.HAPPY)
        check_and_adjust_bounds(page)

    def on_pan_start(_):
        main_miku.set_pan_start(True)
        main_miku.set_state(Miku.ECSTATIC)

    def on_enter(_):
        main_miku.set_state(Miku.READY)

    def on_exit(_):
        if not main_miku.is_pan_start():
            main_miku.set_state(Miku.NEUTRAL)

    def on_tap(_):
        main_miku.set_state(Miku.PONDER)

    def on_double_tap(_):
        if DEBUG:
            print("[Miku] Bye bye...")
            
        exit_miku_img.opacity = 1
        main_miku_img.visible = False
        page.update()
        exit_miku_img.scale = 0
        exit_miku_img.rotate = ft.Rotate(-1)
        page.update()
        time.sleep(1)
        page.window.close()
    
    def on_secondary_tap(_):
        main_miku.set_state(Miku.THINKING)
    
    def on_long_press_start(_):
        main_miku.set_state(Miku.SHOCK)
    
    def on_long_press_end(_):
        main_miku.set_state(Miku.AMGRY)
    
    # Create Miku wrappers
    main_miku = DynamicMiku(Miku.NEUTRAL, debug=DEBUG)
    main_miku_img = main_miku.get_image()

    exit_miku = DynamicMiku(Miku.AMGRY, debug=DEBUG)
    exit_miku_img = exit_miku.get_image()
    exit_miku_img.animate_scale = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    exit_miku_img.animate_rotation = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    exit_miku_img.opacity = 0

    # Stack them
    miku_stack = ft.Stack(controls=[exit_miku_img, main_miku_img], alignment=ft.alignment.center)

    miku_gs = ft.GestureDetector(
        content=miku_stack,
        mouse_cursor=ft.MouseCursor.MOVE,
        on_double_tap=on_double_tap,
        on_enter=on_enter,
        on_exit=on_exit,
        on_tap=on_tap,
        on_long_press_start=on_long_press_start,
        on_long_press_end=on_long_press_end,
        on_secondary_tap=on_secondary_tap
    )
    form = ft.WindowDragArea(content=miku_gs, maximizable=False, on_pan_start=on_pan_start)

    page.window.on_event = on_event
    page.on_keyboard_event = movement
    page.add(form)
    check_and_adjust_bounds(page)
    page.update()


if __name__ == "__main__":
    ft.app(target=test)
