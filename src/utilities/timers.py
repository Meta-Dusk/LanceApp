import asyncio

class ResettableTimer:
    def __init__(self, duration: float):
        self.duration = duration
        self._task = None
        self._reset_event = asyncio.Event()
        self.expired = asyncio.Event()  # <-- external event

    async def _run(self):
        while True:
            try:
                # Wait for reset OR timeout
                await asyncio.wait_for(self._reset_event.wait(), timeout=self.duration)
                self._reset_event.clear()
            except asyncio.TimeoutError:
                # Timer expired
                self.expired.set()   # <-- signal expiration
                break

    def start(self):
        self.expired.clear()  # clear old expiration
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())
        else:
            self._reset_event.set()

    def cancel(self):
        if self._task and not self._task.done():
            self._task.cancel()
            self._task = None