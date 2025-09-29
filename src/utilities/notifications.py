from desktop_notifier import DesktopNotifier, Urgency
from typing import Callable, Any


global_notifier = DesktopNotifier(app_name="Hatsune Miku")


async def send_notif(title: str, msg: str, urgency: Urgency, on_clicked: Callable[[], Any]) -> None:
    """Send a notification that can be clicked. Only works in Windows."""
    await global_notifier.send(title=title, message=msg, urgency=urgency, on_clicked=on_clicked)
    
async def preset_help_notif(on_clicked: Callable[[], Any]) -> None:
    """A preset `Notification` used by Miku."""
    await send_notif(
        title="Help Me!",
        message="I've somehow ended up outside of your monitor... I'm in the void! （；´д｀）ゞ",
        urgency=Urgency.Critical,
        on_clicked=on_clicked
    )