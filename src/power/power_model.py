from __future__ import annotations

from dataclasses import dataclass

from src.core.event import PowerEvent
from src.core.processor import Core


@dataclass(frozen=True)
class CorePowerReport:
    core_id: int
    core_type: str
    active_time: int
    active_power: float
    startup_count: int
    startup_power: float

    @property
    def active_energy(self) -> float:
        return self.active_time * self.active_power

    @property
    def startup_energy(self) -> float:
        return self.startup_count * self.startup_power

    @property
    def total_energy(self) -> float:
        return self.active_energy + self.startup_energy


@dataclass(frozen=True)
class PowerReport:
    cores: list[CorePowerReport]

    @property
    def total_energy(self) -> float:
        return sum(core.total_energy for core in self.cores)

    def format(self) -> str:
        lines = ["[Power Report]"]
        for core in self.cores:
            lines.append(
                "  Core "
                f"{core.core_id} ({core.core_type}): "
                f"active {core.active_time}s x {core.active_power:.1f}W = "
                f"{core.active_energy:.1f}W*s + startup {core.startup_count} x "
                f"{core.startup_power:.1f}W = {core.startup_energy:.1f}W "
                f"-> {core.total_energy:.1f}W*s"
            )
        lines.append("  " + "-" * 58)
        lines.append(f"  Total: {self.total_energy:.1f} W*s")
        return "\n".join(lines)


def compute_power_report(cores: list[Core], power_log: list[PowerEvent]) -> PowerReport:
    active_counts = {core.core_id: 0 for core in cores}
    startup_counts = {core.core_id: 0 for core in cores}

    for entry in power_log:
        if entry.kind == "active":
            active_counts[entry.core_id] += 1
        elif entry.kind == "startup":
            startup_counts[entry.core_id] += 1

    reports = [
        CorePowerReport(
            core_id=core.core_id,
            core_type=core.core_type,
            active_time=active_counts[core.core_id],
            active_power=core.power_active,
            startup_count=startup_counts[core.core_id],
            startup_power=core.power_startup,
        )
        for core in sorted(cores, key=lambda item: item.core_id)
    ]
    return PowerReport(reports)

