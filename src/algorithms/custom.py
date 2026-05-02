from __future__ import annotations

from src.algorithms.base import Scheduler
from src.algorithms.fcfs import FCFSScheduler
from src.core.process import Process
from src.core.processor import Core


class CustomScheduler(Scheduler):
    name = "Custom"

    def __init__(self) -> None:
        self._fallback = FCFSScheduler()

    def select(
        self,
        ready_queue: list[Process],
        cores: list[Core],
        current_time: int,
    ) -> dict[int, int]:
        return self._fallback.select(ready_queue, cores, current_time)

