from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.simulator import SimulationResult


class CoreStatusWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.empty_label = QLabel("Run a simulation to see core activity.")
        self.empty_label.setObjectName("metricLabel")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table = QTableWidget(0, 4)
        self.table.setObjectName("telemetryTable")
        self.table.setHorizontalHeaderLabels(["Core", "Active", "Startup", "Energy"])
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.horizontalHeader().setFixedHeight(34)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.empty_label)
        layout.addWidget(self.table)

    def update_result(self, result: SimulationResult | None) -> None:
        self.table.setRowCount(0)
        if result is None:
            self.table.hide()
            self.empty_label.show()
            return

        self.empty_label.hide()
        self.table.show()
        reports = {report.core_id: report for report in result.power_report.cores}
        for row, core in enumerate(result.cores):
            report = reports[core.core_id]
            self.table.insertRow(row)
            values = [
                f"{core.core_type}{core.core_id}",
                f"{report.active_time}s",
                str(report.startup_count),
                f"{report.total_energy:.1f} W*s",
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, self._make_item(value, core.core_type, column))

    def _make_item(self, value: str, core_type: str, column: int) -> QTableWidgetItem:
        item = QTableWidgetItem(value)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        if column == 0:
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            if core_type == "P":
                item.setBackground(QColor("#4a3927"))
                item.setForeground(QColor("#e1c07d"))
            else:
                item.setBackground(QColor("#334233"))
                item.setForeground(QColor("#c3d0ac"))
        return item
