import flet as ft
import time
import threading
import random

from src.styles import transparent_window
from src.images import DynamicMiku, Miku, generate_image, Sprites
from src.utilities import get_all_monitors, check_and_adjust_bounds, random_line, speech_lines


def test(page: ft.Page):
    # ------- Setup -------
    DEBUG = False
    transparent_window(page, debug=DEBUG)
    stop_event = threading.Event()
    restart_timer = None
    speech_timer = None
    speech_bubble = None
    miku_mv_freq_ms = (1000, 1500)

    # Place window on primary monitor bottom center
    monitors = get_all_monitors()
    if monitors:
        primary = monitors[0]
        page.window.left = primary.x + (primary.width - page.window.width) / 2
        page.window.top = primary.y + primary.height - page.window.height
    
    def debug_msg(msg: str, handler: str = "DEBUG"):
        print(f"[{handler}] {msg}")
    
    # ------- Event Handlers -------
    def on_keyboard_event(e: ft.KeyboardEvent):
        step = 20
        if e.key == "D":
            move_miku(step)
        elif e.key == "A":
            move_miku(step)

    def on_event(e: ft.WindowEvent):
        if e.type == ft.WindowEventType.MOVED:
            main_miku.set_state(Miku.NEUTRAL)
            main_miku.set_pan_start(False)
            restart_loop_after_delay()
        elif e.type == ft.WindowEventType.BLUR:
            main_miku.set_state(Miku.AMGRY)
        elif e.type == ft.WindowEventType.FOCUS:
            main_miku.set_state(Miku.HAPPY)
        check_and_adjust_bounds(page)

    def on_pan_start(_):
        main_miku.set_pan_start(True)
        main_miku.set_state(Miku.ECSTATIC)
        cancel_loop()

    def on_enter(_):
        main_miku.set_state(Miku.READY)

    def on_exit(_):
        if not main_miku.is_pan_start() and not main_miku.is_long_pressed() and not stop_event.is_set():
            main_miku.set_state(Miku.NEUTRAL)

    def on_tap(_):
        main_miku.set_state(Miku.PONDER)
        miku_chat()
        restart_loop_after_delay()

    def on_double_tap(_):
        cancel_loop()
        debug_msg(msg="Bye bye...", handler="Miku")
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
        cancel_loop()
        restart_loop_after_delay()
    
    def on_long_press_start(_):
        main_miku.set_state(Miku.SHOCK)
        main_miku.set_long_pressed(True)
        cancel_loop()
    
    def on_long_press_end(_):
        main_miku.set_state(Miku.AMGRY)
        main_miku.set_long_pressed(False)
        restart_loop_after_delay()
    
    # ------- Chat Feature -------
    def generate_speech(msg: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(value=msg, font_family="BlrrPix", size=16),
            bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE),
            padding=10, border_radius=15, left=0, right=0, top=0,
            border=ft.border.all(4, ft.Colors.with_opacity(0.5, ft.Colors.BLUE)),
            alignment=ft.alignment.top_center,
        )

    def remove_speech():
        nonlocal speech_bubble
        if speech_bubble and speech_bubble in miku_stack.controls:
            miku_stack.controls.remove(speech_bubble)
            speech_bubble = None
            page.update()

    def miku_chat():
        nonlocal speech_bubble, speech_timer

        # Cancel previous timer if still running
        if speech_timer and speech_timer.is_alive():
            speech_timer.cancel()

        if speech_bubble and speech_bubble in miku_stack.controls:
            # Reuse existing bubble
            speech_text: ft.Text = speech_bubble.content
            speech_text.value = random_line(speech_lines)
            page.update()
        else:
            # Create new bubble
            speech_bubble = generate_speech(random_line(speech_lines))
            miku_stack.controls.append(speech_bubble)
            page.update()

        # Reset removal timer
        speech_timer = threading.Timer(2, remove_speech)
        speech_timer.start()
    
    # ------- Movement Loop -------
    def restart_loop_after_delay(delay: int | None = None):
        nonlocal restart_timer
        cancel_loop()
        if restart_timer and restart_timer.is_alive():
            restart_timer.cancel()
        if delay is None:
            delay = random.randint(2, 4)
        debug_msg(f"Waiting for {delay}s before restarting loop.")
        restart_timer = threading.Timer(delay, start_loop)
        restart_timer.start()
    
    def move_miku(step: int):
        if step > 0:
            main_miku.set_flipped(False)
        else:
            main_miku.set_flipped(True)
            
        page.window.left += step
        
        check_and_adjust_bounds(page)
        page.update()
    
    def movement_loop():
        while not stop_event.is_set():
            if main_miku.is_pan_start() and not stop_event.is_set():
                debug_msg("Stopping Movement Loop :: Miku is being dragged!")
                break  # Stop if user drags Miku
            
            min, max = miku_mv_freq_ms[0], miku_mv_freq_ms[1]
            rnd_delay = random.randint(min, max) / 1000
            debug_msg(msg=f"Sleeping for {rnd_delay}s", handler="Miku")
            time.sleep(rnd_delay)
            
            rnd_step = random.randint(-100, 100)
            debug_msg(msg=f"Moving with {rnd_step}", handler="Miku")
            
            if not main_miku.is_pan_start() and not stop_event.is_set():
                move_miku(rnd_step)

    def start_loop():
        if main_miku.state != Miku.NEUTRAL.name:
            main_miku.set_state(Miku.NEUTRAL)
        debug_msg("Starting Movement Loop :: Starting Loop")
        stop_event.clear()
        threading.Thread(target=movement_loop, daemon=True).start()

    def cancel_loop():
        debug_msg("Stopping Movement Loop :: Cancelled Loop")
        stop_event.set()
    
    # Create Miku wrappers
    main_miku = DynamicMiku(Miku.NEUTRAL, debug=False)
    main_miku_img = main_miku.get_image()

    exit_miku = DynamicMiku(Miku.AMGRY, debug=False)
    exit_miku_img = exit_miku.get_image()
    exit_miku_img.animate_scale = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    exit_miku_img.animate_rotation = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    exit_miku_img.opacity = 0

    # Stack them
    miku_stack = ft.Stack(
        controls=[exit_miku_img, main_miku_img], alignment=ft.alignment.center,
        expand=True
    )

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
    page.on_keyboard_event = on_keyboard_event
    page.add(form)
    check_and_adjust_bounds(page)
    page.update()
    
    start_loop()

if __name__ == "__main__":
    ft.app(target=test)
