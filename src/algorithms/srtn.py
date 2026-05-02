from __future__ import annotations

from src.algorithms.base import Scheduler
from src.core.process import Process
from src.core.processor import Core


class SRTNScheduler(Scheduler):
    name = "SRTN"

    def select(
        self,
        ready_queue: list[Process],
        cores: list[Core],
        current_time: int,
    ) -> dict[int, int]:
        candidates = sorted(
            self.runnable_processes(ready_queue),
            key=lambda process: (process.remaining, process.arrival_time, process.pid),
        )
        selected = candidates[: len(cores)]
        selected_pids = {process.pid for process in selected}

        assignment: dict[int, int] = {}
        assigned_pids: set[int] = set()
        for core in sorted(cores, key=lambda item: item.core_id):
            if core.current_pid in selected_pids and core.current_pid not in assigned_pids:
                assignment[core.core_id] = core.current_pid
                assigned_pids.add(core.current_pid)

        remaining_selected = [process for process in selected if process.pid not in assigned_pids]
        return self.assign_candidates_to_idle_cores(
            assignment,
            assigned_pids,
            cores,
            remaining_selected,
        )

