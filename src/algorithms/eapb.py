from __future__ import annotations

from math import ceil

from src.algorithms.base import Scheduler
from src.core.process import Process
from src.core.processor import Core


class EAPBScheduler(Scheduler):
    name = "Custom"

    CACHE_WARMUP_TICKS = 1
    MIGRATION_LAMBDA = 0.3
    MIN_RUN_TICKS = 2
    STARVATION_RATIO = 2.0

    def priority(
        self,
        process: Process,
        ready_queue: list[Process],
        cores: list[Core],
    ) -> float:
        waiting_time = max(process.waiting_time, 0)
        urgency = waiting_time / (waiting_time + process.burst_time)
        queue_pressure = min(len(self.runnable_processes(ready_queue)) / len(cores), 1.0)
        return (0.7 * urgency) + (0.3 * queue_pressure)

    def cost(self, process: Process, core: Core, current_time: int) -> float:
        edp = self.edp_cost(process, core, current_time)
        migration = self.migration_cost(process, core, current_time)
        return edp + (self.MIGRATION_LAMBDA * migration)

    def edp_cost(self, process: Process, core: Core, current_time: int) -> float:
        remaining = process.remaining or 0
        predicted_ticks = max(1, ceil(remaining / core.speed))
        startup_energy = core.power_startup if core.was_idle else 0.0
        predicted_energy = (predicted_ticks * core.power_active) + startup_energy
        predicted_finish = current_time + predicted_ticks
        predicted_turnaround = max(1, predicted_finish - process.arrival_time)
        return predicted_energy * predicted_turnaround

    def migration_cost(self, process: Process, core: Core, current_time: int) -> float:
        if process.last_core_id is None or process.last_core_id == core.core_id:
            return 0.0

        remaining = process.remaining or 0
        predicted_ticks = max(1, ceil(remaining / core.speed))
        predicted_finish = current_time + predicted_ticks
        predicted_turnaround = max(1, predicted_finish - process.arrival_time)
        return self.CACHE_WARMUP_TICKS * core.power_active * predicted_turnaround

    def select(
        self,
        ready_queue: list[Process],
        cores: list[Core],
        current_time: int,
    ) -> dict[int, int]:
        assignment, assigned_pids = self.keep_running_assignments(ready_queue, cores)
        preempted_pids = self._apply_starvation_preemption(
            assignment,
            assigned_pids,
            ready_queue,
            cores,
        )

        candidates = [
            process
            for process in self.runnable_processes(ready_queue, assigned_pids | preempted_pids)
        ]
        candidates.sort(
            key=lambda process: (
                -self.priority(process, ready_queue, cores),
                process.arrival_time,
                process.pid,
            )
        )

        for process in candidates:
            idle_cores = [
                core
                for core in sorted(cores, key=lambda item: item.core_id)
                if core.core_id not in assignment
            ]
            if not idle_cores:
                break

            best_core = min(
                idle_cores,
                key=lambda core: (
                    self.cost(process, core, current_time),
                    self.core_assignment_key(core),
                ),
            )
            assignment[best_core.core_id] = process.pid
            assigned_pids.add(process.pid)

        return assignment

    def _apply_starvation_preemption(
        self,
        assignment: dict[int, int],
        assigned_pids: set[int],
        ready_queue: list[Process],
        cores: list[Core],
    ) -> set[int]:
        preempted_pids: set[int] = set()
        process_by_pid = {process.pid: process for process in ready_queue}

        for core in sorted(cores, key=lambda item: item.core_id):
            running_pid = assignment.get(core.core_id)
            if running_pid is None or core.run_ticks < self.MIN_RUN_TICKS:
                continue

            running_process = process_by_pid[running_pid]
            running_priority = self.priority(running_process, ready_queue, cores)
            waiting_candidates = [
                process
                for process in ready_queue
                if process.pid != running_pid
                and process.pid not in assigned_pids
                and process.remaining
                and process.remaining > 0
            ]
            if not waiting_candidates:
                continue

            strongest_waiting = max(
                waiting_candidates,
                key=lambda process: (
                    self.priority(process, ready_queue, cores),
                    -process.arrival_time,
                    -process.pid,
                ),
            )
            if self.priority(strongest_waiting, ready_queue, cores) > (
                self.STARVATION_RATIO * running_priority
            ):
                assignment.pop(core.core_id)
                assigned_pids.remove(running_pid)
                preempted_pids.add(running_pid)

        return preempted_pids

