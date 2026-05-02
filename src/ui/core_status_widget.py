from __future__ import annotations

from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from src.core.simulator import SimulationResult


class CoreStatusWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.grid = QGridLayout(self)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(8)

    def update_result(self, result: SimulationResult | None) -> None:
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if result is None:
            empty = QLabel("Run a simulation to see core activity.")
            empty.setObjectName("metricLabel")
            self.grid.addWidget(empty, 0, 0)
            return

        reports = {report.core_id: report for report in result.power_report.cores}
        for index, core in enumerate(result.cores):
            report = reports[core.core_id]
            frame = QFrame()
            frame.setObjectName("coreCard")
            frame.setProperty("coreType", core.core_type)
            frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(12, 10, 12, 10)
            layout.setSpacing(4)

            title = QLabel(f"{core.core_type} Core {core.core_id}")
            title.setObjectName("coreTitle")
            active = QLabel(f"Active {report.active_time}s")
            startup = QLabel(f"Startup {report.startup_count}")
            energy = QLabel(f"{report.total_energy:.1f} W*s")
            for label in (active, startup, energy):
                label.setObjectName("metricLabel")

            layout.addWidget(title)
            layout.addWidget(active)
            layout.addWidget(startup)
            layout.addWidget(energy)
            self.grid.addWidget(frame, index // 4, index % 4)
