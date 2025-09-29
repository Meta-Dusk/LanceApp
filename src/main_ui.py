import flet as ft
import random, asyncio, math

from typing import Optional, Tuple
from setup import set_win_pos_bc, before_main_app
from chats import (
    CHAT_GREETINGS, EXIT_APP_MSGS, WHEN_HEADPAT_MSGS, WHEN_DRAGGED_MSGS, WHEN_IN_VOID_MSGS,
    WHEN_FED_UP_MSGS, WHEN_FLUSTERED_MSGS, after_dragged_msgs)
from ui.components import default_speech_bubble
from ui.images import DynamicMiku, Miku
from ui.menus import DefaultMenu
from ui.animations import (opening_animation, anim_setup_main, exit_animation, show_menu_animation,
                           exit_menu_animation)
from utilities.data import SPEECH_LINES, random_line
from utilities.timers import ResettableTimer, DeltaTimer
from utilities.tasks import cancel_task, await_task_completion, is_task_done
from utilities.debug import debug_msg
from utilities.helpers import rnd_miku_chat
from utilities.monitor import check_and_adjust_bounds, get_all_monitors
from utilities.math import chance, is_within_radius
from utilities.notifications import preset_help_notif


# TODO: If possible, refactor everything related to Miku into a class for modularity.
async def main_app(page: ft.Page, debug: bool = False):
    """Serves as the `main` of the entire app."""
    # -------- Setup --------
    # Task Flags for Loops
    stop_event = asyncio.Event() # Used to control movement loop only
    restart_timer_task:      Optional[asyncio.Task] = None
    speech_timer_task:       Optional[asyncio.Task] = None
    movement_task:           Optional[asyncio.Task] = None
    movement_animation_task: Optional[asyncio.Task] = None
    idle_task:               Optional[asyncio.Task] = None
    tasks = [restart_timer_task, speech_timer_task, movement_task, movement_animation_task]
    
    ## -- Controls --
    # Defaults
    speech_bubble = default_speech_bubble("")
    
    # Menu Variables
    HEIGHT_INCREASE = 0
    WIDTH_INCREASE  = 400
    
    ## -- Variables --
    # Debug Stuff
    ALLOW_VOID_TRAVERSAL: bool = False
    ENABLE_MV_OVERRIDE:   bool = False
    SHOW_MOVEMENT_LOGS:   bool = False
    SHOW_IDLE_LOGS:       bool = False
    SHOW_CHAT_LOGS:       bool = False
    SHOW_LOOP_LOGS:       bool = False
    SHOW_WINDOW_LOGS:     bool = False
    mv_override_enabled:  bool = False
    exit_app:             bool = False
    open_menu:            bool = False
    is_miku_chatting:     bool = False
    disable:              bool = False
    
    # Movement
    MIKU_MV_FREQ_MS:    Tuple[int, int] = (2000, 3000) # Frequency of randomized Miku movement
    MIKU_MV_STEP:       Tuple[int, int] = (-300, 300)  # Range of randomized Miku movement
    MIKU_RT_MOD:        float = 0.15                   # Rotation modifier for Miku flip
    MIKU_FLIP_CHANCE:   int = 5                        # Chance of Miku flip out of 100%
    MIKU_CHAT_CHANCE:   int = 20                       # Chance for Miku to randomly chat out of 100%
    FPS:                float = 60.0                   # For smooth movement animation
    MINIMUM_ANIM_FRAME: float = 1.0                    # Used for clamping the lowest allowable animation time per frame
    
    # Idle Animation
    idle_phase: float = 0.0         # Bobbing position
    idle_base_top = page.window.top # Baseline for idle bobbing
    IDLE_AMP: float = 4.0           # Pixels up/down (tweak for subtlety)
    
    # Speech Values (in seconds)
    MSG_BASE_TIME: float = 2.0      # Minimum time to display
    PER_CHAR_TIME: float = 0.02     # Tweak speed factor
    
    # Timers for Stuff
    interaction_timer: ResettableTimer = None
    interaction_increment: int = 0
    exit_timer: ResettableTimer = None
    global_timer: DeltaTimer = DeltaTimer(target_fps=FPS)
    
    # -------- Window Functions --------
    async def to_front_with_delay(delay: float = 1):
        """Sets the window to be `always_on_top` for a duration given by `delay`."""
        debug_msg(f"Bringing Miku to the front for {delay}s", debug=SHOW_WINDOW_LOGS)
        page.window.always_on_top = True
        await asyncio.sleep(delay)
        page.window.always_on_top = False
        debug_msg("Brought Miku to the front.", debug=SHOW_WINDOW_LOGS)
    
    # -------- Task Helpers --------
    def start_movement_loop() -> None:
        """Starts Movement Loop"""
        nonlocal movement_task
        cancel_task(movement_animation_task)
        if cancel_task(movement_task):
            debug_msg("Restarting movement loop", debug=SHOW_MOVEMENT_LOGS)
        else:
            debug_msg("Starting movement loop", debug=SHOW_MOVEMENT_LOGS)
        stop_event.clear()
        movement_task = asyncio.create_task(coro=movement_loop(), name="start_movement_loop -> movement_loop")
        
    def stop_movement_loop() -> None:
        """Stops movement loop."""
        stop_event.set()
        cancel_task(movement_animation_task)
        if cancel_task(movement_task):
            debug_msg("Stopping movement loop", debug=SHOW_MOVEMENT_LOGS)
        else:
            debug_msg("Movement loop already stopped", debug=SHOW_MOVEMENT_LOGS)
            
    def restart_loop_after_delay(delay: Optional[float] = 2.0) -> None:
        """Restarts the movement loop after a `delay`. If `delay <= 0` then cancel, and `delay` is in seconds."""
        nonlocal restart_timer_task
        if cancel_task(restart_timer_task):
            debug_msg(msg="Cancelled previous restart_timer_task", handler="delayed_restart", debug=SHOW_LOOP_LOGS)
        stop_movement_loop()
        
        if delay <= 0:
            debug_msg(f"Cancelling restart loop since delay={delay}", debug=SHOW_LOOP_LOGS)
            return
        
        debug_msg(f"Waiting for {delay}s before restarting loop.", debug=SHOW_LOOP_LOGS)
        
        async def delayed_restart():
            """Starts movement loop after `delay` and also resets Miku to her `Neutral` state."""
            await asyncio.sleep(delay)
            if miku.is_pan_start():
                return
            debug_msg(msg="Setting Miku to Neutral", handler="delayed_restart", debug=SHOW_LOOP_LOGS)
            miku.set_state(Miku.NEUTRAL)
            start_movement_loop()
        
        if delay is None:
            start_movement_loop()
            return
        
        restart_timer_task = asyncio.create_task(coro=delayed_restart(), name="delay_restart")
        
    # -------- Movement (Smooth OS Window Animation) --------
    async def movement_loop() -> None:
        """Handles the movement loop for Miku."""
        while not stop_event.is_set() and not mv_override_enabled and not open_menu:
            if miku.is_pan_start():
                debug_msg("Stopping Movement Loop :: Miku is being dragged!", debug=SHOW_MOVEMENT_LOGS)
                break
            
            rnd_delay = random.randint(*MIKU_MV_FREQ_MS) / 1000
            debug_msg(f"Sleeping for {rnd_delay}s", handler="MIKU", debug=SHOW_MOVEMENT_LOGS)
            await asyncio.sleep(rnd_delay)
            
            rnd_step = random.randint(*MIKU_MV_STEP)
            debug_msg(
                msg=f"Moving {rnd_step}px to the {"left" if rnd_step < 0 else "right"}.",
                handler="MIKU", debug=SHOW_MOVEMENT_LOGS
            )
            
            if not miku.is_pan_start():
                if chance(MIKU_FLIP_CHANCE):
                    rnd_rotation = math.pi * 2 * math.copysign(1, -rnd_step)
                    await start_smooth_movement(step=rnd_step, rotate=rnd_rotation, base_duration=rnd_delay)
                else:
                    await start_smooth_movement(step=rnd_step, base_duration=rnd_delay)
            await asyncio.sleep(rnd_delay)
            
    async def validate_position(step: int, target_left: ft.Number) -> None:
        """Checks whether the window's position is within the boundaries of a valid monitor."""
        if not check_and_adjust_bounds(page, SHOW_WINDOW_LOGS):
            delay: Optional[float] = 2
            debug_msg("Miku has entered the void!", debug=debug)
            stop_movement_loop()
            stop_idle_bobbing()
            if not ALLOW_VOID_TRAVERSAL:
                debug_msg("Attempting to restore position...", debug=SHOW_WINDOW_LOGS)
                page.window.left += -step * 2
                page.window.update()
            else:
                debug_msg("WARNING! Miku can move past monitor boundaries.", debug=SHOW_WINDOW_LOGS)
                def on_clicked(_) -> None:
                    nonlocal target_left
                    set_win_pos_bc(get_all_monitors(), page)
                    page.window.update()
                    target_left = page.window.left
                    restart_loop_after_delay(delay)
                await preset_help_notif(on_clicked=on_clicked)
            # start_idle_bobbing()
            await miku_chat(*rnd_miku_chat(WHEN_IN_VOID_MSGS))
            print(f"Using delay of {delay}s for restart_loop_after_delay")
            restart_loop_after_delay(delay)
            
        else:
            if chance(MIKU_CHAT_CHANCE):
                await miku_chat()
    
    async def start_smooth_movement(
        step: int, rotate: Optional[float] = None, base_duration: float = 0.2
    ) -> None:
        """Manages proper starting of the `move_miku_smooth` function."""
        nonlocal movement_animation_task
        miku_img.rotate = 0
        miku_img.update()
        if cancel_task(movement_animation_task):
            debug_msg("Cancelled previous smooth movement task", debug=SHOW_MOVEMENT_LOGS)
        else:
            debug_msg("Starting new smooth movement task", debug=SHOW_MOVEMENT_LOGS)
        movement_animation_task = asyncio.create_task(
            coro=move_miku_smooth(step, rotate, base_duration),
            name="start_smooth_movement -> move_miku_smooth"
        )
    
    async def move_miku_smooth(
        step: int, rotate: Optional[float] = None, base_duration: float = 0.2
    ) -> None:
        """Smoothly animate the OS window horizontally with ease-out curve and jiggle."""
        nonlocal idle_base_top
        stop_idle_bobbing()
        if step == 0:
            start_idle_bobbing() # nothing to move; ensure idle is running again
            return
        miku.set_flipped(step < 0) # Flip sprite based on direction
        miku_img.rotate = ft.Rotate(MIKU_RT_MOD * (abs(step) / 100)) if rotate is None else rotate
        miku_img.update()
        duration = base_duration + (abs(step) / 300)  # larger step = slower glide
        start_left = page.window.left                 # Initial window x pos
        target_left = start_left + step               # Target window x pos
        await validate_position(step, target_left)
        JIGGLE_AMP = 3
        elapsed = 0.0
        while elapsed < duration and not miku.is_pan_start():
            dt = await global_timer.tick()
            elapsed += dt
            t = min(MINIMUM_ANIM_FRAME, elapsed / duration)
            eased_t = 1 - (1 - t) ** 3
            new_left = start_left + (step * eased_t)
            jiggle = math.sin(t * math.tau) * JIGGLE_AMP
            new_top = idle_base_top + jiggle
            page.window.left = new_left
            page.window.top = new_top
            page.window.update()
        else:
            idle_base_top = page.window.top
            start_idle_bobbing()
        # Snap to target to avoid drift
        page.window.left = target_left
        page.window.top = round(idle_base_top)  # reset jiggle rounding
        page.window.update()
        idle_base_top = page.window.top # Reset baseline for idle bobbing
        start_idle_bobbing()
        await to_front_with_delay()
        await validate_position(step, target_left)
    
    
    # ---- Idle Bobbing (Independent Lifecycle) ----
    async def idle_bobbing_loop() -> None:
        """Handles the window bobbing animation loop."""
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
        """Starts the window bobbing animation."""
        nonlocal idle_task
        check_task = is_task_done(idle_task)
        if check_task and check_task is not None:
            debug_msg(msg="Idle bobbing already started", handler="MIKU", debug=SHOW_IDLE_LOGS)
            return
        debug_msg(msg="Idle bobbing started", handler="MIKU", debug=SHOW_IDLE_LOGS)
        idle_task = asyncio.create_task(coro=idle_bobbing_loop(), name="start_idle_bobbing -> idle_bobbing_loop")

    def stop_idle_bobbing() -> None:
        """Stops the window bobbing animation."""
        nonlocal idle_task
        if cancel_task(idle_task):
            debug_msg(msg="Idle bobbing stopped", handler="MIKU", debug=SHOW_IDLE_LOGS)
            idle_task = None
        else:
            debug_msg(msg="Idle bobbing already stopped", handler="MIKU", debug=SHOW_IDLE_LOGS)
    
    # -------- Speech Feature --------
    async def remove_speech(delay: Optional[float] = None) -> None:
        """Animate speech bubble exit animation and wait for it to finish."""
        nonlocal speech_bubble, is_miku_chatting
        if delay and delay > 0:
            await asyncio.sleep(delay)
            speech_bubble.opacity = 0
            speech_bubble.offset = ft.Offset(x=0.0, y=1.0)
            speech_bubble.update()
            await asyncio.sleep(0.2)
            miku.set_state(Miku.NEUTRAL)
            is_miku_chatting = False
    
    async def miku_chat(msg: Optional[str] = None, emote: Optional[Miku] = None, duration: Optional[float] = None) -> float:
        """
        Make Miku say something in a speech bubble.
        Set `duration <= 0` if the message shouldn't expire.
        Set `duration` to `None` if it should use a dynamic duration.
        
        Args:
            msg (str | None): The message that Miku will say.
            emote (Miku | None): Takes a `Miku` class object, for setting her expressions.
            duration (float | None): The duration of how long the message will show.
        
        Returns:
            float: The `duration` used for displaying the message.
        """
        nonlocal speech_bubble, speech_timer_task, is_miku_chatting
        is_miku_chatting = True
        random_chat = random_line(SPEECH_LINES)
        chat: str = random_chat["text"]
        emotion: str = random_chat["emotion"]
        
        # Dynamic duration fallback
        if duration is None:
            dynamic_duration = MSG_BASE_TIME + PER_CHAR_TIME * len(chat)
            duration = round(dynamic_duration, 3)
            
        if cancel_task(speech_timer_task):
            debug_msg(msg="Cancelled previous speech timer", handler="CHAT", debug=SHOW_CHAT_LOGS)
        else:
            debug_msg(msg=f"Starting new speech timer with {duration}s", handler="CHAT", debug=SHOW_CHAT_LOGS)
        
        if msg is None and emote:
            debug_msg(msg="Using a random line for the message", handler="CHAT", debug=SHOW_CHAT_LOGS)
        elif msg and emote is None:
            debug_msg(msg="Using a random emote for the message", handler="CHAT", debug=SHOW_CHAT_LOGS)
        elif msg is None and emote is None:
            debug_msg(msg="Generating a random chat from list", handler="CHAT", debug=SHOW_CHAT_LOGS)
        else:
            debug_msg(msg="Using provided params for the message", handler="CHAT", debug=SHOW_CHAT_LOGS)
        
        miku.set_state(getattr(Miku, emotion.upper(), emotion) if emote is None else emote)
        speech_text: ft.Text = speech_bubble.content
        speech_text.value = chat if msg is None else msg
        speech_bubble.offset = ft.Offset(x=0.0, y=0.0)
        speech_bubble.opacity = 1
        speech_bubble.update()
        asyncio.create_task(asyncio.sleep(0.2))
        start_idle_bobbing() # ensure idle is running (idempotent) (Mr. GPT truly out here with technical jargon)
        debug_msg(f"Miku's chat will be shown {f"for {duration}s" if duration > 0 else "indefinitely"}.", debug=SHOW_CHAT_LOGS)
        if duration > 0:
            speech_timer_task = asyncio.create_task(coro=remove_speech(duration), name="miku_chat -> remove_speech")
        else:
            speech_timer_task = None
        return duration

    # -------- Event Handlers --------
    async def on_keyboard_event(e: ft.KeyboardEvent) -> None:
        nonlocal mv_override_enabled
        if exit_app:
            return
        # print(f"Detected key press: {e.key}")
        if e.key == "`" and ENABLE_MV_OVERRIDE:
            mv_override_enabled = not mv_override_enabled
            if mv_override_enabled:
                stop_movement_loop()
                await miku_chat(
                    msg="S-something's wrong... I seem to can't move on my own anymore? (´。＿。｀)",
                    emote=Miku.SHOCK)
            else:
                start_movement_loop()
                await miku_chat(msg="I can move again now! (/≧▽≦)/", emote=Miku.JOY)
        if mv_override_enabled:
            step = 100
            if e.key == "D":
                await start_smooth_movement(step)
            elif e.key == "A":
                await start_smooth_movement(-step)
    
    async def window_interactions(e: ft.WindowEvent) -> None:
        """Various window interactions with Miku."""
        delay: float = 2
        if e.type == ft.WindowEventType.MOVED: # After drag
            # user moved window; update baseline and resume idle
            check_and_adjust_bounds(page, SHOW_WINDOW_LOGS)
            miku.set_pan_start(False)
            
            # IMPORTANT: update idle baseline to user's new position
            nonlocal idle_base_top
            idle_base_top = page.window.top
            delay = await miku_chat(*rnd_miku_chat(after_dragged_msgs(page)))
            
        elif e.type == ft.WindowEventType.BLUR:
            if chance(50):
                delay = await miku_chat(msg="Are you just going to leave me here? o(≧口≦)o", emote=Miku.AMGRY)
            else:
                miku.set_state(Miku.AMGRY)
            await to_front_with_delay()
            
        elif e.type == ft.WindowEventType.FOCUS and not is_miku_chatting:
            delay = await miku_chat(msg="Hi! q(≧▽≦q)", emote=Miku.JOY)
            
        restart_loop_after_delay(delay)
    
    async def on_event(e: ft.WindowEvent) -> None:
        """Handles manual application exit logic."""
        if exit_app:
            return
        if e.type == ft.WindowEventType.CLOSE:
            await exit_miku()
        if not open_menu:
            await window_interactions(e)
        check_and_adjust_bounds(page, SHOW_WINDOW_LOGS)

    async def on_drag_start(_) -> None:
        nonlocal exit_app
        exit_app = False
        miku.set_pan_start(True)
        if exit_app or open_menu:
            return
        await miku_chat(*rnd_miku_chat(WHEN_DRAGGED_MSGS), duration=0)

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
    
    async def on_tap_down(e: ft.TapEvent) -> None:
        nonlocal interaction_increment, interaction_timer, exit_app
        if exit_app or miku.is_pan_start():
            return
        delay: float = 2
        local_position: ft.Offset = e.local_position
        stop_movement_loop()
        exit_app = False
        
        if open_menu:
            delay = await miku_chat(
                msg="Just select an option from the menu. I'll be waiting! ヾ(≧ ▽ ≦)ゝ",
                emote=Miku.HAPPY)
            return
        if is_within_radius(center=ft.Offset(x=141.0, y=210.0), point=local_position, radius=40):
            # print(interaction_increment)
            if not interaction_increment >= 5:
                if interaction_timer is None:
                    interaction_timer = ResettableTimer(delay)
                interaction_timer.start()
                delay = await miku_chat(*rnd_miku_chat(WHEN_FLUSTERED_MSGS))
                interaction_increment += 1
                if await interaction_timer.expired.wait():
                    interaction_increment = 0
                    
            else:
                await interaction_timer.expired.wait()
                delay = await miku_chat(*rnd_miku_chat(WHEN_FED_UP_MSGS), duration=0)
                await asyncio.sleep(delay)
                await exit_miku(chat=False)
                return
            
        elif is_within_radius(center=ft.Offset(x=121.0, y=135.0), point=local_position, radius=50):
            delay = await miku_chat(*rnd_miku_chat(WHEN_HEADPAT_MSGS))
            
        else:
            delay = await miku_chat()
        restart_loop_after_delay(delay)
        
    
    async def close_menu_with_anim() -> None:
        nonlocal miku_img_container, menu_container
        await miku_chat(msg="Closing the menu! o(*￣︶￣*)o", emote=Miku.HAPPY)
        await exit_menu_animation(menu_ctrl)
        miku_img_container.expand = True
        menu_container.visible = False
        page.window.height -= HEIGHT_INCREASE
        page.window.width -= WIDTH_INCREASE
        page.window.top += HEIGHT_INCREASE
    
    async def on_double_tap(_) -> None:
        nonlocal open_menu, menu_container, menu
        if exit_app:
            return
        debug_msg(f"{"Opening" if not open_menu else "Closing"} the menu!", debug=debug)
        open_menu = not open_menu
        if open_menu:
            await miku_chat(msg="Welcome to the menu! What do you want to do? o(*￣▽￣*)ブ", emote=Miku.HAPPY)
            stop_idle_bobbing()
            stop_movement_loop()
            page.window.height += HEIGHT_INCREASE
            page.window.width += WIDTH_INCREASE
            page.window.top -= HEIGHT_INCREASE
            miku_img_container.expand = False
            menu_container.visible = True
            page.update()
            await asyncio.sleep(0.1)
            await show_menu_animation(menu_ctrl)
        else:
            await close_menu_with_anim()
            start_idle_bobbing()
            restart_loop_after_delay(await miku_chat())
            page.update()

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
        """
        Attempts to cancel any running tasks in the background, then exits the app with an animation.
        """
        nonlocal interaction_timer, exit_timer
        debug_msg("Window closing... Cleaning up tasks.", debug=debug)
        interaction_timer = None
        exit_timer = None
        for task in tasks:
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
            await close_menu_with_anim()
        if chat:
            delay = await miku_chat(*rnd_miku_chat(EXIT_APP_MSGS))
        stop_movement_loop()
        debug_msg(msg="Bye bye...", handler="MIKU", debug=debug)
        await exit_animation(miku_img, delay, debug)
        stop_idle_bobbing()
        await asyncio.sleep(delay)
        await cleanup_then_exit()
        
    # -------- Setup Miku --------
    miku = DynamicMiku(Miku.NEUTRAL, debug=False)
    miku_img = miku.get_image()
    anim_setup_main(miku_img)
    
    miku_img_container = ft.Container(
        content=miku_img, padding=10, alignment=ft.Alignment.BOTTOM_LEFT,
        expand=True
    )
    
    menu = DefaultMenu("-- Action Menu --\nSelect any option from below to try!")
    menu.add_button("Exit Miku", lambda _: asyncio.create_task(coro=exit_miku(), name="Exit Miku -> exit_miku()"))
    menu.add_button("Make Miku Yap", lambda _: asyncio.create_task(coro=miku_chat(), name="Make Miku Yap -> miku_chat()"))
    menu_ctrl = menu.build()
    menu_column = ft.Column(
        controls=[menu_ctrl], expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    menu_container = ft.Container(
        content=menu_column, alignment=ft.Alignment.CENTER,
        expand=True, visible=False
    )
    
    miku_row = ft.Row(
        controls=[miku_img_container, menu_container], alignment=ft.MainAxisAlignment.START,
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
        alignment=ft.MainAxisAlignment.START
    )
    
    miku_stack = ft.Stack(
        controls=[miku_column, speech_column],
        alignment=ft.Alignment.CENTER, expand=True,
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
    
    if not debug: # Temporary solution for stretching during launch
        page.decoration = ft.BoxDecoration(border_radius=10, border=ft.Border.all(2, ft.Colors.PRIMARY))
        page.update()
        await asyncio.sleep(0.1)
        page.decoration = None
        page.update()
    
    check_and_adjust_bounds(page, SHOW_WINDOW_LOGS)
    debug_msg("...And Hatsune Miku enters the screen!", debug=debug)
    await opening_animation(miku_img)
    restart_loop_after_delay(await miku_chat(*rnd_miku_chat(CHAT_GREETINGS)))


if __name__ == "__main__":
    ft.run(main=main_app, before_main=before_main_app)