from src.algorithms.custom import CustomScheduler
from src.algorithms.eapb import EAPBScheduler
from src.core.process import Process
from src.core.processor import Core
from src.core.simulator import Simulator


def test_eapb_priority_is_normalized_and_waiting_sensitive() -> None:
    scheduler = EAPBScheduler()
    cores = [Core.make_e_core(0)]
    fresh = Process(1, 0, 10)
    waiting = Process(2, 0, 10)
    waiting.waiting_time = 20
    ready = [fresh, waiting]

    fresh_priority = scheduler.priority(fresh, ready, cores)
    waiting_priority = scheduler.priority(waiting, ready, cores)

    assert 0 <= fresh_priority <= 1
    assert 0 <= waiting_priority <= 1
    assert waiting_priority > fresh_priority


def test_eapb_edp_prefers_e_core_for_one_tick_job() -> None:
    scheduler = EAPBScheduler()
    process = Process(1, 0, 1)
    p_core = Core.make_p_core(0)
    e_core = Core.make_e_core(1)

    assert scheduler.cost(process, e_core, current_time=0) < scheduler.cost(
        process, p_core, current_time=0
    )


def test_eapb_edp_prefers_p_core_for_long_job() -> None:
    scheduler = EAPBScheduler()
    process = Process(1, 0, 8)
    p_core = Core.make_p_core(0)
    e_core = Core.make_e_core(1)

    assert scheduler.cost(process, p_core, current_time=0) < scheduler.cost(
        process, e_core, current_time=0
    )


def test_eapb_migration_cost_only_applies_when_core_changes() -> None:
    scheduler = EAPBScheduler()
    process = Process(1, 0, 5)
    process.last_core_id = 0
    same_core = Core.make_e_core(0)
    other_core = Core.make_e_core(1)

    assert scheduler.migration_cost(process, same_core, current_time=2) == 0
    assert scheduler.migration_cost(process, other_core, current_time=2) > 0


def test_custom_scheduler_assigns_short_job_to_e_and_long_job_to_p() -> None:
    processes = [Process(1, 0, 8), Process(2, 0, 1)]
    cores = [Core.make_p_core(0), Core.make_e_core(1)]
    result = Simulator(processes, cores, CustomScheduler()).run()

    first_tick = {event.core_id: event.pid for event in result.events if event.time == 0}
    assert first_tick == {0: 1, 1: 2}


def test_eapb_starvation_preemption_after_minimum_run() -> None:
    scheduler = EAPBScheduler()
    running = Process(1, 0, 20, remaining=18)
    waiting = Process(2, 0, 2)
    waiting.waiting_time = 8
    core = Core.make_e_core(0)
    core.current_pid = running.pid
    core.was_idle = False
    core.run_ticks = scheduler.MIN_RUN_TICKS

    assignment = scheduler.select([running, waiting], [core], current_time=2)

    assert assignment == {0: waiting.pid}


def test_eapb_does_not_preempt_before_minimum_run() -> None:
    scheduler = EAPBScheduler()
    running = Process(1, 0, 20, remaining=19)
    waiting = Process(2, 0, 2)
    waiting.waiting_time = 8
    core = Core.make_e_core(0)
    core.current_pid = running.pid
    core.was_idle = False
    core.run_ticks = scheduler.MIN_RUN_TICKS - 1

    assignment = scheduler.select([running, waiting], [core], current_time=1)

    assert assignment == {0: running.pid}


def test_simulator_tracks_run_ticks_and_last_core_id_for_eapb() -> None:
    process = Process(1, 0, 3)
    core = Core.make_e_core(0)
    result = Simulator([process], [core], CustomScheduler()).run()

    assert process.last_core_id == 0
    assert result.average_migrations_per_process == 0
    assert core.run_ticks == 0
