from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.simulator import SimulationResult
from src.ui.theme import BURST_COLUMN_BACKGROUND, BURST_COLUMN_FOREGROUND


class ResultTable(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["PID", "AT", "BT", "WT", "TT", "NTT"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.verticalHeader().setDefaultSectionSize(34)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.summary_label = QLabel("Total Power: - | Avg NTT: -")
        self.summary_label.setObjectName("summaryLabel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table)
        layout.addWidget(self.summary_label)

    def update_result(self, result: SimulationResult | None) -> None:
        self.table.setRowCount(0)
        if result is None:
            self.summary_label.setText("Total Power: - | Avg NTT: -")
            return

        for row, process in enumerate(sorted(result.processes, key=lambda item: item.pid)):
            self.table.insertRow(row)
            values = [
                process.pid,
                process.arrival_time,
                process.burst_time,
                process.waiting_time,
                process.turnaround_time,
                f"{process.normalized_turnaround_time:.2f}",
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, self._make_item(value, column))

        self.summary_label.setText(
            f"Total Power: {result.total_power:.1f} W*s | "
            f"Avg WT: {result.average_waiting_time:.2f} | "
            f"Avg TT: {result.average_turnaround_time:.2f} | "
            f"Avg NTT: {result.average_normalized_turnaround_time:.2f} | "
            f"Avg Mig: {result.average_migrations_per_process:.2f} | "
            f"P Util: {result.p_core_utilization_rate:.0%}"
        )

    def _make_item(self, value: int | str, column: int) -> QTableWidgetItem:
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if column == 2:
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            item.setBackground(QColor(BURST_COLUMN_BACKGROUND))
            item.setForeground(QColor(BURST_COLUMN_FOREGROUND))
            item.setToolTip("Burst Time: total CPU work units")
        return item
