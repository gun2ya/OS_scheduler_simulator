from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


CoreType = Literal["P", "E"]


@dataclass
class Core:
    core_id: int
    core_type: CoreType
    speed: int
    power_active: float
    power_startup: float
    current_pid: int | None = None
    was_idle: bool = True
    run_ticks: int = 0

    def __post_init__(self) -> None:
        if self.core_id < 0:
            raise ValueError("core_id must be non-negative")
        if self.core_type not in ("P", "E"):
            raise ValueError("core_type must be 'P' or 'E'")
        if self.speed < 1:
            raise ValueError("speed must be at least 1")
        if self.power_active < 0 or self.power_startup < 0:
            raise ValueError("power values must be non-negative")

    @classmethod
    def make_p_core(cls, core_id: int) -> Core:
        return cls(core_id, "P", 2, 3.0, 0.5)

    @classmethod
    def make_e_core(cls, core_id: int) -> Core:
        return cls(core_id, "E", 1, 1.0, 0.1)

    def reset_runtime(self) -> None:
        self.current_pid = None
        self.was_idle = True
        self.run_ticks = 0
