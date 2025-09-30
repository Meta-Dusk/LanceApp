import flet as ft

from typing import Optional
from ui.components import default_text, default_container, default_button
from ui.animations import anim_setup_menu


class DefaultMenu:
    """Dynamic menu with title and buttons."""
    def __init__(self, title: str, visible: bool = False):
        # Title
        title_text = default_text(value=title, size=20)
        title_container = default_container(content=title_text, expand=True)
        title_row = ft.Row(
            controls=[title_container], expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        title_row_container = ft.Container(
            content=title_row, expand=1,
            alignment=ft.Alignment.CENTER,
        )

        # Buttons (start empty)
        self._buttons = ft.ResponsiveRow(
            controls=[], expand=True, spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            run_spacing=10,
        )
        self._button_column = ft.Column(
            controls=[self._buttons],
            expand=True, height=80, scroll=ft.ScrollMode.ALWAYS,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
        button_row = ft.Row(
            controls=[self._button_column], expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        buttons_container = default_container(content=button_row, expand=2)

        # Main column
        main_column = ft.Column(
            controls=[title_row_container, buttons_container],
            alignment=ft.MainAxisAlignment.CENTER, expand=True,
        )

        # Root container
        self.container = ft.Container(
            content=main_column, expand=True, padding=10, border_radius=15,
            bgcolor=ft.Colors.with_opacity(0.65, ft.Colors.LIGHT_BLUE),
            border=ft.Border.all(4, ft.Colors.with_opacity(0.5, ft.Colors.BLUE_900)),
            alignment=ft.Alignment.TOP_CENTER, visible=visible
        )

        anim_setup_menu(self.container)

    def add_button(
        self, text: str,
        on_click: Optional[ft.ControlEventHandler[ft.Button]] = None
    ) -> ft.Control:
        """Add a new button to the menu."""
        btn = default_button(text=text, on_click=on_click)
        self._buttons.controls.append(btn)
        if self.container.page is not None:
            self.container.update()
        return btn

    def build(self) -> ft.Container:
        """Return the root container for placement in the UI."""
        return self.container
