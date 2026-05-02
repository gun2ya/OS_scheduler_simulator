from __future__ import annotations

from dataclasses import dataclass

from src.algorithms.base import Scheduler
from src.core.event import PowerEvent, ScheduleEvent
from src.core.process import Process
from src.core.processor import Core
from src.power.power_model import PowerReport, compute_power_report


@dataclass
class SimulationResult:
    events: list[ScheduleEvent]
    power_log: list[PowerEvent]
    processes: list[Process]
    cores: list[Core]
    finish_time: int

    @property
    def power_report(self) -> PowerReport:
        return compute_power_report(self.cores, self.power_log)

    @property
    def total_power(self) -> float:
        return self.power_report.total_energy

    @property
    def average_waiting_time(self) -> float:
        if not self.processes:
            return 0.0
        return sum(process.waiting_time for process in self.processes) / len(self.processes)

    @property
    def average_turnaround_time(self) -> float:
        if not self.processes:
            return 0.0
        return sum(process.turnaround_time for process in self.processes) / len(self.processes)

    @property
    def average_normalized_turnaround_time(self) -> float:
        if not self.processes:
            return 0.0
        return (
            sum(process.normalized_turnaround_time for process in self.processes)
            / len(self.processes)
        )


class Simulator:
    def __init__(
        self,
        processes: list[Process],
        cores: list[Core],
        scheduler: Scheduler,
        max_ticks: int = 100_000,
    ) -> None:
        if not cores:
            raise ValueError("at least one core is required")
        if len({process.pid for process in processes}) != len(processes):
            raise ValueError("process pid values must be unique")
        if max_ticks < 1:
            raise ValueError("max_ticks must be at least 1")

        self.processes = sorted(processes, key=lambda process: (process.arrival_time, process.pid))
        self.cores = sorted(cores, key=lambda core: core.core_id)
        self.scheduler = scheduler
        self.max_ticks = max_ticks
        self._process_by_pid = {process.pid: process for process in self.processes}

    def run(self) -> SimulationResult:
        self._reset_runtime_state()

        current_time = 0
        ready_queue: list[Process] = []
        events: list[ScheduleEvent] = []
        power_log: list[PowerEvent] = []

        while not self._all_finished():
            if current_time >= self.max_ticks:
                raise RuntimeError(
                    f"simulation exceeded max_ticks={self.max_ticks}; check scheduler progress"
                )

            self._append_arrivals(ready_queue, current_time)
            assignment = self.scheduler.select(ready_queue, self.cores, current_time)
            self._validate_assignment(assignment, ready_queue, current_time)

            assigned_pids = set(assignment.values())
            completed_this_tick: set[int] = set()
            for core in self.cores:
                assigned_pid = assignment.get(core.core_id)
                if assigned_pid is None:
                    events.append(ScheduleEvent(current_time, 1, core.core_id, None))
                    core.current_pid = None
                    core.was_idle = True
                    continue

                process = self._process_by_pid[assigned_pid]
                if core.was_idle:
                    power_log.append(
                        PowerEvent(current_time, core.core_id, "startup", core.power_startup)
                    )

                if process.start_time == -1:
                    process.start_time = current_time

                work_done = min(core.speed, process.remaining or 0)
                process.remaining = (process.remaining or 0) - work_done

                events.append(ScheduleEvent(current_time, 1, core.core_id, process.pid))
                power_log.append(PowerEvent(current_time, core.core_id, "active", core.power_active))

                core.was_idle = False
                if process.remaining == 0:
                    process.completion_time = current_time + 1
                    completed_this_tick.add(process.pid)
                    core.current_pid = None
                else:
                    core.current_pid = process.pid

            if completed_this_tick:
                ready_queue[:] = [
                    process for process in ready_queue if process.pid not in completed_this_tick
                ]

            for process in ready_queue:
                if process.pid not in assigned_pids and process.remaining and process.remaining > 0:
                    process.waiting_time += 1

            current_time += 1

        return SimulationResult(
            events=events,
            power_log=power_log,
            processes=self.processes,
            cores=self.cores,
            finish_time=current_time,
        )

    def _reset_runtime_state(self) -> None:
        for process in self.processes:
            process.reset_runtime()
        for core in self.cores:
            core.reset_runtime()

    def _all_finished(self) -> bool:
        return all(process.remaining == 0 for process in self.processes)

    def _append_arrivals(self, ready_queue: list[Process], current_time: int) -> None:
        queued_pids = {process.pid for process in ready_queue}
        for process in self.processes:
            if process.arrival_time == current_time and process.pid not in queued_pids:
                ready_queue.append(process)
                queued_pids.add(process.pid)

    def _validate_assignment(
        self,
        assignment: dict[int, int],
        ready_queue: list[Process],
        current_time: int,
    ) -> None:
        valid_core_ids = {core.core_id for core in self.cores}
        ready_pids = {
            process.pid
            for process in ready_queue
            if process.arrival_time <= current_time and process.remaining and process.remaining > 0
        }

        seen_pids: set[int] = set()
        for core_id, pid in assignment.items():
            if core_id not in valid_core_ids:
                raise ValueError(f"scheduler assigned unknown core_id={core_id}")
            if pid in seen_pids:
                raise ValueError(f"scheduler assigned pid={pid} to multiple cores")
            if pid not in ready_pids:
                raise ValueError(f"scheduler assigned unavailable pid={pid}")
            seen_pids.add(pid)

