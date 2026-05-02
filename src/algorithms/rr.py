from __future__ import annotations

from src.algorithms.base import Scheduler
from src.core.process import Process
from src.core.processor import Core


class RRScheduler(Scheduler):
    name = "RR"

    def __init__(self, quantum: int = 3) -> None:
        if quantum < 1:
            raise ValueError("quantum must be at least 1")
        self.quantum = quantum
        self.running_ticks_by_core: dict[int, int] = {}
        self.last_pid_by_core: dict[int, int | None] = {}

    def select(
        self,
        ready_queue: list[Process],
        cores: list[Core],
        current_time: int,
    ) -> dict[int, int]:
        valid_pids = self.ready_pids(ready_queue)
        assignment: dict[int, int] = {}
        assigned_pids: set[int] = set()

        for core in sorted(cores, key=lambda item: item.core_id):
            current_pid = core.current_pid
            if current_pid not in valid_pids:
                self.running_ticks_by_core[core.core_id] = 0
                self.last_pid_by_core[core.core_id] = None
                continue

            other_ready = any(
                process.pid != current_pid and process.pid not in assigned_pids
                for process in ready_queue
                if process.remaining and process.remaining > 0
            )
            elapsed = self.running_ticks_by_core.get(core.core_id, 0)
            if elapsed >= self.quantum and other_ready:
                self.move_to_end(ready_queue, current_pid)
                self.running_ticks_by_core[core.core_id] = 0
                self.last_pid_by_core[core.core_id] = None
                continue

            assignment[core.core_id] = current_pid
            assigned_pids.add(current_pid)

        idle_cores = [
            core
            for core in sorted(cores, key=self.core_assignment_key)
            if core.core_id not in assignment
        ]
        for core in idle_cores:
            for process in ready_queue:
                if not process.remaining or process.remaining <= 0:
                    continue
                if process.pid in assigned_pids:
                    continue
                assignment[core.core_id] = process.pid
                assigned_pids.add(process.pid)
                break

        self._update_quantum_state(cores, assignment)
        return assignment

    def _update_quantum_state(self, cores: list[Core], assignment: dict[int, int]) -> None:
        for core in cores:
            next_pid = assignment.get(core.core_id)
            previous_pid = self.last_pid_by_core.get(core.core_id)
            if next_pid is None:
                self.running_ticks_by_core[core.core_id] = 0
                self.last_pid_by_core[core.core_id] = None
            elif next_pid == previous_pid:
                self.running_ticks_by_core[core.core_id] = (
                    self.running_ticks_by_core.get(core.core_id, 0) + 1
                )
            else:
                self.running_ticks_by_core[core.core_id] = 1
                self.last_pid_by_core[core.core_id] = next_pid

