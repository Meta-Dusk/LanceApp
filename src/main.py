import flet as ft

from test import test


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
    # await initial_test(page)
    await test(page)


if __name__ == "__main__":
    ft.run(main=main, assets_dir="assets")