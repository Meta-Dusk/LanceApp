import flet as ft

from dataclasses import dataclass
from enum import Enum


@dataclass
class ImageData:
    src: str
    anti_alias: bool = False
    error_content: ft.Control = ft.Container(
        ft.Text("IMAGE ERROR", color=ft.Colors.ERROR), bgcolor=ft.Colors.ERROR_CONTAINER,
        border_radius=20, padding=5, alignment=ft.alignment.center)
    expand: bool = True
    data: any = {"flipped": False}
    
class Miku(ImageData, Enum):
    AMGRY = ImageData(src="assets/images/miku_states/miku_amgry.png")
    ECSTATIC = ImageData(src="assets/images/miku_states/miku_ecstatic.png")
    