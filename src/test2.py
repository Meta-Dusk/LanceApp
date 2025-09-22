import flet as ft
import screeninfo
import asyncio
import random
from typing import Optional, Tuple


def get_primary_monitor() -> Optional[screeninfo.Monitor]:
    try:
        monitors = screeninfo.get_monitors()
        return monitors[0] if monitors else None
    except Exception as e:
        print("get_primary_monitor error:", e)
        return None


def get_monitor_bounds() -> Tuple[int, int, int, int]:
    m = get_primary_monitor()
    if not m:
        return 0, 0, 1920, 1080
    return int(getattr(m, "x", 0)), int(getattr(m, "y", 0)), int(m.width), int(m.height)


def clamp_window(page: ft.Page, left: float, top: float) -> Tuple[int, int]:
    mx, my, mw, mh = get_monitor_bounds()
    max_left = mx + mw - page.window.width
    max_top = my + mh - page.window.height
    clamped_left = max(mx, min(left, max_left))
    clamped_top = max(my, min(top, max_top))
    return int(clamped_left), int(clamped_top)


def set_flip(img: ft.Image, flipped: bool):
    img.data["flipped"] = bool(flipped)
    img.scale = ft.Scale(scale_x=-1 if flipped else 1)


def test(page: ft.Page):
    if page.data is None:
        page.data = {}

    # Window config
    page.bgcolor = ft.Colors.TRANSPARENT
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.window.title_bar_hidden = True
    page.window.frameless = True
    page.window.always_on_top = True
    page.window.resizable = False
    page.window.width = 258
    page.window.height = 210

    # Place at bottom center
    monitor = get_primary_monitor()
    if monitor:
        page.window.left = int(monitor.x + (monitor.width - page.window.width) / 2)
        page.window.top = int(monitor.y + monitor.height - page.window.height)

    # Image
    miku_img = ft.Image(
        src="images/miku_states/miku_neutral.png",
        fit=ft.ImageFit.FILL,
        expand=True,
        data={"flipped": False, "is_dragging": False},
    )
    set_flip(miku_img, False)

    # Keyboard movement
    def movement(e: ft.KeyboardEvent):
        step = 20
        if e.key == "D":
            set_flip(miku_img, False)
            page.window.left += step
        elif e.key == "A":
            set_flip(miku_img, True)
            page.window.left -= step
        page.update()

    page.on_keyboard_event = movement

    # --- Dragging using GestureDetector, clamping handled by window.on_event ---
    def on_pan_start(_):
        miku_img.data["is_dragging"] = True

    def on_pan_update(e: ft.DragUpdateEvent):
        if not miku_img.data.get("is_dragging"):
            return
        page.window.left += e.delta_x
        page.window.top += e.delta_y
        if e.delta_x < 0:
            set_flip(miku_img, True)
        elif e.delta_x > 0:
            set_flip(miku_img, False)
        page.update()

    def on_pan_end(_):
        miku_img.data["is_dragging"] = False

    # --- Double click closes window ---
    def on_double_tap(_):
        auto_task = page.data.get("auto_task")
        if auto_task and not auto_task.done():
            auto_task.cancel()
        page.window.close()

    gs = ft.GestureDetector(
        content=ft.Column([miku_img], expand=True),
        on_double_tap=on_double_tap,
        on_pan_start=on_pan_start,
        on_pan_update=on_pan_update,
        on_pan_end=on_pan_end,
    )
    page.add(gs)

    # --- Clamp via window.on_event ---
    def on_window_event(e: ft.WindowEvent):
        if e.data and e.data.get("event") == "moved":
            left, top = clamp_window(page, page.window.left, page.window.top)
            if left != page.window.left or top != page.window.top:
                page.window.left = left
                page.window.top = top
                page.update()

    page.window.on_event = on_window_event

    # --- Auto move background task ---
    async def auto_move(page: ft.Page, img: ft.Image):
        direction = random.choice([-1, 1])
        try:
            while True:
                if not img.data.get("is_dragging", False):
                    step = random.randint(1, 10)
                    page.window.left += direction * step
                    set_flip(img, direction < 0)
                    page.update()

                    mx, my, mw, mh = get_monitor_bounds()
                    if page.window.left + page.window.width >= mx + mw:
                        direction = -1
                    elif page.window.left <= mx:
                        direction = 1

                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            return

    page.data["auto_task"] = page.run_task(auto_move, page, miku_img)


if __name__ == "__main__":
    ft.app(target=test)
