from __future__ import annotations

import matplotlib

matplotlib.use("QtAgg")
matplotlib.rcParams["font.family"] = "Arial"

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import to_rgb
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from src.core.event import ScheduleEvent
from src.core.simulator import SimulationResult
from src.ui.theme import (
    CHART_BACKGROUND,
    CHART_GRID,
    CHART_IDLE,
    CHART_PANEL,
    CHART_TEXT,
    PROCESS_COLORS,
)


class GanttWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.figure = Figure(figsize=(7, 3), facecolor=CHART_BACKGROUND)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.update_result(None)

    def update_result(self, result: SimulationResult | None) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)

        if result is None or not result.events:
            axis.set_facecolor(CHART_PANEL)
            axis.text(0.5, 0.5, "No simulation result", ha="center", va="center", color=CHART_TEXT)
            axis.set_axis_off()
            self.canvas.draw_idle()
            return

        axis.set_facecolor(CHART_PANEL)
        axis.set_title("Gantt Chart", loc="left", fontweight="bold", color=CHART_TEXT)
        axis.set_xlabel("Time")
        axis.set_ylabel("")
        axis.xaxis.label.set_color(CHART_TEXT)

        grouped = self._merge_events(result.events)
        core_ids = [core.core_id for core in result.cores]
        core_to_y = {core_id: index for index, core_id in enumerate(core_ids)}
        core_labels = {core.core_id: f"{core.core_type}{core.core_id}" for core in result.cores}

        for event in grouped:
            y = core_to_y[event.core_id]
            if event.pid is None:
                facecolor = CHART_IDLE
                edgecolor = "#394256"
                label = ""
            else:
                facecolor = PROCESS_COLORS[event.pid % len(PROCESS_COLORS)]
                edgecolor = CHART_PANEL
                label = f"P{event.pid}"
            axis.add_patch(
                Rectangle(
                    (event.time, y - 0.35),
                    event.duration,
                    0.7,
                    facecolor=facecolor,
                    edgecolor=edgecolor,
                    linewidth=0.8,
                )
            )
            if event.pid is not None and event.duration >= 1:
                text_color = self._label_color_for(facecolor)
                axis.text(
                    event.time + event.duration / 2,
                    y,
                    label,
                    ha="center",
                    va="center",
                    fontsize=8,
                    fontweight="bold",
                    color=text_color,
                )

        axis.set_xlim(0, max(event.time + event.duration for event in grouped))
        axis.set_ylim(-0.75, len(core_ids) - 0.25)
        axis.set_yticks(list(core_to_y.values()))
        axis.set_yticklabels([core_labels[core_id] for core_id in core_ids])
        axis.tick_params(axis="x", colors="#c8c0b2", pad=5)
        axis.tick_params(axis="y", colors="#c8c0b2", pad=8, labelsize=10)
        axis.grid(axis="x", linestyle=":", color=CHART_GRID)
        for spine in axis.spines.values():
            spine.set_color("#303746")
        self.figure.subplots_adjust(left=0.085, right=0.985, top=0.84, bottom=0.18)
        self.canvas.draw_idle()

    def _label_color_for(self, color: str) -> str:
        red, green, blue = to_rgb(color)
        luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        return "#171714" if luminance > 0.48 else "#f3ead9"

    def _merge_events(self, events: list[ScheduleEvent]) -> list[ScheduleEvent]:
        merged: list[ScheduleEvent] = []
        for event in sorted(events, key=lambda item: (item.core_id, item.time)):
            if (
                merged
                and merged[-1].core_id == event.core_id
                and merged[-1].pid == event.pid
                and merged[-1].time + merged[-1].duration == event.time
            ):
                previous = merged[-1]
                merged[-1] = ScheduleEvent(
                    previous.time,
                    previous.duration + event.duration,
                    previous.core_id,
                    previous.pid,
                )
            else:
                merged.append(event)
        return merged
