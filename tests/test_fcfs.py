from src.algorithms.fcfs import FCFSScheduler
from src.core.process import Process
from src.core.processor import Core
from src.core.simulator import Simulator


def test_fcfs_single_core_waiting_time() -> None:
    processes = [Process(1, 0, 5), Process(2, 2, 3)]
    result = Simulator(processes, [Core.make_e_core(0)], FCFSScheduler()).run()

    assert result.finish_time == 8
    assert processes[0].completion_time == 5
    assert processes[0].waiting_time == 0
    assert processes[1].completion_time == 8
    assert processes[1].waiting_time == 3


def test_fcfs_prefers_e_core_for_new_assignments() -> None:
    processes = [Process(1, 0, 2), Process(2, 0, 1)]
    cores = [Core.make_p_core(0), Core.make_e_core(1)]
    result = Simulator(processes, cores, FCFSScheduler()).run()

    first_tick = [event for event in result.events if event.time == 0]
    assert {event.core_id: event.pid for event in first_tick} == {0: 2, 1: 1}
    assert processes[0].completion_time == 2
    assert processes[1].completion_time == 1

