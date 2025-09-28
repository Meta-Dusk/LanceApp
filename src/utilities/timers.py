import asyncio, time

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

class DeltaTimer:
    def __init__(self, target_fps: float | None = None):
        self._last_time = time.perf_counter()
        self._frame_time = 1 / target_fps if target_fps else 0
        self._target_fps = target_fps
        self._dt = 0.0

    async def tick(self) -> float:
        """Advance the global clock and return delta time in seconds."""
        now = time.perf_counter()
        dt = now - self._last_time

        if self._target_fps and dt < self._frame_time:
            delay = self._frame_time - dt
            await asyncio.sleep(round(delay, 2))
            now = time.perf_counter()
            dt = now - self._last_time
            
        self._last_time = now
        self._dt = dt
        return dt

    @property
    def delta(self) -> float:
        """Get the most recent delta time."""
        return self._dt


# Create a single global timer (e.g. 60 FPS cap)
# global_timer = DeltaTimer(target_fps=60)