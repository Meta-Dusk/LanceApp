import flet as ft

import asyncio
import math


# -------- Setups --------
def set_initial_animations(miku_img: ft.Image) -> None:
    """Animations setup for Miku."""
    miku_img.animate_rotation = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    miku_img.animate_scale = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    miku_img.animate_opacity = ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
    miku_img.rotate = 0
    miku_img.scale = 0
    miku_img.opacity = 0

# -------- Animation Seqeuences --------
async def opening_animation(page: ft.Page, miku_img: ft.Image) -> None:
    """The application opening animation sequence for Miku."""
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
    
async def exit_animation(miku_img: ft.Image, delay: float) -> None:
    """The application exit animation sequence for Miku."""
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