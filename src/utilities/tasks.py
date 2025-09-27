import asyncio

from typing import Optional


def cancel_task(task: Optional[asyncio.Task]) -> bool:
    if task and not task.done():
        task.cancel()
        return True
    return False

async def await_task_completion(task: Optional[asyncio.Task]) -> bool:
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            return True
    return False