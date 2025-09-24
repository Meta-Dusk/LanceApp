import flet as ft
import random
import asyncio
import math

from typing import Optional
from styles import transparent_window, FontStyles
from images import DynamicMiku, Miku
from utilities import (
    get_all_monitors, check_and_adjust_bounds, random_line,
    speech_lines, debug_msg,
)


DEBUG = True


async def before_main_app(page: ft.Page):
    # -------- Before Main App --------
    transparent_window(page, height=260, debug=DEBUG)
    
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
    

async def main_app(page: ft.Page):
    # -------- Setup --------
    # Task Flags for Loops
    stop_event = asyncio.Event() # Used to control movement loop only
    restart_timer: asyncio.Task | None = None
    speech_timer: asyncio.Task | None = None
    movement_task: asyncio.Task | None = None
    idle_task: asyncio.Task | None = None
    
    # Controls
    speech_bubble = None
    
    ## Variables
    # Movement
    miku_mv_freq_ms = (1000, 1500)
    miku_mv_step = (-100, 100)
    
    # Idle Animation
    idle_running = False
    idle_phase = 0.0
    idle_amp = 4  # pixels up/down (tweak for subtlety)
    idle_base_top = page.window.top  # baseline for idle bobbing

    # -------- Task Helpers --------
    def cancel_task(task: asyncio.Task | None):
        if task and not task.done():
            task.cancel()

    async def _await_task_completion(task: asyncio.Task | None):
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    def start_loop():
        nonlocal movement_task
        cancel_task(movement_task)
        stop_event.clear()
        debug_msg("Starting Movement Loop :: Starting Loop", debug=DEBUG)
        movement_task = asyncio.create_task(movement_loop())

    def cancel_loop():
        stop_event.set() # Stops movement loop
        cancel_task(movement_task)
        debug_msg("Stopping Movement Loop :: Cancelled Loop", debug=DEBUG)

    def restart_loop_after_delay(delay: int | None = None):
        nonlocal restart_timer
        cancel_task(restart_timer)
        cancel_loop()

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
                    rnd_rotation = math.pi * 2 * math.copysign(1, rnd_step)
                    await move_miku_smooth(rnd_delay, rotate=rnd_rotation)
                else:
                    await move_miku_smooth(rnd_step)

    def move_miku(step: int, rotate: float | None = None):
        if step > 0:
            main_miku.set_flipped(False)
        else:
            main_miku.set_flipped(True)

        main_miku_img.rotate = (
            ft.Rotate(0.1 * (abs(step) / 100)) if rotate is None else rotate
        )
        page.window.left += step
        check_and_adjust_bounds(page)
        page.update()
        page.window.update()
    
    async def move_miku_smooth(
        step: int, rotate: float | None = None,
        base_duration: float = 0.2, fps: int = 60
    ):
        """Smoothly animate the OS window horizontally with ease-out curve and jiggle."""
        stop_idle_bobbing()
        
        if step == 0:
            start_idle_bobbing()
            return

        # Flip sprite based on direction
        if step > 0:
            main_miku.set_flipped(False)
        else:
            main_miku.set_flipped(True)

        # Add playful rotation
        main_miku_img.rotate = ft.Rotate(0.1 * (abs(step) / 100)) if rotate is None else rotate
        page.update()

        # Dynamic duration scaling
        duration = base_duration + (abs(step) / 300)  # larger step = slower glide
        frames = int(duration * fps)

        # Current positions
        start_left = page.window.left
        target_left = start_left + step

        # Jiggle amplitude
        jiggle_amp = 3  # pixels
        jiggle_freq = 2 * math.pi / frames  # one small oscillation

        for i in range(frames):
            if stop_event.is_set() or main_miku.is_pan_start():
                start_idle_bobbing()
                return

            # Ease-out interpolation
            t = i / frames
            eased_t = 1 - (1 - t) ** 3  # cubic ease-out

            # Horizontal movement
            new_left = start_left + (step * eased_t)

            # Vertical jiggle
            new_top = page.window.top + math.sin(i * jiggle_freq) * jiggle_amp

            page.window.left = new_left
            page.window.top = new_top
            page.window.update()

            await asyncio.sleep(1 / fps)

        # Snap to target to avoid drift
        page.window.left = target_left
        page.window.top = round(page.window.top)  # reset jiggle rounding

        # Reset baseline for idle bobbing
        nonlocal idle_base_top
        idle_base_top = page.window.top
        page.window.update()
        
        check_and_adjust_bounds(page)
        start_idle_bobbing()
    
    # -------- Idle Animation --------
    async def idle_bobbing_loop():
        nonlocal idle_phase, idle_running, idle_base_top
        idle_running = True

        while not stop_event.is_set():
            # Smooth sine-wave offset from baseline
            offset = math.sin(idle_phase) * idle_amp
            page.window.top = idle_base_top + offset
            page.window.update()

            await asyncio.sleep(1 / 60)  # ~60fps
            idle_phase += 0.08
            if idle_phase > math.tau:
                idle_phase -= math.tau

        idle_running = False


    def start_idle_bobbing():
        nonlocal idle_task
        debug_msg(msg="Idle bobbing started", handler="Miku", debug=DEBUG)
        if idle_task and not idle_task.done():
            return
        idle_task = asyncio.create_task(idle_bobbing_loop())


    def stop_idle_bobbing():
        nonlocal idle_task
        if idle_task and not idle_task.done():
            debug_msg(msg="Idle bobbing stopped", handler="Miku", debug=DEBUG)
            idle_task.cancel()
            idle_task = None
    
    # -------- Speech Feature --------
    async def remove_speech():
        nonlocal speech_bubble
        if speech_bubble and speech_bubble in miku_stack.controls:
            miku_stack.controls.remove(speech_bubble)
            speech_bubble = None
            page.update()

    def miku_chat(
        msg: Optional[str] = None,
        emote: Optional[Miku] = None,
        exit: bool = False,
        duration: int = 2
    ):
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
                content=ft.Text(
                    value=chat if msg is None else msg, font_family=FontStyles.BLRRPIX,
                    size=16, text_align=ft.TextAlign.CENTER
                ),
                bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE),
                padding=10, border_radius=15, left=0, right=0, top=0,
                border=ft.Border.all(4, ft.Colors.with_opacity(0.7, ft.Colors.BLUE_900)),
                alignment=ft.Alignment.TOP_CENTER,
                offset=ft.Offset(0.0, -0.5),
            )
            miku_stack.controls.append(speech_bubble)

        main_miku.set_state(
            getattr(Miku, emotion.upper(), emotion) if emote is None else emote
        )
        page.update()
        
        if not exit:
            async def speech_remover():
                await asyncio.sleep(duration)
                await remove_speech()

            speech_timer = asyncio.create_task(speech_remover())

    # -------- Event Handlers --------
    def on_keyboard_event(e: ft.KeyboardEvent):
        if DEBUG:
            step = 20
            if e.key == "D":
                move_miku(step)
            elif e.key == "A":
                move_miku(-step)

    async def on_close(_):
        debug_msg("Window closing... Cleaning up tasks.", debug=DEBUG)

        for task in [movement_task, restart_timer, speech_timer]:
            await _await_task_completion(task)

        await page.window.close()

    def on_event(e: ft.WindowEvent):
        if e.type == ft.WindowEventType.MOVED:
            miku_chat("╰(￣ω￣ｏ)", Miku.NEUTRAL)
            main_miku.set_pan_start(False)
            restart_loop_after_delay()
        elif e.type == ft.WindowEventType.BLUR:
            main_miku.set_state(Miku.AMGRY)
        elif e.type == ft.WindowEventType.FOCUS:
            main_miku.set_state(Miku.HAPPY)
        elif e.type == ft.WindowEventType.CLOSE:
            asyncio.create_task(on_close(e))

        check_and_adjust_bounds(page)

    def on_drag_start(_):
        main_miku.set_pan_start(True)
        miku_chat("Where we going? o((>ω< ))o", Miku.ECSTATIC)
        cancel_loop()

    def on_enter(_):
        main_miku.set_state(Miku.READY)

    def on_exit(_):
        if (
            not main_miku.is_pan_start()
            and not main_miku.is_long_pressed()
            and not stop_event.is_set()
        ):
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
        await on_close(_)

    def on_secondary_tap(_):
        miku_chat(
            "You can double-click me for me to leave your desktop (≧﹏ ≦)", Miku.THINKING
        )
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
    form = ft.WindowDragArea(
        content=miku_gs, maximizable=False, on_drag_start=on_drag_start
    )

    page.window.on_event = on_event
    page.on_keyboard_event = on_keyboard_event
    page.add(form)

    check_and_adjust_bounds(page)
    start_loop()
    start_idle_bobbing()


if __name__ == "__main__":
    ft.app(target=main_app)
