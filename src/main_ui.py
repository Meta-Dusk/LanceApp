import flet as ft
import random
import asyncio
import math

from desktop_notifier import DesktopNotifier, Urgency
from typing import Optional, Tuple
from setup import set_win_pos_bc
from components import default_speech_bubble, default_menu
from images import DynamicMiku, Miku
from utilities.data import speech_lines, random_line
from utilities.timers import ResettableTimer, DeltaTimer
from utilities.tasks import cancel_task, await_task_completion
from utilities.debug import get_full_username, debug_msg
from utilities.helpers import rnd_miku_chat
from utilities.monitor import check_and_adjust_bounds, get_all_monitors
from utilities.math import chance, is_within_radius

# TODO: If possible, refactor everything related to Miku into a class for modularity.
async def main_app(page: ft.Page, debug: bool = False):
    # -------- Setup --------
    # Task Flags for Loops
    stop_event = asyncio.Event() # Used to control movement loop only
    restart_timer: Optional[asyncio.Task] = None
    speech_timer: Optional[asyncio.Task] = None
    movement_task: Optional[asyncio.Task] = None
    idle_task: Optional[asyncio.Task] = None
    
    # Controls
    speech_bubble = default_speech_bubble("")
    
    ## -- Variables --
    # Debug Stuff
    ENABLE_MV_OVERRIDE: bool = False
    SHOW_MOVEMENT_LOGS: bool = False
    SHOW_IDLE_LOGS: bool = False
    exit_app: bool = False
    open_menu: bool = False
    ALLOW_VOID_TRAVERSAL: bool = False
    is_miku_chatting: bool = False
    disable: bool = False
    
    # Movement
    MIKU_MV_FREQ_MS: Tuple[int, int] = (1000, 1500)  # Frequency of randomized Miku movement
    MIKU_MV_STEP: Tuple[int, int] = (-300, 300)      # Range of randomized Miku movement
    MIKU_RT_MOD: float = 0.3                         # Rotation modifier for Miku flip
    MIKU_FLIP_CHANCE: int = 5                        # Chance of Miku flip out of 100%
    MIKU_CHAT_CHANCE: int = 20                       # Chance for Miku to randomly chat out of 100%
    FPS: float = 60.0                                # For smooth movement animation
    
    # Idle Animation
    idle_phase: float = 0.0
    IDLE_AMP: float = 4.0               # pixels up/down (tweak for subtlety)
    idle_base_top = page.window.top     # baseline for idle bobbing
    
    # Speech Values (in seconds)
    MSG_BASE_TIME: float = 2.0          # Minimum time to display
    PER_CHAR_TIME: float = 0.005        # Tweak speed factor
    
    # Timers for Stuff
    interaction_timer: ResettableTimer = None
    interaction_increment: int = 0
    exit_timer: ResettableTimer = None
    global_timer: DeltaTimer = DeltaTimer(target_fps=FPS)
    
    # -------- Window Functions --------
    async def to_front_with_delay(delay: float = 1):
        debug_msg(f"Bringing Miku to the front for {delay}s", debug=False)
        page.window.always_on_top = True
        await asyncio.sleep(delay)
        page.window.always_on_top = False
        debug_msg("Brought Miku to the front.", debug=False)
    
    # -------- Task Helpers --------
    def start_movement_loop() -> None:
        """Starts Movement Loop"""
        nonlocal movement_task
        cancel_task(movement_task)
        stop_event.clear()
        debug_msg("Starting Movement Loop :: Starting Loop", debug=SHOW_MOVEMENT_LOGS)
        movement_task = asyncio.create_task(movement_loop())

    def stop_movement_loop() -> None:
        """Stops movement loop."""
        stop_event.set()
        cancel_task(movement_task)
        debug_msg("Stopping Movement Loop :: Cancelled Loop", debug=SHOW_MOVEMENT_LOGS)

    def restart_loop_after_delay(delay: float = 2.0) -> None:
        """If `delay <= 0` then cancel, and `delay` is in seconds."""
        nonlocal restart_timer
        cancel_task(restart_timer)
        stop_movement_loop()
        
        if delay <= 0:
            debug_msg(f"Cancelling restart loop since delay={delay}", debug=debug)
            return
        
        debug_msg(f"Waiting for {delay}s before restarting loop.", debug=debug)

        async def delayed_restart():
            await asyncio.sleep(delay)
            if is_miku_chatting:
                return
            print("[delayed_restart] Setting to Neutral")
            miku.set_state(Miku.NEUTRAL)
            page.update()
            start_movement_loop()

        restart_timer = asyncio.create_task(delayed_restart())

    # -------- Movement (Smooth OS Window Animation) --------
    async def movement_loop() -> None:
        """Handles the movement loop for Miku."""
        while not stop_event.is_set() and not ENABLE_MV_OVERRIDE and not open_menu:
            if miku.is_pan_start():
                debug_msg("Stopping Movement Loop :: Miku is being dragged!", debug=SHOW_MOVEMENT_LOGS)
                break

            rnd_delay = random.randint(*MIKU_MV_FREQ_MS) / 1000
            debug_msg(f"Sleeping for {rnd_delay}s", handler="Miku", debug=SHOW_MOVEMENT_LOGS)
            await asyncio.sleep(rnd_delay)

            rnd_step = random.randint(*MIKU_MV_STEP)
            debug_msg(
                msg=f"Moving {rnd_step}px to the {"left" if rnd_step < 0 else "right"}.",
                handler="Miku", debug=SHOW_MOVEMENT_LOGS
            )

            if not miku.is_pan_start():
                if chance(MIKU_FLIP_CHANCE):
                    rnd_rotation = math.pi * 2 * math.copysign(1, -rnd_step)
                    await move_miku_smooth(step=rnd_step, rotate=rnd_rotation, base_duration=rnd_delay)
                else:
                    await move_miku_smooth(step=rnd_step, base_duration=rnd_delay * 0.5)
    
    async def move_miku_smooth(step: int, rotate: Optional[float] = None, base_duration: float = 0.2) -> None:
        """Smoothly animate the OS window horizontally with ease-out curve and jiggle."""
        nonlocal idle_base_top
        stop_idle_bobbing()
        
        if step == 0:
            start_idle_bobbing() # nothing to move; ensure idle is running again
            return

        # Flip sprite based on direction
        miku.set_flipped(step < 0)

        # Rotate towards target
        miku_img.rotate = ft.Rotate(MIKU_RT_MOD * (abs(step) / 100)) if rotate is None else rotate
        page.update()

        duration = base_duration + (abs(step) / 300)  # larger step = slower glide

        # Current positions
        start_left = page.window.left
        target_left = start_left + step

        jiggle_amp = 3
        
        elapsed = 0.0
        while elapsed < duration:
            dt = await global_timer.tick()
            # print(f"[Animation::Movement] Waited for {round(dt, 2)}s or {int(dt*1000)}ms")
            elapsed += dt
            t = min(1.0, elapsed / duration)
            
            if miku.is_pan_start():
                idle_base_top = page.window.top
                start_idle_bobbing()
                return
            
            eased_t = 1 - (1 - t) ** 3
            new_left = start_left + (step * eased_t)
            jiggle = math.sin(t * math.tau) * jiggle_amp
            new_top = idle_base_top + jiggle

            page.window.left = new_left
            page.window.top = new_top
            page.window.update()

        # Snap to target to avoid drift
        page.window.left = target_left
        page.window.top = round(idle_base_top)  # reset jiggle rounding
        page.window.update()
        
        # Reset baseline for idle bobbing
        idle_base_top = page.window.top
        
        start_idle_bobbing()
        await to_front_with_delay()
        
        is_in_bounds = check_and_adjust_bounds(page, debug)
        if not is_in_bounds:
            debug_msg("Attempting to restore position...", debug=debug)
            if not ALLOW_VOID_TRAVERSAL:
                page.window.left += step
                page.window.update()
            else:
                debug_msg("WARNING! Miku can move past monitor boundaries.", debug=debug)
                def on_clicked():
                    nonlocal target_left
                    
                    stop_movement_loop()
                    set_win_pos_bc(get_all_monitors(), page)
                    page.window.update()
                    target_left = page.window.left
                    restart_loop_after_delay(1)
                
                notifier = DesktopNotifier(app_name="Hatsune Miku")
                await notifier.send(
                    title="Help Me!",
                    message="I've somehow ended up outside of your monitor... I'm in the void! （；´д｀）ゞ",
                    urgency=Urgency.Critical,
                    on_clicked=on_clicked
                )
                
            await miku_chat("W-woah... So that's what the void looks like (⊙_⊙;)", Miku.SHOCK)
            
        else:
            if chance(MIKU_CHAT_CHANCE):
                await miku_chat()
    
    
    # ---- Idle Bobbing (Independent Lifecycle) ----
    async def idle_bobbing_loop() -> None:
        nonlocal idle_phase, idle_base_top
        
        miku_img.rotate = 0
        page.update()
        
        while not miku.is_pan_start() and not open_menu:
            dt = await global_timer.tick()
            
            idle_phase += IDLE_AMP * dt
            if idle_phase > math.tau:
                idle_phase -= math.tau
                
            offset = math.sin(idle_phase) * IDLE_AMP
            page.window.top = idle_base_top + offset
            page.window.update()
            
    def start_idle_bobbing() -> None:
        """Starts the idle animation."""
        nonlocal idle_task
        debug_msg(msg="Idle bobbing started", handler="Miku", debug=SHOW_IDLE_LOGS)
        if idle_task and not idle_task.done():
            return
        idle_task = asyncio.create_task(idle_bobbing_loop())

    def stop_idle_bobbing() -> None:
        """Stops the idle animation."""
        nonlocal idle_task
        if idle_task and not idle_task.done():
            debug_msg(msg="Idle bobbing stopped", handler="Miku", debug=SHOW_IDLE_LOGS)
            idle_task.cancel()
            idle_task = None
    
    # -------- Speech Feature --------
    async def remove_speech(delay: Optional[float] = None) -> None:
        """Removes all speech bubbles in use, with optional delay before deletion."""
        nonlocal speech_bubble, is_miku_chatting
        
        if delay and delay > 0:
            await asyncio.sleep(delay)
            speech_bubble.opacity = 0
            speech_bubble.offset = ft.Offset(x=0.0, y=1.0)
            page.update()
            await asyncio.sleep(0.2)
            miku.set_state(Miku.NEUTRAL)
            is_miku_chatting = False
    
    async def miku_chat(msg: Optional[str] = None, emote: Optional[Miku] = None, duration: Optional[float] = None) -> float:
        """
        Make Miku say something in a speech bubble.
        
        Args:
            msg (str | None): The message that Miku will say.
            emote (Miku | None): Takes a `Miku` class object, for setting her expressions.
            duration (float | None): The duration of how long the message will show. Set the `duration <= 0` if the message shouldn't expire.
        
        Returns:
            float: The duration used for displaying the message.
        """
        nonlocal speech_bubble, speech_timer, is_miku_chatting
        
        is_miku_chatting = True
        random_chat = random_line(speech_lines)
        chat: str = random_chat["text"]
        emotion: str = random_chat["emotion"]
        
        # Dynamic duration fallback
        if duration is None:
            dynamic_duration = MSG_BASE_TIME + PER_CHAR_TIME * len(chat)
            duration = round(dynamic_duration, 3)
            
        cancel_task(speech_timer)
        
        speech_text: ft.Text = speech_bubble.content
        speech_text.value = chat if msg is None else msg
        speech_bubble.update()
        
        miku.set_state(
            getattr(Miku, emotion.upper(), emotion) if emote is None else emote
        )
        speech_bubble.offset = ft.Offset(x=0.0, y=0.0)
        speech_bubble.opacity = 1
        page.update()
        await asyncio.sleep(0.2)
        
        # ensure idle is running (idempotent) (Mr. GPT truly out here with technical jargon)
        start_idle_bobbing()
        
        debug_msg(f"Miku's chat will be shown {f"for {duration}s" if duration > 0 else "indefinitely"}.", debug=debug)
        speech_timer = asyncio.create_task(remove_speech(duration)) if duration > 0 else None
        
        return duration

    # -------- Event Handlers --------
    async def on_keyboard_event(e: ft.KeyboardEvent) -> None:
        nonlocal ENABLE_MV_OVERRIDE
        if exit_app:
            return
        # print(f"Detected key press: {e.key}")
        if e.key == "`":
            ENABLE_MV_OVERRIDE = not ENABLE_MV_OVERRIDE
            
            if ENABLE_MV_OVERRIDE:
                stop_movement_loop()
                await miku_chat(
                    msg="S-something's wrong... I seem to can't move on my own anymore? (´。＿。｀)",
                    emote=Miku.SHOCK
                )
            else:
                start_movement_loop()
                await miku_chat(msg="I can move again now! (/≧▽≦)/", emote=Miku.JOY)
            
        if ENABLE_MV_OVERRIDE:
            step = 100
            if e.key == "D":
                await move_miku_smooth(step)
                
            elif e.key == "A":
                await move_miku_smooth(-step)

    async def on_event(e: ft.WindowEvent) -> None:
        if exit_app:
            return
        async def window_interactions(e: ft.WindowEvent):
            delay: float = 2
            
            if e.type == ft.WindowEventType.MOVED:
                # user moved window; update baseline and resume idle
                miku.set_pan_start(False)
                
                # IMPORTANT: update idle baseline to user's new position
                nonlocal idle_base_top
                idle_base_top = page.window.top
                
                delay = await miku_chat(msg="╰(￣ω￣ｏ)", emote=Miku.HAPPY)
                # start_idle_bobbing()
                restart_loop_after_delay(delay)
                
            elif e.type == ft.WindowEventType.BLUR:
                if chance(50):
                    delay = await miku_chat(msg="Are you just going to leave me here? o(≧口≦)o", emote=Miku.AMGRY)
                else:
                    miku.set_state(Miku.AMGRY)
                    
                await to_front_with_delay()
                restart_loop_after_delay(delay)
                
            elif e.type == ft.WindowEventType.FOCUS and not is_miku_chatting:
                delay = await miku_chat(msg="Hi! q(≧▽≦q)", emote=Miku.JOY)
                restart_loop_after_delay(delay)
        
        if e.type == ft.WindowEventType.CLOSE:
            await exit_miku()
            
        if not open_menu:
            await window_interactions(e)

        check_and_adjust_bounds(page)

    async def on_drag_start(_) -> None:
        nonlocal exit_app
        if exit_app:
            return
        exit_app = False
        miku.set_pan_start(True)
        
        if not open_menu:
            await miku_chat(*rnd_miku_chat([
                ("Where we going? o((>ω< ))o", Miku.ECSTATIC),
                ("Weeeee \\(≧▽≦)/", Miku.ECSTATIC),
                ("P-please be gentle... (*/ω＼*)", Miku.PONDER),
                ("You can place me in any monitor space! ヾ(•ω•`)o", Miku.GLASSES),
            ]), duration=0)

    def on_enter(_) -> None: # User hovers over Miku
        if not (
            open_menu or is_miku_chatting
            or miku.is_pan_start() or exit_app
        ):
            miku.set_state(Miku.READY)

    def on_exit(_) -> None: # Default state for Miku
        if not (
            miku.is_pan_start() or stop_event.is_set()
            or exit_app or open_menu or is_miku_chatting
        ):
            miku.set_state(Miku.NEUTRAL)
    
    async def on_tap_down(e: ft.TapEvent):
        nonlocal interaction_increment, interaction_timer, exit_app
        if exit_app:
            return
        delay: float = 2
        local_position: ft.Offset = e.local_position
        stop_movement_loop()
        exit_app = False
        
        if not open_menu and not miku.is_pan_start():
            if is_within_radius(center=ft.Offset(x=141.0, y=210.0), point=local_position, radius=40):
                # print(interaction_increment)
                if not interaction_increment >= 5:
                    if interaction_timer is None:
                        interaction_timer = ResettableTimer(delay)
                    
                    interaction_timer.start()
                    
                    delay = await miku_chat(msg="W-what are you doing?! ヽ（≧□≦）ノ", emote=Miku.SHOCK)
                    interaction_increment += 1
                    
                    if await interaction_timer.expired.wait():
                        interaction_increment = 0
                        
                else:
                    await interaction_timer.expired.wait()
                    delay = await miku_chat(msg="Grr, I've had enough! (* ￣︿￣)", emote=Miku.AMGRY, duration=0)
                    await asyncio.sleep(delay)
                    await exit_miku(chat=False)
                    return
                
            elif is_within_radius(center=ft.Offset(x=121.0, y=135.0), point=local_position, radius=50):
                delay = await miku_chat(*rnd_miku_chat([
                    ("I-I do like h-headpats (≧﹏ ≦)", Miku.PONDER),
                    ("Hehehe~ (p≧w≦q)", Miku.ECSTATIC),
                    ("Headpats? Yippee q(≧▽≦q)", Miku.ECSTATIC),
                    ("I-I don't mind h-headpats\n(≧﹏ ≦)", Miku.PONDER),
                ]))
                
            else:
                delay = await miku_chat()
            restart_loop_after_delay(delay)
        else:
            await miku_chat(msg="Welcome to the menu! What do you want to do? o(*￣︶￣*)o", emote=Miku.HAPPY)
        
    
    # TODO: Finish implementing a menu
    async def on_double_tap(_) -> None:
        nonlocal open_menu
        if exit_app:
            return
        height_increase = 0
        width_increase = 400
        
        print(f"{"Opening" if not open_menu else "Closing"} the menu!")
        menu = default_menu("o(*≧▽≦)ツ┏━┓ What to do?")
        
        if not open_menu:
            stop_idle_bobbing()
            stop_movement_loop()
            page.window.height += height_increase
            page.window.width += width_increase
            page.window.top -= height_increase
            menu_column.controls.append(menu)
            page.update()
            
        else:
            menu_column.controls.clear()
            start_idle_bobbing()
            page.window.height -= height_increase
            page.window.width -= width_increase
            page.window.top += height_increase
            page.update()
            restart_loop_after_delay(await miku_chat())
        
        open_menu = not open_menu

    async def on_secondary_tap(_) -> None: # When user right-clicks (or secondary) Miku
        nonlocal exit_timer, exit_app, disable, form
        delay: float = 2
        
        if disable:
            form.disabled = disable
            form.update()
            return
        if exit_app:
            disable = True
            if exit_timer:
                exit_timer.cancel()
            await exit_miku()
            return
            
        exit_app = True
        delay = await miku_chat(
            msg="Right-click me again if you want me to leave... ~(>_<。)\\", 
            emote=Miku.PONDER)
        
        if exit_timer is None:
            exit_timer = ResettableTimer(delay)
        
        exit_timer.start()
            
        stop_movement_loop()
        restart_loop_after_delay(delay)
        
        await exit_timer.expired.wait()
        exit_app = False
    
    async def on_close(_):
        debug_msg("Window has been closed manually!", debug=debug)
        await exit_miku()
    
    # -------- Events --------
    async def cleanup_then_exit() -> None:
        nonlocal interaction_timer, exit_timer
        
        debug_msg("Window closing... Cleaning up tasks.", debug=debug)
        
        interaction_timer = None
        exit_timer = None
        for task in [movement_task, restart_timer, speech_timer, idle_task]:
            await await_task_completion(task)
        
        page.window.prevent_close = False
        page.window.update()
        await asyncio.sleep(0.1)
        try:
            await page.window.close()
        except:
            print("There was an error closing the app... Anyways...")
            pass
    
    async def exit_miku(chat: bool = True) -> None:
        delay: float = 1
        
        if open_menu:
            menu_column.controls.clear()
            page.window.width -= 400
            page.update()
        
        if chat:
            delay = await miku_chat(*rnd_miku_chat([
                ("\'Til next time! ヽ（≧□≦）ノ", Miku.HAPPY),
                ("Don't forget about me! (≧﹏ ≦)", Miku.AMGRY),
                ("I'm going to miss you... 〒▽〒", Miku.PONDER),
                ("Don't forget to review!\nヾ(≧▽≦*)o", Miku.ECSTATIC),
            ]))
            
        stop_movement_loop()
        debug_msg("Bye bye...", handler="Miku", debug=debug)
        
        delay_in_ms = int(delay * 1000)
        print(f"Closing up after {delay_in_ms}ms ({delay}s)...")
        miku_img.animate_rotation = ft.Animation(delay_in_ms, ft.AnimationCurve.EASE_IN_OUT_CUBIC)
        miku_img.animate_opacity = ft.Animation(delay_in_ms, ft.AnimationCurve.EASE_IN_OUT)
        miku_img.animate_scale = ft.Animation(delay_in_ms, ft.AnimationCurve.EASE_IN_OUT)
        miku_img.update()
        await asyncio.sleep(0.1)
        miku_img.rotate = ft.Rotate(math.pi * 2)
        miku_img.opacity = 0
        miku_img.scale = 0
        miku_img.update()
        
        stop_idle_bobbing()
        await asyncio.sleep(delay)
        await cleanup_then_exit()
        
    # -------- Setup Miku --------
    miku = DynamicMiku(Miku.NEUTRAL, debug=False)
    miku_img = miku.get_image()
    miku_img.animate_rotation = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    miku_img.animate_scale = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    miku_img.animate_opacity = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    miku_img.rotate = 0
    miku_img.scale = 0
    miku_img.opacity = 0
    
    menu_column = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True,
        alignment=ft.MainAxisAlignment.CENTER
    )
    menu_container = ft.Container(
        content=menu_column, alignment=ft.Alignment.CENTER,
        expand=True
    )
    
    miku_row = ft.Row(
        controls=[miku_img, menu_container], alignment=ft.MainAxisAlignment.START,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    miku_column = ft.Column(
        controls=[miku_row], expand=False,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.END
    )
    
    speech_column = ft.Column(
        controls=[speech_bubble],
        horizontal_alignment=ft.CrossAxisAlignment.START,
        alignment=ft.MainAxisAlignment.START, expand=False
    )
    
    miku_stack = ft.Stack(
        controls=[miku_column, speech_column],
        alignment=ft.Alignment.CENTER,
        expand=True,
    )
    
    miku_container = ft.Container(
        content=miku_stack, expand=True, alignment=ft.Alignment.CENTER
    )
    
    miku_gs = ft.GestureDetector(
        content=miku_container,
        mouse_cursor=ft.MouseCursor.GRAB,
        on_double_tap=on_double_tap,
        on_enter=on_enter,
        on_exit=on_exit,
        on_tap_down=on_tap_down,
        on_secondary_tap=on_secondary_tap,
        expand=True
    )
    
    form = ft.WindowDragArea(
        content=miku_gs, maximizable=False, on_drag_start=on_drag_start,
        expand=True
    )
    
    page.on_keyboard_event = on_keyboard_event
    page.on_close = on_close
    page.window.on_event = on_event
    page.add(form)
    
    check_and_adjust_bounds(page)
    
    # Opening Animation
    await asyncio.sleep(0.1)
    miku_img.scale = 1
    miku_img.opacity = 1
    miku_img.rotate = ft.Rotate(math.pi * 2)
    page.update()
    await asyncio.sleep(1)
    miku_img.animate_scale = None
    miku_img.animate_rotation = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
    miku_img.rotate = 0
    page.update()
    
    # Greetings
    await asyncio.sleep(await miku_chat(*rnd_miku_chat([
        (f"Hello there {get_full_username()}! (｡･∀･)ﾉﾞ", Miku.HAPPY),
        ("Hello, I'm Hatsune Miku! ヾ(•ω•`)o", Miku.HAPPY),
    ])))
    
    start_movement_loop()
    start_idle_bobbing()


if __name__ == "__main__":
    ft.app(target=main_app)