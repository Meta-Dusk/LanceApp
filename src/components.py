import flet as ft

from styles import FontStyles


def default_text(value: str, size: ft.Number = 14) -> ft.Text:
    return ft.Text(
        value=value, size=size,
        font_family=FontStyles.BLRRPIX,
        text_align=ft.TextAlign.CENTER
    )

def default_speech_bubble(msg: str) -> ft.Container:
    """Returns the default speech bubble for Miku."""
    return ft.Container(
        content=default_text(value=msg, size=16),
        bgcolor=ft.Colors.with_opacity(0.95, ft.Colors.LIGHT_BLUE),
        border=ft.Border.all(4, ft.Colors.with_opacity(0.7, ft.Colors.BLUE_900)),
        padding=10, border_radius=15, alignment=ft.Alignment.TOP_CENTER,
        opacity=0, offset=ft.Offset(x=0.0, y=1.0),
        animate_offset=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
        animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT)
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
        content=default_text(value=text), expand=True,
        on_click=on_click,
        # col={"lg": 2, "md": 4, "xs": 8}
    )

def default_menu(title: str) -> ft.Container:
    """Returns the default menu for Miku."""
    count = 0
    def on_click(_):
        nonlocal count
        count += 1
        text = f"I'm a button ({count})"
        extension = "---"
        for _ in range(count):
            extension += extension
        text = f"{extension}{text}{extension}"
        buttons.controls.append(default_button(text=text, on_click=on_click))
        buttons.update()
    
    title_text = default_text(value=title, size=20)
    title_container = default_container(title_text)
    title_row = ft.Row(
        controls=[title_container], expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    test_button = default_button(text=f"I'm a button ({count})", on_click=on_click)
    buttons = ft.ResponsiveRow(
        controls=[test_button], expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    button_column = ft.Column(
        controls=[buttons], expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO, height=80
    )
    button_row = ft.Row(
        controls=[button_column], expand=True,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    buttons_container = default_container(button_row)
    
    main_column = ft.Column(
        controls=[title_row, buttons_container], expand=True,
        alignment=ft.MainAxisAlignment.CENTER
    )
    
    return ft.Container(
        content=main_column, expand=True,
        bgcolor=ft.Colors.with_opacity(0.65, ft.Colors.LIGHT_BLUE),
        padding=10, border_radius=15,
        border=ft.Border.all(4, ft.Colors.with_opacity(0.5, ft.Colors.BLUE_900)),
        alignment=ft.Alignment.TOP_CENTER,
    )