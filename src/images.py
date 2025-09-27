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
from desktop_notifier import DesktopNotifier, Notification, Urgency

async def before_test(page: ft.Page):
    page.bgcolor = ft.Colors.TRANSPARENT
    page.padding = 0

    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.window.title_bar_hidden = True
    page.window.always_on_top = True
    page.window.frameless = True
    page.window.resizable = False
    page.window.width = 258 * 2
    page.window.height = 210 * 2
    page.decoration = ft.BoxDecoration(border_radius=10, border=ft.Border.all(2, ft.Colors.PRIMARY))
    await page.window.center()
    page.update()

async def test(page: ft.Page):
    notifier = DesktopNotifier(app_name="Desktop Assistant")
    
    note = Notification(
        title="Miku",
        message="I moved to the right!",
        urgency=Urgency.Normal
    )
    
    async def send_notification(note: Notification):
        await notifier.send_notification(note)
    
    await before_test(page)
    
    async def on_keyboard_event(e: ft.KeyboardEvent):
        key = e.key
        step = 100
        
        if key == "A":
            page.window.left -= step
            page.window.width += step
        if key == "D":
            page.window.left += step
            page.run_task(send_notification, note)
        if key == "W":
            page.window.top -= step
        if key == "S":
            page.window.top += step
        if key == "Escape":
            await page.window.close()
        
        if key or key != "":
            page.window.update()
    
    miku = DynamicMiku(Miku.NEUTRAL)
    miku_img = miku.get_image()
    miku_column = ft.Column(
        controls=[miku_img], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        alignment=ft.MainAxisAlignment.END
    )
    
    test_container = ft.Container(
        content=ft.Row(
            controls=[ft.Text("Hello", color=ft.Colors.ON_SECONDARY_CONTAINER)],
            expand=True, alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor=ft.Colors.SECONDARY_CONTAINER, padding=10, border_radius=20, border=ft.Border.all(3, ft.Colors.SECONDARY)
    )
    test_column = ft.Column(
        controls=[test_container], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    stack = ft.Stack(controls=[miku_column, test_column], alignment=ft.Alignment.TOP_CENTER, expand=True)
    container = ft.Container(content=stack, alignment=ft.Alignment.BOTTOM_CENTER, expand=True)
    form = ft.WindowDragArea(content=container, maximizable=False, expand=True)
    
    page.add(form)
    page.on_keyboard_event = on_keyboard_event


if __name__ == "__main__":
    ft.run(main=test)
