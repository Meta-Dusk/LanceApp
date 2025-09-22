import flet as ft
import screeninfo

def main(page: ft.Page):
    def check_and_adjust_bounds(_):
        try:
            monitors = screeninfo.get_monitors()
            if not monitors:
                return
            
            # Assume primary monitor; adjust for multi-monitor if needed
            screen = monitors[0]
            screen_width = screen.width
            screen_height = screen.height
            
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
        except Exception as ex:
            print(f"Error adjusting bounds: {ex}")
    
    page.window.on_event = check_and_adjust_bounds
    
    # Example UI
    page.add(ft.ElevatedButton("Snap to Bounds", on_click=check_and_adjust_bounds))
    page.add(ft.Text("Drag the window off-screen and click to fix."))

ft.app(main)