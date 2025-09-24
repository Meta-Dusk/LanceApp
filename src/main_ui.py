import flet as ft
import random
import asyncio
import math

from typing import Optional, Tuple
from components import default_speech_bubble
from images import DynamicMiku, Miku
from utilities import (
    check_and_adjust_bounds, random_line, speech_lines, debug_msg, cancel_task,
    await_task_completion, is_within_radius, chance
)


async def main_app(page: ft.Page, debug: bool = False):
    # -------- Setup --------
    # Task Flags for Loops
    stop_event = asyncio.Event() # Used to control movement loop only
    restart_timer: Optional[asyncio.Task] = None
    speech_timer: Optional[asyncio.Task] = None
    movement_task: Optional[asyncio.Task] = None
    idle_task: Optional[asyncio.Task] = None
    
    # Controls
    speech_bubble: Optional[ft.Control] = None
    
    ## -- Variables --
    # Movement
    miku_mv_freq_ms: Tuple[int, int] = (1000, 1500)  # Frequency of randomized Miku movement
    miku_mv_step: Tuple[int, int] = (-100, 100)      # Range of randomized Miku movement
    miku_rt_mod: float = 0.3                         # Rotation modifier for Miku flip
    miku_flip_chance: int = 5                        # Chance of Miku flip out of 100%
    fps: float = 60.0
    
    # Idle Animation
    idle_phase: float = 0.0
    idle_amp: float = 4.0               # pixels up/down (tweak for subtlety)
    idle_base_top = page.window.top     # baseline for idle bobbing
    
    # Speech Values (in seconds)
    msg_base_time: float = 2.0          # Minimum time to display
    per_char_time: float = 0.005        # Tweak speed factor

    # -------- Task Helpers --------
    def start_loop() -> None:
        """Starts Movement Loop"""
        nonlocal movement_task
        cancel_task(movement_task)
        stop_event.clear()
        debug_msg("Starting Movement Loop :: Starting Loop", debug=debug)
        movement_task = asyncio.create_task(movement_loop())

    def cancel_loop() -> None:
        """Stops movement loop."""
        stop_event.set()
        cancel_task(movement_task)
        debug_msg("Stopping Movement Loop :: Cancelled Loop", debug=debug)

    def restart_loop_after_delay(delay: float = 2.0) -> None:
        """If `delay <= 0` then cancel, and `delay` is in seconds."""
        nonlocal restart_timer
        cancel_task(restart_timer)
        cancel_loop()
        
        if delay <= 0:
            debug_msg(f"Cancelling restart loop since delay={delay}", debug=debug)
            return
        
        debug_msg(f"Waiting for {delay}s before restarting loop.", debug=debug)

        async def delayed_restart():
            await asyncio.sleep(delay)
            main_miku.set_state(Miku.NEUTRAL)
            page.update()
            start_loop()

        restart_timer = asyncio.create_task(delayed_restart())

    # -------- Movement (Smooth OS Window Animation) --------
    async def movement_loop() -> None:
        """Handles the movement loop for Miku."""
        nonlocal miku_flip_chance, miku_mv_freq_ms, miku_mv_step
        
        while not stop_event.is_set():
            if main_miku.is_pan_start():
                debug_msg("Stopping Movement Loop :: Miku is being dragged!", debug=debug)
                break

            rnd_delay = random.randint(*miku_mv_freq_ms) / 1000
            debug_msg(f"Sleeping for {rnd_delay}s", handler="Miku", debug=debug)
            await asyncio.sleep(rnd_delay)

            rnd_step = random.randint(*miku_mv_step)
            debug_msg(f"Moving with {rnd_step}", handler="Miku", debug=debug)

            if not main_miku.is_pan_start():
                if chance(miku_flip_chance):
                    rnd_rotation = math.pi * 2 * math.copysign(1, rnd_step)
                    await move_miku_smooth(step=rnd_step, rotate=rnd_rotation, base_duration=rnd_delay)
                else:
                    await move_miku_smooth(step=rnd_step, base_duration=rnd_delay * 0.25)
    
    async def move_miku_smooth(
        step: int, rotate: Optional[float] = None,
        base_duration: float = 0.2, fps: int = fps
    ) -> None:
        """Smoothly animate the OS window horizontally with ease-out curve and jiggle."""
        nonlocal idle_base_top
        # pause idle while actively sliding
        stop_idle_bobbing()
        
        if step == 0:
            # nothing to move; ensure idle is running again
            start_idle_bobbing()
            return

        # Flip sprite based on direction
        if step > 0:
            main_miku.set_flipped(False)
        else:
            main_miku.set_flipped(True)

        # Add playful rotation
        main_miku_img.rotate = ft.Rotate(miku_rt_mod * (abs(step) / 100)) if rotate is None else rotate
        page.update()

        # Dynamic duration scaling
        duration = base_duration + (abs(step) / 300)  # larger step = slower glide
        frames = max(1, int(duration * fps))

        # Current positions
        start_left = page.window.left
        target_left = start_left + step

        # Jiggle amplitude and frequency
        jiggle_amp = 3  # pixels
        jiggle_freq = 2 * math.pi / frames  # one small oscillation

        for i in range(frames):
            if stop_event.is_set() or main_miku.is_pan_start():
                # interrupted -> set new baseline to current top and resume idle
                idle_base_top = page.window.top
                start_idle_bobbing()
                return

            # Ease-out interpolation
            t = i / frames
            eased_t = 1 - (1 - t) ** 3  # cubic ease-out

            # Horizontal movement
            new_left = start_left + (step * eased_t)

            # Compute vertical jiggle relative to the baseline (do NOT rebase each frame)
            new_top = idle_base_top + math.sin(i * jiggle_freq) * jiggle_amp

            page.window.left = new_left
            page.window.top = new_top
            page.window.update()

            await asyncio.sleep(1 / fps)

        # Snap to target to avoid drift
        page.window.left = target_left
        page.window.top = round(idle_base_top)  # reset jiggle rounding

        # Reset baseline for idle bobbing
        idle_base_top = page.window.top
        page.window.update()
        
        check_and_adjust_bounds(page)
        start_idle_bobbing()
    
    # ---- Idle Bobbing (Independent Lifecycle) ----    
    async def idle_bobbing_loop() -> None:
        """Handles the idle animation loop."""
        nonlocal idle_phase, fps
        base_top = page.window.top
        
        main_miku_img.rotate = 0
        page.update()
        
        while not main_miku.is_pan_start():
            offset = math.sin(idle_phase) * idle_amp
            page.window.top = base_top + offset
            page.window.update()
            idle_phase += 0.08
            
            if idle_phase > math.tau:
                idle_phase -= math.tau
                
            await asyncio.sleep(1 / fps)

    def start_idle_bobbing() -> None:
        """Starts the idle animation."""
        nonlocal idle_task
        debug_msg(msg="Idle bobbing started", handler="Miku", debug=debug)
        if idle_task and not idle_task.done():
            return
        idle_task = asyncio.create_task(idle_bobbing_loop())

    def stop_idle_bobbing() -> None:
        """Stops the idle animation."""
        nonlocal idle_task
        if idle_task and not idle_task.done():
            debug_msg(msg="Idle bobbing stopped", handler="Miku", debug=debug)
            idle_task.cancel()
            idle_task = None
    
    # -------- Speech Feature --------
    async def remove_speech(delay: Optional[float] = None) -> None:
        """Removes all speech bubbles in use, with optional delay before deletion."""
        nonlocal speech_bubble
        
        if delay and delay > 0:
            await asyncio.sleep(delay)
        else:
            raise ValueError(f"delay shouldn't be negative. Received value for `remove_speech()` = {delay}")
        
        if speech_bubble and speech_bubble in miku_stack.controls:
            miku_stack.controls.remove(speech_bubble)
            speech_bubble = None
            page.update()
            
        # ensure bobbing continues after speech removed
        start_idle_bobbing()
    
    def miku_chat(msg: Optional[str] = None, emote: Optional[Miku] = None, duration: Optional[float] = None) -> float:
        """
        Make Miku say something in a speech bubble.
        
        Args:
            msg (str | None): The message that Miku will say.
            emote (Miku | None): Takes a `Miku` class object, for setting her expressions.
            duration (float | None): The duration of how long the message will show. Set the `duration <= 0` if the message shouldn't expire.
        
        Returns:
            float: The duration used for displaying the message.
        """
        nonlocal speech_bubble, speech_timer, msg_base_time, per_char_time
        random_chat = random_line(speech_lines)
        chat: str = random_chat["text"]
        emotion: str = random_chat["emotion"]
        
        # Dynamic duration fallback
        if duration is None:
            dynamic_duration = msg_base_time + per_char_time * len(chat)
            duration = round(dynamic_duration, 3)

        cancel_task(speech_timer)

        if speech_bubble and speech_bubble in miku_stack.controls:
            speech_text: ft.Text = speech_bubble.content
            speech_text.value = chat if msg is None else msg
        else:
            speech_bubble = default_speech_bubble(chat if msg is None else msg)
            miku_stack.controls.append(speech_bubble)

        main_miku.set_state(
            getattr(Miku, emotion.upper(), emotion) if emote is None else emote
        )
        page.update()
        
        # ensure idle is running (idempotent) (Mr. GPT truly out here with technical jargon)
        start_idle_bobbing()
        
        if duration > 0:
            speech_timer = asyncio.create_task(remove_speech(duration))
        
        return duration

    # -------- Event Handlers --------
    async def on_keyboard_event(e: ft.KeyboardEvent) -> None:
        if debug:
            step = 20
            if e.key == "D":
                await move_miku_smooth(step)
            elif e.key == "A":
                await move_miku_smooth(-step)

    async def on_close(_) -> None:
        debug_msg("Window closing... Cleaning up tasks.", debug=debug)

        for task in [movement_task, restart_timer, speech_timer, idle_task]:
            await await_task_completion(task)

        await page.window.close()

    def on_event(e: ft.WindowEvent) -> None:
        if e.type == ft.WindowEventType.MOVED:
            # user moved window; update baseline and resume idle
            main_miku.set_pan_start(False)
            
            # IMPORTANT: update idle baseline to user's new position
            nonlocal idle_base_top
            idle_base_top = page.window.top
            
            start_idle_bobbing()
            restart_loop_after_delay(miku_chat(msg="╰(￣ω￣ｏ)", emote=Miku.NEUTRAL))
            
        elif e.type == ft.WindowEventType.BLUR:
            main_miku.set_state(Miku.AMGRY)
            
        elif e.type == ft.WindowEventType.FOCUS:
            main_miku.set_state(Miku.HAPPY)
            
        elif e.type == ft.WindowEventType.CLOSE:
            asyncio.create_task(on_close(e))

        check_and_adjust_bounds(page)

    def on_drag_start(_) -> None:
        main_miku.set_pan_start(True)
        delay = miku_chat(msg="Where we going? o((>ω< ))o", emote=Miku.ECSTATIC, duration=0)
        restart_loop_after_delay(delay)

    def on_enter(_) -> None: # User hovers over Miku
        if not (speech_bubble and speech_bubble in miku_stack.controls):
            main_miku.set_state(Miku.READY)

    def on_exit(_) -> None: # Default state for Miku
        if (
            not main_miku.is_pan_start()
            and not main_miku.is_long_pressed()
            and not stop_event.is_set()
        ):
            main_miku.set_state(Miku.NEUTRAL)
    
    def on_tap_down(e: ft.TapEvent):
        delay: float
        local_position: ft.Offset = e.local_position
        
        if is_within_radius(center=ft.Offset(x=141.0, y=210.0), point=local_position, radius=40):
            delay = miku_chat(msg="W-what are you doing?! ヽ（≧□≦）ノ", emote=Miku.SHOCK)
            
        elif is_within_radius(center=ft.Offset(x=121.0, y=135.0), point=local_position, radius=50):
            delay = miku_chat(msg="I-I do like h-headpats (≧﹏ ≦)", emote=Miku.PONDER)
            
        else:
            delay = miku_chat()
            
        restart_loop_after_delay(delay)
        
    
    #TODO: Implement a sub-menu for Miku
    async def on_double_tap(_) -> None: # Placeholder interaction for exitting application
        miku_chat(msg="Bye bye ヽ（≧□≦）ノ", emote=Miku.AMGRY, duration=0)
        cancel_loop()
        debug_msg("Bye bye...", handler="Miku", debug=debug)

        exit_miku_img.opacity = 1
        main_miku_img.visible = False
        page.update()

        exit_miku_img.scale = 0
        exit_miku_img.rotate = ft.Rotate(-1)
        page.update()

        await asyncio.sleep(1)
        await on_close(_)

    def on_secondary_tap(_) -> None: # When user right-clicks (or secondary) Miku
        delay = miku_chat(
            msg="You can double-click me for me to leave your desktop (≧﹏ ≦)", 
            emote=Miku.THINKING)
        cancel_loop()
        restart_loop_after_delay(delay)

    def on_long_press_start(e: ft.LongPressStartEvent) -> None:
        delay = miku_chat(
            msg="The patch notes says, that there will be more Miku interactions soon! ( •̀ ω •́ )✧",
            emote=Miku.READING, duration=0)
        
        main_miku.set_long_pressed(True)
        restart_loop_after_delay(delay)

    def on_long_press_end(e: ft.LongPressEndEvent) -> None:
        main_miku.set_long_pressed(False)
        restart_loop_after_delay(miku_chat())

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
        on_tap_down=on_tap_down,
        on_long_press_start=on_long_press_start,
        on_long_press_end=on_long_press_end,
        on_secondary_tap=on_secondary_tap,
        expand=True
    )
    
    form = ft.WindowDragArea(
        content=miku_gs, maximizable=False, on_drag_start=on_drag_start,
        expand=True
    )

    page.window.on_event = on_event
    page.on_keyboard_event = on_keyboard_event
    page.add(form)

    check_and_adjust_bounds(page)
    start_loop()
    start_idle_bobbing()


if __name__ == "__main__":
    ft.app(target=main_app)