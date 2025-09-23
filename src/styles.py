import flet as ft


def transparent_window(page: ft.Page, width: int = 258, height: int = 210, debug: bool = False):
    page.bgcolor = ft.Colors.TRANSPARENT
    page.padding = 0
    page.fonts = {
        "BlrrPix": "blrrpixs016.ttf"
    }
    page.vertical_alignment = ft.MainAxisAlignment.END

    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.window.title_bar_hidden = True
    page.window.always_on_top = True
    page.window.frameless = True
    page.window.resizable = False
    page.window.width = width
    page.window.height = height
    page.decoration = ft.BoxDecoration(border_radius=10, border=ft.border.all(2, ft.Colors.PRIMARY)) if debug else None
    # page.appbar = ft.AppBar(
    #     actions=[
    #         ft.IconButton(ft.Icons.CHAT_BUBBLE, on_click=on_chat)
    #     ], bgcolor=ft.Colors.TRANSPARENT, toolbar_height=40,
    #     # title=ft.Text("Hatsune Miku"), center_title=True
    # )