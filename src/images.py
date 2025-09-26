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
        border_radius=20, padding=5,
        alignment=ft.Alignment.CENTER
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
    gapless_playback: bool = True
    expand: bool = False
    anti_alias: bool = True


@dataclass
class MikuData(ImageData):
    width: Optional[int] = 258
    height: Optional[int] = 210
    anti_alias: bool = False
    error_content: ft.Control = field(default_factory=lambda: error_container("No Miku 😔"))
    data: Optional[dict] = field(default_factory=lambda: {
        "flipped": False,
        "pan_start": False,
        "long_pressed": False
    })


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
        self._debug_msg("A miku has been made.")
        return generate_image(miku_data)
    
    def _debug_msg(self, msg: str):
        if self.debug:
            print(f"[Miku] {msg}")
    
    
    def print(self):
        for attr in self.__dict__.items():
            print(attr)
    
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
    """
    Gets attributes of `image_data` as a `dict`, then unpacks them with `**`,
    then assigns them to the args of `Image`.
    """
    return ft.Image(**image_data.__dict__)


"""
Run test for images.py with:
py -m src.images
"""
async def test(page: ft.Page):
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
    await page.window.center()

    miku = DynamicMiku(Miku.NEUTRAL, debug=True)
    # miku.print()
    
    # for data in Miku:
    #     print(f"{data.name}: {data.value}\n")
    
    stack = ft.Stack(controls=[miku.get_image()], alignment=ft.Alignment.CENTER)
    
    page.add(stack)


if __name__ == "__main__":
    ft.app(target=test)
