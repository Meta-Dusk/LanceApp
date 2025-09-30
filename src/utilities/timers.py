import asyncio, time

class ResettableTimer:
    """An asynchronous timer that can be reset while running."""
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

class DeltaTimer:
    """
    A global timer that serves as a machine-independent
    frame delay for implementations with FPS.
    """
    def __init__(self, target_fps: float | None = None):
        self._last_time = time.perf_counter()
        self._frame_time = 1 / target_fps if target_fps else 0
        self._target_fps = target_fps
        self._dt = 0.0
        self._MIN_SLEEP_S = 0.01
        self._MIN_DT_S = 0.01

    async def tick(self) -> float:
        """Advance the global clock and return delta time in seconds."""
        now = time.perf_counter()
        dt = now - self._last_time

        if self._target_fps and dt < self._frame_time:
            delay = self._frame_time - dt
            await asyncio.sleep(max(delay, self._MIN_SLEEP_S))
            now = time.perf_counter()
            dt = now - self._last_time
        
        dt = max(dt, self._MIN_DT_S)
        self._last_time = now
        self._dt = dt
        return dt

    @property
    def delta(self) -> float:
        """Get the most recent delta time."""
        return self._dt
