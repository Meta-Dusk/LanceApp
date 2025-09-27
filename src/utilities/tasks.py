import asyncio

def cancel_task(task: asyncio.Task | None):
    if task and not task.done():
        task.cancel()

async def await_task_completion(task: asyncio.Task | None):
    if task and not task.done():
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass