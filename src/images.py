import flet as ft

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


IMAGES_PATH = Path("images")
MIKU_STATES = IMAGES_PATH / "miku_states"


def error_container(msg: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(value=msg, color=ft.Colors.ERROR),
        bgcolor=ft.Colors.ERROR_CONTAINER,
        border_radius=20,
        padding=5,
        alignment=ft.Alignment.CENTER,
    )


class MikuStates(Enum):
    AMGRY = "amgry"
    ECSTATIC = "ecstatic"
    GLASSES = "glasses"
    HAPPY = "happy"
    JOY = "joy"
    NEUTRAL = "neutral"
    PONDER = "ponder"
    READING = "reading"
    READY = "ready"
    SHOCK = "shock"
    SINGING = "singing"
    THINKING = "thinking"


def get_miku_state(state: MikuStates) -> str:
    img_path = MIKU_STATES / f"miku_{state.value}.png"
    return str(img_path)


@dataclass
class ImageData:
    src: str
    width: Optional[int] = None
    height: Optional[int] = None
    error_content: ft.Control = field(default_factory=lambda: error_container("IMAGE ERROR"))
    fit: ft.BoxFit = ft.BoxFit.COVER


@dataclass
class MikuData(ImageData):
    anti_alias: bool = False
    expand: bool = True
    error_content: ft.Control = field(default_factory=lambda: error_container("No Miku 😔"))
    fit: ft.BoxFit = ft.BoxFit.FILL
    data: Optional[dict] = None


class Miku(Enum):
    AMGRY = MikuData(src=get_miku_state(MikuStates.AMGRY))
    ECSTATIC = MikuData(src=get_miku_state(MikuStates.ECSTATIC))
    GLASSES = MikuData(src=get_miku_state(MikuStates.GLASSES))
    HAPPY = MikuData(src=get_miku_state(MikuStates.HAPPY))
    JOY = MikuData(src=get_miku_state(MikuStates.JOY))
    NEUTRAL = MikuData(src=get_miku_state(MikuStates.NEUTRAL))
    PONDER = MikuData(src=get_miku_state(MikuStates.PONDER))
    READING = MikuData(src=get_miku_state(MikuStates.READING))
    READY = MikuData(src=get_miku_state(MikuStates.READY))
    SHOCK = MikuData(src=get_miku_state(MikuStates.SHOCK))
    SINGING = MikuData(src=get_miku_state(MikuStates.SINGING))
    THINKING = MikuData(src=get_miku_state(MikuStates.THINKING))


class Sprites(Enum):
    SPEECH_BUBBLE = ImageData(src=str(IMAGES_PATH / "speech_bubble.png"), width=1024, height=577)

class DynamicMiku:
    def __init__(self, miku_data: Miku, debug: bool = False):
        self.debug = debug
        self.miku_data = miku_data
        self._image = self._generate_image(miku_data.value)
        self.state = miku_data.name

    def _generate_image(self, miku_data):
        img = ft.Image(
            src=miku_data.src,
            width=miku_data.width,
            height=miku_data.height,
            error_content=miku_data.error_content,
            fit=miku_data.fit,
            expand=miku_data.expand,
        )
        img.data = {
            "flipped": False,
            "pan_start": False,
            "long_pressed": False
        }
        img.animate_opacity = ft.Animation(0)
        img.anti_alias = miku_data.anti_alias
        self._debug_msg("A miku has been made.")
        return img
    
    def _debug_msg(self, msg: str):
        if self.debug:
            print(f"[Miku] {msg}")
    
    
    def get_image(self) -> ft.Image:
        return self._image

    def set_state(self, new_state: Miku):
        """Swap to a new Miku state."""
        self._debug_msg(f"Setting state from {self.miku_data.name} -> {new_state.name}")
        self.state = new_state.name
        self.miku_data = new_state
        self._image.src = new_state.value.src
        self._image.update()

    # -----------------------------
    # Helpers for common flags
    # -----------------------------
    def set_flipped(self, flipped: bool):
        self._debug_msg(f"Setting flip to {flipped}")
        self._image.data["flipped"] = flipped
        self._image.scale = ft.Scale(scale_x=-1 if flipped else 1)
        self._image.update()

    def is_flipped(self) -> bool:
        return self._image.data.get("flipped", False)

    def set_pan_start(self, active: bool):
        self._image.data["pan_start"] = active

    def is_pan_start(self) -> bool:
        return self._image.data.get("pan_start", False)
    
    def set_long_pressed(self, active: bool) -> bool:
        self._image.data["long_pressed"] = active
    
    def is_long_pressed(self) -> bool:
        return self._image.data.get("long_pressed", False)


def generate_image(image_data: ImageData) -> ft.Image:
    return ft.Image(
        src=image_data.src,
        width=image_data.width,
        height=image_data.height,
        error_content=image_data.error_content,
        fit=image_data.fit,
    )


def generate_miku(miku_data: MikuData) -> ft.Image:
    img = generate_image(miku_data)
    img.expand = miku_data.expand
    img.data = {"flipped": False, "pan_start": False}
    img.animate_opacity = ft.Animation(0)
    img.anti_alias = miku_data.anti_alias
    return img


def test(page: ft.Page):
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
    
    # transparent_window(page, debug=True)
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER
    page.vertical_alignment = ft.CrossAxisAlignment.CENTER
    page.window.center()

    miku = generate_miku(Miku.AMGRY.value)
    
    speech_bubble = generate_image(Sprites.SPEECH_BUBBLE.value)
    speech_bubble.scale = 0.4
    
    stack = ft.Stack(controls=[miku, speech_bubble], alignment=ft.alignment.center)
    
    page.add(stack)


if __name__ == "__main__":
    ft.app(target=test)
