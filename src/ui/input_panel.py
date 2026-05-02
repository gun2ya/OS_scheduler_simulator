from __future__ import annotations

import random

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.core.process import Process
from src.core.processor import Core
from src.ui.theme import BURST_COLUMN_BACKGROUND, BURST_COLUMN_FOREGROUND


MAX_PROCESS_ROWS = 15
PROCESS_ROW_HEIGHT = 28
PROCESS_TABLE_HEADER_HEIGHT = 34


class InputPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumWidth(360)

        self.p_core_spin = QSpinBox()
        self.p_core_spin.setRange(0, 4)
        self.p_core_spin.setValue(1)
        self._configure_spin_box(self.p_core_spin)
        self.e_core_spin = QSpinBox()
        self.e_core_spin.setRange(0, 8)
        self.e_core_spin.setValue(1)
        self._configure_spin_box(self.e_core_spin)

        core_box = QGroupBox("Cores")
        form = QFormLayout(core_box)
        form.addRow("P cores", self.p_core_spin)
        form.addRow("E cores", self.e_core_spin)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["PID", "Arrival", "Burst"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.DoubleClicked
            | QAbstractItemView.EditTrigger.EditKeyPressed
            | QAbstractItemView.EditTrigger.AnyKeyPressed
        )
        self.table.verticalHeader().setDefaultSectionSize(PROCESS_ROW_HEIGHT)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setFixedHeight(PROCESS_TABLE_HEADER_HEIGHT)
        self.table.setMinimumHeight(
            PROCESS_TABLE_HEADER_HEIGHT + (PROCESS_ROW_HEIGHT * MAX_PROCESS_ROWS) + 8
        )
        header = self.table.horizontalHeader()
        header.setMinimumSectionSize(58)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_row())
        delete_button = QPushButton("Del")
        delete_button.clicked.connect(self.delete_selected_row)
        random_button = QPushButton("Random AT/BT")
        random_button.clicked.connect(self.randomize_timings)
        button_row = QHBoxLayout()
        button_row.addWidget(add_button)
        button_row.addWidget(delete_button)
        button_row.addWidget(random_button)

        process_box = QGroupBox("Processes")
        process_layout = QVBoxLayout(process_box)
        process_layout.addWidget(self.table)
        process_layout.addLayout(button_row)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addWidget(core_box)
        layout.addWidget(process_box, stretch=1)

        self.reset_defaults()

    def reset_defaults(self) -> None:
        self.p_core_spin.setValue(1)
        self.e_core_spin.setValue(1)
        self.table.setRowCount(0)
        for values in [(1, 0, 5), (2, 2, 8), (3, 4, 6)]:
            self.add_row(values)

    def add_row(self, values: tuple[int, int, int] | None = None) -> None:
        if not isinstance(values, tuple):
            values = None
        if values is None:
            next_pid = self.table.rowCount() + 1
            values = (next_pid, 0, 1)
        row = self.table.rowCount()
        self.table.insertRow(row)
        for column, value in enumerate(values):
            self.table.setItem(row, column, self._make_item(value, column))

    def delete_selected_row(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def randomize_timings(self) -> None:
        rng = random.Random()
        arrival_time = 0
        for row in range(self.table.rowCount()):
            if row == 0:
                arrival_time = 0
            else:
                arrival_time += rng.choice([0, 1, 1, 2, 2, 3])
            burst_time = rng.randint(1, 12)
            self.table.setItem(row, 1, self._make_item(arrival_time, 1))
            self.table.setItem(row, 2, self._make_item(burst_time, 2))

    def get_processes(self) -> list[Process]:
        if self.table.rowCount() == 0:
            raise ValueError("at least one process is required")
        if self.table.rowCount() > MAX_PROCESS_ROWS:
            raise ValueError(f"process count must be {MAX_PROCESS_ROWS} or less")

        processes: list[Process] = []
        seen_pids: set[int] = set()
        for row in range(self.table.rowCount()):
            pid = self._read_int(row, 0, "PID")
            arrival_time = self._read_int(row, 1, "Arrival")
            burst_time = self._read_int(row, 2, "Burst")
            if pid in seen_pids:
                raise ValueError(f"duplicate pid: {pid}")
            seen_pids.add(pid)
            processes.append(Process(pid, arrival_time, burst_time))
        return processes

    def get_cores(self) -> list[Core]:
        p_count = self.p_core_spin.value()
        e_count = self.e_core_spin.value()
        total = p_count + e_count
        if total < 1:
            raise ValueError("at least one core is required")
        if total > 12:
            raise ValueError("total core count must be 12 or less")

        cores: list[Core] = []
        core_id = 0
        for _ in range(p_count):
            cores.append(Core.make_p_core(core_id))
            core_id += 1
        for _ in range(e_count):
            cores.append(Core.make_e_core(core_id))
            core_id += 1
        return cores

    def _read_int(self, row: int, column: int, label: str) -> int:
        item = self.table.item(row, column)
        if item is None:
            raise ValueError(f"{label} is empty at row {row + 1}")
        try:
            value = int(item.text())
        except ValueError as exc:
            raise ValueError(f"{label} must be an integer at row {row + 1}") from exc
        if column in (0, 1) and value < 0:
            raise ValueError(f"{label} must be non-negative at row {row + 1}")
        if column == 2 and value < 1:
            raise ValueError(f"{label} must be at least 1 at row {row + 1}")
        return value

    def _make_item(self, value: int, column: int) -> QTableWidgetItem:
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

    def _configure_spin_box(self, spin_box: QSpinBox) -> None:
        spin_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        spin_box.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
