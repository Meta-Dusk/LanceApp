import flet as ft

from styles import FontStyles


def default_speech_bubble(msg: str) -> ft.Container:
    """Returns the default speech bubble for Miku."""
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

def default_container(content: ft.Control) -> ft.Container:
    """Returns a pre-styled container."""
    return ft.Container(
        content=content, padding=10, border_radius=10,
        border=ft.Border.all(4, ft.Colors.with_opacity(0.5, ft.Colors.BLUE_400)),
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE), expand=True,
        alignment=ft.Alignment.CENTER
    )

def default_button(
    text: str = "Example Button",
    on_click: ft.ControlEventHandler[ft.Button] | None = None
) -> ft.Button:
    """Returns a pre-styled button."""
    if on_click is None:
        on_click = lambda _: print(f"Button ({text}) has been pressed!")
    
    return ft.Button(
        content=ft.Text(
            value=text, size=14, font_family=FontStyles.BLRRPIX,
            text_align=ft.TextAlign.CENTER
        ), expand=True, on_click=on_click
    )

def default_menu(title: str) -> ft.Container:
    """Returns the default menu for Miku."""
    title_text = ft.Text(
        value=title, size=20,
        font_family=FontStyles.BLRRPIX,
        text_align=ft.TextAlign.CENTER
    )
    title_container = default_container(title_text)
    title_row = ft.Row(
        controls=[title_container], expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    test_button = default_button(text="I'm a button")
    button_row = ft.Row(
        controls=[test_button, test_button], expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    button_row_container = default_container(button_row)
    buttons_column = ft.Column(
        controls=[button_row_container], expand=True,
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    # TODO: Add more styling for the menu, and if possible, customizability as provided by the arguments.
    
    main_column = ft.Column(
        controls=[title_row, buttons_column], expand=True,
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    return ft.Container(
        content=main_column,
        bgcolor=ft.Colors.with_opacity(0.65, ft.Colors.LIGHT_BLUE),
        padding=10, border_radius=15,
        border=ft.Border.all(4, ft.Colors.with_opacity(0.5, ft.Colors.BLUE_900)),
        alignment=ft.Alignment.TOP_CENTER,
    )