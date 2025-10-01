import flet as ft
import asyncio
import math

from utilities.debug import debug_msg


# -------- Helpers --------
def update_ctrl(ctrl: ft.LayoutControl) -> None:
    if ctrl.page is not None:
        ctrl.update()

# -------- Setups --------
def anim_setup_main(ctrl: ft.LayoutControl) -> None:
    """The animation setup for the main layout control."""
    ctrl.animate_rotation = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    ctrl.animate_scale = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    ctrl.animate_opacity = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    ctrl.rotate = 0
    ctrl.scale = 0
    ctrl.opacity = 0
    
def anim_setup_menu(ctrl: ft.LayoutControl) -> None:
    """The animation setup for a menu layout control."""
    ctrl.animate_offset = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    ctrl.animate_opacity = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    ctrl.animate_scale = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    ctrl.offset = ft.Offset(x=0.0, y=1.0)
    ctrl.opacity = 0
    ctrl.scale = 0

# -------- Animation Seqeuences --------
async def opening_animation(ctrl: ft.LayoutControl) -> None:
    """Application opening animation sequence for the main layout control."""
    await asyncio.sleep(0.1)
    ctrl.scale = 1
    ctrl.opacity = 1
    ctrl.rotate = ft.Rotate(math.pi * 2)
    update_ctrl(ctrl)
    await asyncio.sleep(1)
    ctrl.animate_scale = None
    ctrl.animate_rotation = ft.Animation(500, ft.AnimationCurve.EASE_IN_OUT)
    ctrl.rotate = 0
    update_ctrl(ctrl)
    
async def exit_animation(ctrl: ft.LayoutControl, delay: float, debug: bool = False) -> None:
    """Application exit animation sequence for the main layout control."""
    delay_in_ms = int(delay * 1000)
    debug_msg(f"Exiting app after animation finishes in {delay_in_ms}ms ({delay}s).", debug=debug)
    ctrl.animate_rotation = ft.Animation(delay_in_ms, ft.AnimationCurve.EASE_IN_OUT_CUBIC)
    ctrl.animate_opacity = ft.Animation(delay_in_ms, ft.AnimationCurve.EASE_IN_OUT)
    ctrl.animate_scale = ft.Animation(delay_in_ms, ft.AnimationCurve.EASE_IN_OUT)
    update_ctrl(ctrl)
    await asyncio.sleep(0.1)
    ctrl.rotate = ft.Rotate(math.pi * 2)
    ctrl.opacity = 0
    ctrl.scale = 0
    update_ctrl(ctrl)
    
async def show_menu_animation(ctrl: ft.LayoutControl, duration: float = 1):
    """Animates a menu layout control with `duration`."""
    ctrl.visible = True
    update_ctrl(ctrl)
    await asyncio.sleep(0.1)
    ctrl.offset = ft.Offset(x=0.0, y=0.0)
    ctrl.opacity = 1
    ctrl.scale = 1
    update_ctrl(ctrl)
    await asyncio.sleep(duration)
    
async def exit_menu_animation(ctrl: ft.LayoutControl, duration: float = 1):
    """Animates a menu layout control with `duration`. Returns used `duration`."""
    ctrl.offset = ft.Offset(x=0.0, y=1.0)
    ctrl.opacity = 0
    ctrl.scale = 0
    update_ctrl(ctrl)
    await asyncio.sleep(duration)
    ctrl.visible = False
    update_ctrl(ctrl)