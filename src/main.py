import flet as ft


def main(page: ft.Page):
    page.title = "Test"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.window.center()
    
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
                alignment=ft.alignment.center,
            ),
            expand=True,
        )
    )


ft.app(main)
