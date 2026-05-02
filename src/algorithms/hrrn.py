from __future__ import annotations

from src.algorithms.base import Scheduler
from src.core.process import Process
from src.core.processor import Core


class HRRNScheduler(Scheduler):
    name = "HRRN"

    def select(
        self,
        ready_queue: list[Process],
        cores: list[Core],
        current_time: int,
    ) -> dict[int, int]:
        assignment, assigned_pids = self.keep_running_assignments(ready_queue, cores)
        candidates = sorted(
            self.runnable_processes(ready_queue, assigned_pids),
            key=lambda process: (
                -((process.waiting_time + process.burst_time) / process.burst_time),
                process.arrival_time,
                process.pid,
            ),
        )
        return self.assign_candidates_to_idle_cores(assignment, assigned_pids, cores, candidates)

