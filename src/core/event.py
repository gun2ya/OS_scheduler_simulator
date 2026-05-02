from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class ScheduleEvent:
    time: int
    duration: int
    core_id: int
    pid: int | None


@dataclass(frozen=True)
class PowerEvent:
    time: int
    core_id: int
    kind: Literal["active", "startup"]
    amount: float

