from src.algorithms.fcfs import FCFSScheduler
from src.core.process import Process
from src.core.processor import Core
from src.core.simulator import Simulator


def test_power_model_counts_active_ticks_and_idle_to_active_startup() -> None:
    processes = [Process(1, 0, 2), Process(2, 3, 1)]
    result = Simulator(processes, [Core.make_e_core(0)], FCFSScheduler()).run()
    report = result.power_report.cores[0]

    assert report.active_time == 3
    assert report.startup_count == 2
    assert report.total_energy == 3.2


def test_mixed_core_power_total() -> None:
    processes = [Process(1, 0, 2), Process(2, 0, 1)]
    result = Simulator(
        processes,
        [Core.make_p_core(0), Core.make_e_core(1)],
        FCFSScheduler(),
    ).run()

    assert round(result.total_power, 1) == 5.6

