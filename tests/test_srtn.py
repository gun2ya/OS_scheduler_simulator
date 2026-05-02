from src.algorithms.srtn import SRTNScheduler
from src.core.process import Process
from src.core.processor import Core
from src.core.simulator import Simulator


def test_srtn_preempts_for_shorter_remaining_time() -> None:
    processes = [Process(1, 0, 8), Process(2, 1, 2), Process(3, 2, 1)]
    Simulator(processes, [Core.make_e_core(0)], SRTNScheduler()).run()

    assert processes[1].completion_time == 3
    assert processes[2].completion_time == 4
    assert processes[0].completion_time == 11
    assert processes[0].waiting_time == 3


def test_srtn_keeps_selected_process_on_same_core() -> None:
    processes = [Process(1, 0, 5), Process(2, 0, 5), Process(3, 1, 1)]
    cores = [Core.make_p_core(0), Core.make_e_core(1)]
    result = Simulator(processes, cores, SRTNScheduler()).run()

    tick_one = {event.core_id: event.pid for event in result.events if event.time == 1}
    assert tick_one[0] == 2
    assert tick_one[1] == 3
