import flet as ft

from styles import FontStyles


def default_speech_bubble(msg: str) -> ft.Container:
    """Returns the default speech bubble for Miku"""
    return ft.Container(
        content=ft.Text(
            value=msg, size=16,
            font_family=FontStyles.BLRRPIX,
            text_align=ft.TextAlign.CENTER
        ),
        
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE),
        padding=10, border_radius=15,
        border=ft.Border.all(4, ft.Colors.with_opacity(0.7, ft.Colors.BLUE_900)),
        alignment=ft.Alignment.TOP_CENTER,
    )

def default_menu(title: str) -> ft.Container:
    """Returns the default menu for Miku"""
    title_text = ft.Text(
        value=title, size=20,
        font_family=FontStyles.BLRRPIX,
        text_align=ft.TextAlign.CENTER
    )
    title_container = ft.Container(
        content=title_text, padding=10, border=ft.Border.all(3), border_radius=10,
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE), expand=True,
        alignment=ft.Alignment.CENTER
    )
    title_row = ft.Row(
        controls=[title_container], expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    test_button = ft.ElevatedButton("Test Button")
    
    main_column = ft.Column(
        controls=[title_row, test_button], expand=True,
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    return ft.Container(
        content=main_column,
        bgcolor=ft.Colors.with_opacity(0.65, ft.Colors.LIGHT_BLUE),
        padding=10, border_radius=15,
        border=ft.Border.all(4, ft.Colors.with_opacity(0.5, ft.Colors.BLUE_900)),
        alignment=ft.Alignment.TOP_CENTER,
    )