from src.algorithms.fcfs import FCFSScheduler
from src.core.process import Process
from src.core.processor import Core
from src.core.simulator import Simulator


def test_p_core_with_one_remaining_unit_still_consumes_one_tick() -> None:
    processes = [Process(1, 0, 1)]
    result = Simulator(processes, [Core.make_p_core(0)], FCFSScheduler()).run()

    assert result.finish_time == 1
    assert processes[0].completion_time == 1
    assert len([event for event in result.events if event.pid == 1]) == 1


def test_multicore_finishes_independent_jobs_in_parallel() -> None:
    processes = [Process(1, 0, 4), Process(2, 0, 4)]
    cores = [Core.make_p_core(0), Core.make_e_core(1)]
    result = Simulator(processes, cores, FCFSScheduler()).run()

    assert result.finish_time == 4
    assert processes[0].completion_time == 4
    assert processes[1].completion_time == 2

