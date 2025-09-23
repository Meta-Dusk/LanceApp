import flet as ft


def transparent_window(page: ft.Page, width: int = 258, height: int = 210, debug: bool = False):
    page.bgcolor = ft.Colors.TRANSPARENT
    page.padding = 0

    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.window.title_bar_hidden = True
    page.window.always_on_top = True
    page.window.frameless = True
    page.window.resizable = False
    page.window.width = width
    page.window.height = height
    page.decoration = ft.BoxDecoration(border_radius=10, border=ft.border.all(2, ft.Colors.PRIMARY)) if debug else None