from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    remaining: int | None = None
    start_time: int = -1
    completion_time: int = -1
    waiting_time: int = 0
    last_core_id: int | None = None
    migration_count: int = 0

    def __post_init__(self) -> None:
        if self.pid < 0:
            raise ValueError("pid must be non-negative")
        if self.arrival_time < 0:
            raise ValueError("arrival_time must be non-negative")
        if self.burst_time < 1:
            raise ValueError("burst_time must be at least 1")
        if self.remaining is None:
            self.remaining = self.burst_time
        if self.remaining < 0:
            raise ValueError("remaining must be non-negative")

    @property
    def is_arrived(self) -> bool:
        return self.arrival_time >= 0

    @property
    def is_completed(self) -> bool:
        return self.remaining == 0

    @property
    def turnaround_time(self) -> int:
        if self.completion_time < 0:
            return -1
        return self.completion_time - self.arrival_time

    @property
    def normalized_turnaround_time(self) -> float:
        if self.turnaround_time < 0:
            return -1.0
        return self.turnaround_time / self.burst_time

    def reset_runtime(self) -> None:
        self.remaining = self.burst_time
        self.start_time = -1
        self.completion_time = -1
        self.waiting_time = 0
        self.last_core_id = None
        self.migration_count = 0
