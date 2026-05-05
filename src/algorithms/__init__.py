"""Scheduling algorithms."""

from .base import Scheduler
from .custom import CustomScheduler
from .eapb import EAPBScheduler
from .fcfs import FCFSScheduler
from .hrrn import HRRNScheduler
from .rr import RRScheduler
from .spn import SPNScheduler
from .srtn import SRTNScheduler

SCHEDULERS = {
    FCFSScheduler.name: FCFSScheduler,
    RRScheduler.name: RRScheduler,
    SPNScheduler.name: SPNScheduler,
    SRTNScheduler.name: SRTNScheduler,
    HRRNScheduler.name: HRRNScheduler,
    CustomScheduler.name: CustomScheduler,
}

__all__ = [
    "CustomScheduler",
    "EAPBScheduler",
    "FCFSScheduler",
    "HRRNScheduler",
    "RRScheduler",
    "SCHEDULERS",
    "SPNScheduler",
    "SRTNScheduler",
    "Scheduler",
]
