from src.algorithms.hrrn import HRRNScheduler
from src.core.process import Process
from src.core.processor import Core
from src.core.simulator import Simulator


def test_hrrn_uses_highest_response_ratio_when_core_is_idle() -> None:
    processes = [Process(1, 0, 5), Process(2, 0, 2), Process(3, 1, 1)]
    Simulator(processes, [Core.make_e_core(0)], HRRNScheduler()).run()

    assert processes[0].completion_time == 5
    assert processes[2].completion_time == 6
    assert processes[1].completion_time == 8

