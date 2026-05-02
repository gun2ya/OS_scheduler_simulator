from src.algorithms.spn import SPNScheduler
from src.core.process import Process
from src.core.processor import Core
from src.core.simulator import Simulator


def test_spn_keeps_running_job_and_then_picks_shortest() -> None:
    processes = [Process(1, 0, 8), Process(2, 1, 2), Process(3, 1, 1)]
    Simulator(processes, [Core.make_e_core(0)], SPNScheduler()).run()

    assert processes[0].completion_time == 8
    assert processes[2].completion_time == 9
    assert processes[1].completion_time == 11
    assert processes[2].waiting_time == 7

