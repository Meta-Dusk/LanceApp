import flet as ft

import screeninfo
import time


def get_primary_monitor():
    try:
        monitors = screeninfo.get_monitors()
        if monitors:
            return monitors[0]  # Primary monitor
        else:
            print("No monitors detected")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test(page: ft.Page):
    page.bgcolor = ft.Colors.TRANSPARENT
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0
    
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.window.title_bar_hidden = True
    page.window.frameless = True
    page.window.always_on_top = True
    page.window.resizable = False
    page.window.width = 258
    page.window.height = 210
    
    # Get monitor and set initial bottom-center position
    monitor = get_primary_monitor()
    if monitor:
        page.window.left = (monitor.width - page.window.width) / 2
        page.window.top = monitor.height - page.window.height
    
    def check_and_adjust_bounds(e=None):
        monitor = get_primary_monitor()
        if not monitor:
            return
        
        screen_width = monitor.width
        screen_height = monitor.height
        
        win_left = page.window.left
        win_top = page.window.top
        win_width = page.window.width
        win_height = page.window.height
        
        # Detect and correct clipping
        if win_left < 0:
            page.window.left = 0
        if win_top < 0:
            page.window.top = 0
        if win_left + win_width > screen_width:
            page.window.left = screen_width - win_width
        if win_top + win_height > screen_height:
            page.window.top = screen_height - win_height
        
        page.update()
    
    def movement(e: ft.KeyboardEvent):
        step = 20  # Pixels to move per key press; adjust as needed
        
        if e.key == "D":
            miku_img.data["flipped"] = False
            page.window.left += step
        if e.key == "A":
            miku_img.data["flipped"] = True
            page.window.left -= step
        
        if miku_img.data["flipped"]:
            miku_img.scale = ft.Scale(scale_x=-1)
        else:
            miku_img.scale = ft.Scale(scale_x=1)
        
        print(miku_img.data)
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
        # time.sleep(0.1)
        bye_bye_miku.scale = 0
        bye_bye_miku.rotate = ft.Rotate(-1)
        page.update()
        time.sleep(1)
        page.window.close()
    
    miku_img = ft.Image(
        src="images/miku_states/miku_neutral.png", fit=ft.ImageFit.FILL, gapless_playback=True,
        anti_alias=False, error_content=ft.Container(
            ft.Text("No Miku :(", color=ft.Colors.ERROR), bgcolor=ft.Colors.ERROR_CONTAINER,
            border_radius=20, padding=5, alignment=ft.alignment.center
        ), expand=True, data={"flipped": False, "pan_start": False},
        animate_opacity=ft.Animation(0)
    )
    bye_bye_miku = ft.Image(
        src="images/miku_states/miku_amgry.png", fit=ft.ImageFit.FILL, gapless_playback=True,
        anti_alias=False, error_content=ft.Container(
            ft.Text("No Miku :(", color=ft.Colors.ERROR), bgcolor=ft.Colors.ERROR_CONTAINER,
            border_radius=20, padding=5, alignment=ft.alignment.center
        ), expand=True,
        animate_scale=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        animate_rotation=ft.Animation(1000, ft.AnimationCurve.EASE_IN_OUT),
        opacity=0, animate_opacity=ft.Animation(0)
    )
    miku_stack = ft.Stack(
        controls=[bye_bye_miku, miku_img], alignment=ft.alignment.center
    )
    
    gs = ft.GestureDetector(
        content=miku_stack, on_double_tap=on_double_tap,
        on_enter=on_enter, on_exit=on_exit, on_tap=on_tap,
        mouse_cursor=ft.MouseCursor.MOVE
    )
    form = ft.WindowDragArea(content=gs, maximizable=False, on_pan_start=on_pan_start)
    
    page.window.on_event = on_event
    page.on_keyboard_event = movement
    page.add(form)
    check_and_adjust_bounds()  # Initial bounds check
    page.update()


if __name__ == "__main__":
    ft.app(target=test)