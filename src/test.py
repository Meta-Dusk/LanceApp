import flet as ft

import screeninfo
import time

from typing import Optional


def get_all_monitors():
    try:
        return screeninfo.get_monitors()
    except Exception as e:
        print("Error detecting monitors:", e)
        return []


def get_monitor_for_window(left: float, top: float, width: float, height: float) -> Optional[screeninfo.Monitor]:
    """Return the monitor where the window is located (largest overlap)."""
    monitors = get_all_monitors()
    if not monitors:
        return None

    best_monitor = None
    best_area = 0
    win_rect = (left, top, left + width, top + height)

    for m in monitors:
        mon_rect = (m.x, m.y, m.x + m.width, m.y + m.height)

        # compute intersection
        ix1 = max(win_rect[0], mon_rect[0])
        iy1 = max(win_rect[1], mon_rect[1])
        ix2 = min(win_rect[2], mon_rect[2])
        iy2 = min(win_rect[3], mon_rect[3])

        if ix1 < ix2 and iy1 < iy2:  # overlap exists
            area = (ix2 - ix1) * (iy2 - iy1)
            if area > best_area:
                best_area = area
                best_monitor = m

    return best_monitor


def clamp_to_monitor(m: screeninfo.Monitor, left: float, top: float, width: float, height: float):
    """Clamp window inside given monitor."""
    max_left = m.x + m.width - width
    max_top = m.y + m.height - height
    clamped_left = max(m.x, min(left, max_left))
    clamped_top = max(m.y, min(top, max_top))
    return int(clamped_left), int(clamped_top)


def test(page: ft.Page):
    DEBUG = True
    
    page.bgcolor = ft.Colors.TRANSPARENT
    page.padding = 0

    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.window.title_bar_hidden = True
    page.window.always_on_top = True
    page.window.frameless = True
    page.window.resizable = False
    page.window.width = 258
    page.window.height = 210
    page.decoration = ft.BoxDecoration(border_radius=10, border=ft.border.all(2, ft.Colors.PRIMARY)) if DEBUG else None

    # Place window on primary monitor bottom center
    monitors = get_all_monitors()
    if monitors:
        primary = monitors[0]
        page.window.left = primary.x + (primary.width - page.window.width) / 2
        page.window.top = primary.y + primary.height - page.window.height

    def check_and_adjust_bounds(e=None):
        m = get_monitor_for_window(
            page.window.left, page.window.top, page.window.width, page.window.height
        )
        if not m:
            return

        clamped_left, clamped_top = clamp_to_monitor(
            m, page.window.left, page.window.top, page.window.width, page.window.height
        )
        if clamped_left != page.window.left or clamped_top != page.window.top:
            page.window.left, page.window.top = clamped_left, clamped_top
            page.update()

    def movement(e: ft.KeyboardEvent):
        step = 20
        if e.key == "D":
            miku_img.data["flipped"] = False
            page.window.left += step
        elif e.key == "A":
            miku_img.data["flipped"] = True
            page.window.left -= step

        miku_img.scale = ft.Scale(scale_x=-1 if miku_img.data["flipped"] else 1)
        check_and_adjust_bounds()
        page.update()

    def on_event(e: ft.WindowEvent):
        if e.type == ft.WindowEventType.MOVED:
            miku_img.src = "images/miku_states/miku_neutral.png"
            miku_img.data["pan_start"] = False
        elif e.type == ft.WindowEventType.BLUR:
            miku_img.src = "images/miku_states/miku_amgry.png"
        check_and_adjust_bounds()

    def on_pan_start(_):
        miku_img.data["pan_start"] = True
        miku_img.src = "images/miku_states/miku_ecstatic.png"
        miku_img.update()

    def on_enter(_):
        miku_img.src = "images/miku_states/miku_ready.png"
        miku_img.update()

    def on_exit(_):
        if not miku_img.data["pan_start"]:
            miku_img.src = "images/miku_states/miku_neutral.png"
            miku_img.update()

    def on_tap(_):
        miku_img.src = "images/miku_states/miku_ponder.png"
        miku_img.update()

    def on_double_tap(_):
        bye_bye_miku.opacity = 1
        miku_img.opacity = 0
        page.update()
        bye_bye_miku.scale = 0
        bye_bye_miku.rotate = ft.Rotate(-1)
        page.update()
        time.sleep(1)
        page.window.close()

    miku_img = ft.Image(
        src="images/miku_states/miku_neutral.png",
        fit=ft.ImageFit.FILL,
        gapless_playback=True,
        anti_alias=False,
        error_content=ft.Container(
            ft.Text("No Miku :(", color=ft.Colors.ERROR),
            bgcolor=ft.Colors.ERROR_CONTAINER,
            border_radius=20,
            padding=5,
            alignment=ft.alignment.center,
        ),
        expand=True,
        data={"flipped": False, "pan_start": False},
        animate_opacity=ft.Animation(0),
    )
    bye_bye_miku = ft.Image(
        src="images/miku_states/miku_amgry.png",
        fit=ft.ImageFit.FILL,
        gapless_playback=True,
        anti_alias=False,
        error_content=ft.Container(
            ft.Text("No Miku :(", color=ft.Colors.ERROR),
            bgcolor=ft.Colors.ERROR_CONTAINER,
            border_radius=20,
            padding=5,
            alignment=ft.alignment.center,
        ),
        expand=True,
        animate_scale=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        animate_rotation=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        opacity=0,
        animate_opacity=ft.Animation(0),
    )
    miku_stack = ft.Stack(controls=[bye_bye_miku, miku_img], alignment=ft.alignment.center)

    gs = ft.GestureDetector(
        content=miku_stack,
        on_double_tap=on_double_tap,
        on_enter=on_enter,
        on_exit=on_exit,
        on_tap=on_tap,
        mouse_cursor=ft.MouseCursor.MOVE,
    )
    form = ft.WindowDragArea(content=gs, maximizable=False, on_pan_start=on_pan_start)

    page.window.on_event = on_event
    page.on_keyboard_event = movement
    page.add(form)
    check_and_adjust_bounds()
    page.update()


if __name__ == "__main__":
    ft.app(target=test)
