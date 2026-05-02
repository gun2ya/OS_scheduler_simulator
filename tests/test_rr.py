from src.algorithms.rr import RRScheduler
from src.core.process import Process
from src.core.processor import Core
from src.core.simulator import Simulator


def test_rr_rotates_after_quantum() -> None:
    processes = [Process(1, 0, 5), Process(2, 0, 3)]
    result = Simulator(processes, [Core.make_e_core(0)], RRScheduler(quantum=2)).run()

    assert result.finish_time == 8
    assert processes[0].completion_time == 8
    assert processes[0].waiting_time == 3
    assert processes[1].completion_time == 7
    assert processes[1].waiting_time == 4


def test_rr_quantum_counts_ticks_not_work_units() -> None:
    processes = [Process(1, 0, 6), Process(2, 0, 2)]
    result = Simulator(processes, [Core.make_p_core(0)], RRScheduler(quantum=2)).run()

    assert processes[0].completion_time == 4
    assert processes[1].completion_time == 3
    assert result.finish_time == 4

