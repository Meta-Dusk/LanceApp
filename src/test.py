import flet as ft
import random
import asyncio

from styles import transparent_window
from images import DynamicMiku, Miku
from utilities import get_all_monitors, check_and_adjust_bounds, random_line, speech_lines, debug_msg


async def test(page: ft.Page):
    # -------- Setup --------
    DEBUG = True
    transparent_window(page, height=260, debug=DEBUG)

    stop_event = asyncio.Event()
    restart_timer: asyncio.Task | None = None
    speech_timer: asyncio.Task | None = None
    movement_task: asyncio.Task | None = None
    speech_bubble = None
    miku_mv_freq_ms = (1000, 1500)
    miku_mv_step = (-100, 100)

    # Window position
    monitors = get_all_monitors()
    if monitors:
        primary = monitors[0]
        page.window.left = primary.x + (primary.width - page.window.width) / 2
        page.window.top = primary.y + primary.height - page.window.height

    # -------- Task helpers --------
    def cancel_task(task: asyncio.Task | None):
        if task and not task.done():
            task.cancel()

    def start_loop():
        nonlocal movement_task
        cancel_task(movement_task)
        stop_event.clear()
        debug_msg("Starting Movement Loop :: Starting Loop", debug=DEBUG)
        movement_task = asyncio.create_task(movement_loop())

    def cancel_loop():
        stop_event.set()
        cancel_task(movement_task)
        debug_msg("Stopping Movement Loop :: Cancelled Loop", debug=DEBUG)

    def restart_loop_after_delay(delay: int | None = None):
        nonlocal restart_timer
        cancel_task(restart_timer)
        if delay is None:
            delay = random.randint(1, 2)
        debug_msg(f"Waiting for {delay}s before restarting loop.", debug=DEBUG)

        async def delayed_restart():
            await asyncio.sleep(delay)
            main_miku.set_state(Miku.NEUTRAL)
            page.update()
            start_loop()

        restart_timer = asyncio.create_task(delayed_restart())
    
    # -------- Movement --------
    async def movement_loop():
        while not stop_event.is_set():
            if main_miku.is_pan_start():
                debug_msg("Stopping Movement Loop :: Miku is being dragged!", debug=DEBUG)
                break
            rnd_delay = random.randint(*miku_mv_freq_ms) / 1000
            debug_msg(f"Sleeping for {rnd_delay}s", handler="Miku", debug=DEBUG)
            await asyncio.sleep(rnd_delay)

            rnd_step = random.randint(*miku_mv_step)
            debug_msg(f"Moving with {rnd_step}", handler="Miku", debug=DEBUG)

            if not main_miku.is_pan_start():
                if rnd_step > 80 or rnd_step < -80:
                    move_miku(rnd_delay, 3.14 * 2)
                else:
                    move_miku(rnd_step)
    
    def move_miku(step: int, rotate: float | None = None):
        if step > 0:
            main_miku.set_flipped(False)
        else:
            main_miku.set_flipped(True)
        main_miku_img.rotate = ft.Rotate(0.1 * (abs(step) / 100)) if rotate is None else rotate
        page.window.left += step
        check_and_adjust_bounds(page)
        page.update()
        page.window.update()
    
    # -------- Speech Feature --------
    async def remove_speech():
        nonlocal speech_bubble
        if speech_bubble and speech_bubble in miku_stack.controls:
            miku_stack.controls.remove(speech_bubble)
            speech_bubble = None
            page.update()

    def miku_chat(msg: str | None = None, emote: Miku | None = None, exit: bool = False):
        nonlocal speech_bubble, speech_timer
        random_chat = random_line(speech_lines)
        chat: str = random_chat["text"]
        emotion: str = random_chat["emotion"]

        cancel_task(speech_timer)

        if speech_bubble and speech_bubble in miku_stack.controls:
            speech_text: ft.Text = speech_bubble.content
            speech_text.value = chat if msg is None else msg
        else:
            speech_bubble = ft.Container(
                content=ft.Text(value=chat if msg is None else msg, font_family="BlrrPix", size=16),
                bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE),
                padding=10,
                border_radius=15,
                left=0,
                right=0,
                top=0,
                border=ft.Border.all(4, ft.Colors.with_opacity(0.5, ft.Colors.BLUE)),
                alignment=ft.Alignment.TOP_CENTER,
                offset=ft.Offset(0.0, -0.5),
            )
            miku_stack.controls.append(speech_bubble)

        main_miku.set_state(getattr(Miku, emotion.upper(), emotion) if emote is None else emote)
        page.update()

        if not exit:
            async def speech_remover():
                await asyncio.sleep(2)
                await remove_speech()
            speech_timer = asyncio.create_task(speech_remover())
    
    # -------- Event Handlers --------
    def on_keyboard_event(e: ft.KeyboardEvent):
        step = 20
        if e.key == "D":
            move_miku(step)
        elif e.key == "A":
            move_miku(-step)

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

    def on_drag_start(_):
        main_miku.set_pan_start(True)
        main_miku.set_state(Miku.ECSTATIC)
        cancel_loop()

    def on_enter(_):
        main_miku.set_state(Miku.READY)

    def on_exit(_):
        if not main_miku.is_pan_start() and not main_miku.is_long_pressed() and not stop_event.is_set():
            main_miku.set_state(Miku.NEUTRAL)

    def on_tap(_):
        miku_chat()
        restart_loop_after_delay()

    async def on_double_tap(_):
        miku_chat(msg="Bye bye 😔", emote=Miku.AMGRY, exit=True)
        cancel_loop()
        debug_msg("Bye bye...", handler="Miku", debug=DEBUG)
        exit_miku_img.opacity = 1
        main_miku_img.visible = False
        page.update()
        exit_miku_img.scale = 0
        exit_miku_img.rotate = ft.Rotate(-1)
        page.update()
        await asyncio.sleep(1)
        await page.window.close()

    def on_secondary_tap(_):
        miku_chat("You can double-click me for me to leave your desktop (≧﹏ ≦)", Miku.THINKING)
        cancel_loop()
        restart_loop_after_delay()

    def on_long_press_start(_):
        miku_chat("W-what are you doing?! ヽ（≧□≦）ノ", Miku.SHOCK)
        main_miku.set_long_pressed(True)
        cancel_loop()

    def on_long_press_end(_):
        miku_chat("Hmph (* ￣︿￣)", Miku.AMGRY)
        main_miku.set_long_pressed(False)
        restart_loop_after_delay()

    # -------- Setup Miku --------
    main_miku = DynamicMiku(Miku.NEUTRAL, debug=False)
    main_miku_img = main_miku.get_image()
    main_miku_img.animate_rotation = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)

    exit_miku = DynamicMiku(Miku.AMGRY, debug=False)
    exit_miku_img = exit_miku.get_image()
    exit_miku_img.animate_scale = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    exit_miku_img.animate_rotation = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    exit_miku_img.opacity = 0

    miku_stack = ft.Stack(
        controls=[exit_miku_img, main_miku_img],
        alignment=ft.Alignment.BOTTOM_CENTER,
        expand=True,
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
        on_secondary_tap=on_secondary_tap,
    )
    form = ft.WindowDragArea(content=miku_gs, maximizable=False, on_drag_start=on_drag_start)

    page.window.on_event = on_event
    page.on_keyboard_event = on_keyboard_event
    page.add(form)
    check_and_adjust_bounds(page)
    page.update()

    start_loop()


if __name__ == "__main__":
    ft.app(target=test)
