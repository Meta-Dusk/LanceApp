import flet as ft

from typing import Optional
from ui.styles import FontStyles


def default_text(value: str, size: ft.Number = 16, no_wrap: bool = False) -> ft.Text:
    """Returns a pre-styled text component."""
    return ft.Text(
        value=value, size=size,
        font_family=FontStyles.BLRRPIX,
        text_align=ft.TextAlign.CENTER,
        no_wrap=no_wrap
    )

def speech_bubble_text(msg: str, size: ft.Number = 16, text_emoticon: Optional[str] = None) -> ft.Text:
    return ft.Text(
        value=msg, spans=[
            ft.TextSpan(text=msg),
            ft.TextSpan(text=text_emoticon)
        ], size=size,
        font_family=FontStyles.BLRRPIX,
        text_align=ft.TextAlign.CENTER
    )

def default_speech_bubble(msg: str, text_emoticon: Optional[str] = None) -> ft.Container:
    """Returns the default speech bubble for Miku."""
    return ft.Container(
        content=speech_bubble_text(msg=msg, text_emoticon=text_emoticon),
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE),
        border=ft.Border.all(4, ft.Colors.with_opacity(0.7, ft.Colors.BLUE_900)),
        padding=10, border_radius=15, alignment=ft.Alignment.TOP_CENTER,
        opacity=0, offset=ft.Offset(x=0.0, y=1.0),
        animate_offset=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
    )

def default_container(content: ft.Control, expand: bool | int = True) -> ft.Container:
    """Returns a pre-styled container."""
    return ft.Container(
        content=content, padding=10, border_radius=10, alignment=ft.Alignment.CENTER,
        border=ft.Border.all(4, ft.Colors.with_opacity(0.5, ft.Colors.BLUE_400)),
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE), expand=expand
    )

def default_button(
    text: str = "Example Button",
    on_click: Optional[ft.ControlEventHandler[ft.Button]] = None
) -> ft.Button:
    """Returns a pre-styled button."""
    if on_click is None:
        on_click = lambda _: print(f"Button ({text}) has been pressed!")
    
    return ft.Button(
        content=default_text(value=text), expand=True,
        on_click=on_click,
        # col={"lg": 2, "md": 4, "xs": 8}
    )
