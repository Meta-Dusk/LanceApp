import flet as ft

from styles import FontStyles


def default_speech_bubble(msg: str) -> ft.Container:
    """Returns the default speech bubble for Miku"""
    return ft.Container(
        content=ft.Text(
            value=msg, size=16,
            font_family=FontStyles.BLRRPIX,
            text_align=ft.TextAlign.CENTER),
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE),
        padding=10, border_radius=15, left=0, right=0, top=0,
        border=ft.Border.all(4, ft.Colors.with_opacity(0.7, ft.Colors.BLUE_900)),
        alignment=ft.Alignment.TOP_CENTER,
    )