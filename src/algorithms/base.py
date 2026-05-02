from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.process import Process
from src.core.processor import Core


class Scheduler(ABC):
    name = "Scheduler"

    @abstractmethod
    def select(
        self,
        ready_queue: list[Process],
        cores: list[Core],
        current_time: int,
    ) -> dict[int, int]:
        """Return a {core_id: pid} assignment for the current tick."""

    @staticmethod
    def core_assignment_key(core: Core) -> tuple[int, int]:
        return (0 if core.core_type == "E" else 1, core.core_id)

    @staticmethod
    def ready_pids(ready_queue: list[Process]) -> set[int]:
        return {process.pid for process in ready_queue if process.remaining and process.remaining > 0}

    @staticmethod
    def running_pids(cores: list[Core]) -> set[int]:
        return {core.current_pid for core in cores if core.current_pid is not None}

    @staticmethod
    def runnable_processes(
        ready_queue: list[Process],
        excluded_pids: set[int] | None = None,
    ) -> list[Process]:
        excluded_pids = excluded_pids or set()
        return [
            process
            for process in ready_queue
            if process.remaining and process.remaining > 0 and process.pid not in excluded_pids
        ]

    @staticmethod
    def keep_running_assignments(
        ready_queue: list[Process],
        cores: list[Core],
    ) -> tuple[dict[int, int], set[int]]:
        valid_pids = Scheduler.ready_pids(ready_queue)
        assignment: dict[int, int] = {}
        assigned_pids: set[int] = set()

        for core in sorted(cores, key=lambda item: item.core_id):
            if core.current_pid in valid_pids and core.current_pid not in assigned_pids:
                assignment[core.core_id] = core.current_pid
                assigned_pids.add(core.current_pid)

        return assignment, assigned_pids

    @staticmethod
    def move_to_end(ready_queue: list[Process], pid: int) -> None:
        for index, process in enumerate(ready_queue):
            if process.pid == pid:
                ready_queue.append(ready_queue.pop(index))
                return

    @staticmethod
    def assign_candidates_to_idle_cores(
        assignment: dict[int, int],
        assigned_pids: set[int],
        cores: list[Core],
        candidates: list[Process],
    ) -> dict[int, int]:
        idle_cores = [
            core
            for core in sorted(cores, key=Scheduler.core_assignment_key)
            if core.core_id not in assignment
        ]

        candidate_iter = (
            process
            for process in candidates
            if process.pid not in assigned_pids and process.remaining and process.remaining > 0
        )
        for core, process in zip(idle_cores, candidate_iter):
            assignment[core.core_id] = process.pid
            assigned_pids.add(process.pid)

        return assignment

