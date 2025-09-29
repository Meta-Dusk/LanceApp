import asyncio

from typing import Optional


def is_task_done(task: Optional[asyncio.Task]) -> Optional[bool]:
    """
    Returns `True` if task is done. Returns `None` if there's no task.
    """
    if task:
        if task.done():
            return False
        else:
            return True
    else:
        return None

def cancel_task(task: Optional[asyncio.Task]) -> bool:
    """Returns `True` if a task has been cancelled."""
    if task and not task.done():
        task.cancel()
        return True
    return False

async def await_task_completion(task: Optional[asyncio.Task]) -> bool:
    """Returns `True` if a task has been cancelled and is no longer awaitable."""
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            return True
        return True
    return False