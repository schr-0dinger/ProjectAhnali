from __future__ import annotations

import asyncio


class LifecycleAsyncScope:
    """Lifecycle-bound asyncio task scope for host-side helpers.

    Static mode semantics are unaffected because usage is explicit and opt-in.
    """

    def __init__(self):
        self._tasks: set[asyncio.Task] = set()
        self._closed = False

    def create_task(self, coro) -> asyncio.Task:
        if self._closed:
            raise RuntimeError("LifecycleAsyncScope is closed")
        task = asyncio.create_task(coro)
        self._tasks.add(task)

        def _discard(done_task):
            self._tasks.discard(done_task)

        task.add_done_callback(_discard)
        return task

    async def cancel_all(self):
        if self._closed:
            return
        self._closed = True
        tasks = list(self._tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()

    @property
    def active_count(self) -> int:
        return len(self._tasks)
