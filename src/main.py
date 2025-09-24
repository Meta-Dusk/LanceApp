import flet as ft

from main_ui import main_app
from setup import before_main_app


DEBUG = False


async def initial_test(page: ft.Page):
    page.title = "Test"
    page.window.width = 500
    page.window.height = 200
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    await page.window.center()
    
    counter = ft.Text("0", size=50, data=0)

    def increment_click(_):
        counter.data += 1
        counter.value = str(counter.data)
        counter.update()
    
    def detect_key_press(e: ft.KeyboardEvent):
        print(f"Key pressed: {e.key}")
    
    page.on_keyboard_event = detect_key_press
    page.floating_action_button = ft.FloatingActionButton(icon=ft.Icons.ADD, on_click=increment_click)
    page.add(
        ft.SafeArea(
            ft.Container(
                counter,
                alignment=ft.Alignment.CENTER,
            ),
            expand=True,
        )
    )


async def main(page: ft.Page):
    await main_app(page=page, debug=DEBUG)

async def before_main(page: ft.Page):
    await before_main_app(page=page, debug=DEBUG)


if __name__ == "__main__":
    ft.run(main=main, before_main=before_main, assets_dir="assets")