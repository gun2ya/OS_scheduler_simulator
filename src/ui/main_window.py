from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QRect, QSize, Qt
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QAbstractSpinBox,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from src.algorithms import (
    CustomScheduler,
    FCFSScheduler,
    HRRNScheduler,
    RRScheduler,
    SPNScheduler,
    SRTNScheduler,
)
from src.core.simulator import Simulator
from src.ui.core_status_widget import CoreStatusWidget
from src.ui.gantt_widget import GanttWidget
from src.ui.input_panel import InputPanel
from src.ui.result_table import ResultTable
from src.ui.theme import APP_STYLESHEET


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LOGO_PATH = PROJECT_ROOT / "assets" / "koreatech_logo.png"
PROCESSED_LOGO_PATH = PROJECT_ROOT / "assets" / "koreatech_logo_keyed.png"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Process Scheduling Simulator")
        self.resize(1240, 860)
        self.setMinimumSize(1100, 820)
        self.setStyleSheet(APP_STYLESHEET)

        self.scheduler_factories = {
            "FCFS": FCFSScheduler,
            "RR": lambda: RRScheduler(self.quantum_spin.value()),
            "SPN": SPNScheduler,
            "SRTN": SRTNScheduler,
            "HRRN": HRRNScheduler,
            "Custom": CustomScheduler,
        }

        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(self.scheduler_factories.keys())
        self.algorithm_combo.currentTextChanged.connect(self._sync_quantum_state)
        self.quantum_spin = QSpinBox()
        self.quantum_spin.setRange(1, 50)
        self.quantum_spin.setValue(3)
        self.quantum_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.quantum_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.PlusMinus)
        run_button = QPushButton("Run")
        run_button.clicked.connect(self.run_simulation)
        reset_button = QPushButton("Reset")
        reset_button.setObjectName("secondaryButton")
        reset_button.clicked.connect(self.reset)

        brand_title = QLabel("Scheduler Simulator")
        brand_title.setObjectName("brandTitle")
        brand_subtitle = QLabel("P/E CORE TIMELINE")
        brand_subtitle.setObjectName("brandSubtitle")
        brand = QVBoxLayout()
        brand.setContentsMargins(0, 0, 18, 0)
        brand.setSpacing(0)
        brand.addWidget(brand_title)
        brand.addWidget(brand_subtitle)

        algorithm_label = QLabel("Algorithm")
        algorithm_label.setObjectName("toolbarLabel")
        self.quantum_label = QLabel("Time-quantum = δ")
        self.quantum_label.setObjectName("toolbarLabel")
        self.logo_label = self._make_logo_label()

        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(18, 14, 18, 14)
        toolbar.setSpacing(12)
        toolbar.addLayout(brand)
        toolbar.addWidget(algorithm_label)
        toolbar.addWidget(self.algorithm_combo)
        toolbar.addWidget(self.quantum_label)
        toolbar.addWidget(self.quantum_spin)
        toolbar.addStretch(1)
        toolbar.addWidget(self.logo_label)
        toolbar.addStretch(1)
        toolbar.addWidget(run_button)
        toolbar.addWidget(reset_button)

        toolbar_widget = QWidget()
        toolbar_widget.setObjectName("toolbarWidget")
        toolbar_widget.setLayout(toolbar)

        self.input_panel = InputPanel()
        self.core_status = CoreStatusWidget()
        self.gantt = GanttWidget()
        self.results = ResultTable()

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)
        right_layout.addWidget(self._make_section_panel("Core Telemetry", self.core_status))
        right_layout.addWidget(self._make_section_panel("Execution Timeline", self.gantt), stretch=2)
        right_layout.addWidget(self._make_section_panel("Process Metrics", self.results), stretch=2)

        splitter = QSplitter()
        splitter.addWidget(self.input_panel)
        splitter.addWidget(right)
        splitter.setSizes([380, 860])

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)
        root_layout.addWidget(toolbar_widget)
        root_layout.addWidget(splitter, stretch=1)
        self.setCentralWidget(root)

        self._sync_quantum_state(self.algorithm_combo.currentText())
        self.core_status.update_result(None)
        self.results.update_result(None)

    def _make_logo_label(self) -> QLabel:
        label = QLabel()
        label.setObjectName("topLogo")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setMinimumSize(QSize(240, 70))
        label.setMaximumSize(QSize(340, 96))

        pixmap = self._load_logo_pixmap()
        if not pixmap.isNull():
            label.setPixmap(
                pixmap.scaled(
                    label.maximumSize(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
        else:
            label.setText("KOREATECH")
        return label

    def _load_logo_pixmap(self) -> QPixmap:
        if PROCESSED_LOGO_PATH.exists():
            return QPixmap(str(PROCESSED_LOGO_PATH))

        image = QImage(str(LOGO_PATH))
        if image.isNull():
            return QPixmap()

        image = image.convertToFormat(QImage.Format.Format_ARGB32)
        keyed = self._chroma_key_dark_background(image)
        trimmed = self._trim_transparent_edges(keyed)
        trimmed.save(str(PROCESSED_LOGO_PATH))
        return QPixmap.fromImage(trimmed)

    def _chroma_key_dark_background(self, image: QImage) -> QImage:
        keyed = QImage(image)
        for y in range(keyed.height()):
            for x in range(keyed.width()):
                color = keyed.pixelColor(x, y)
                red = color.red()
                green = color.green()
                blue = color.blue()
                original_alpha = color.alpha()
                max_channel = max(red, green, blue)

                if max_channel <= 22:
                    alpha = 0
                elif max_channel < 82:
                    alpha = int(original_alpha * ((max_channel - 22) / 60) ** 1.45)
                else:
                    alpha = original_alpha

                if alpha != original_alpha:
                    keyed.setPixelColor(x, y, QColor(red, green, blue, alpha))
        return keyed

    def _trim_transparent_edges(self, image: QImage) -> QImage:
        threshold = 56
        left = image.width()
        right = -1
        top = image.height()
        bottom = -1

        for y in range(image.height()):
            for x in range(image.width()):
                if image.pixelColor(x, y).alpha() > threshold:
                    left = min(left, x)
                    right = max(right, x)
                    top = min(top, y)
                    bottom = max(bottom, y)

        if right < left or bottom < top:
            return image

        padding = 18
        left = max(0, left - padding)
        top = max(0, top - padding)
        right = min(image.width() - 1, right + padding)
        bottom = min(image.height() - 1, bottom + padding)
        return image.copy(QRect(left, top, right - left + 1, bottom - top + 1))

    def _make_section_panel(self, title: str, child: QWidget) -> QFrame:
        panel = QFrame()
        panel.setObjectName("sectionPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(10)

        title_label = QLabel(title)
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)
        layout.addWidget(child, stretch=1)
        return panel

    def run_simulation(self) -> None:
        try:
            processes = self.input_panel.get_processes()
            cores = self.input_panel.get_cores()
            scheduler = self.scheduler_factories[self.algorithm_combo.currentText()]()
            result = Simulator(processes, cores, scheduler).run()
        except Exception as exc:
            QMessageBox.warning(self, "Simulation failed", str(exc))
            return

        self.core_status.update_result(result)
        self.gantt.update_result(result)
        self.results.update_result(result)

    def reset(self) -> None:
        self.input_panel.reset_defaults()
        self.core_status.update_result(None)
        self.gantt.update_result(None)
        self.results.update_result(None)

    def _sync_quantum_state(self, algorithm_name: str) -> None:
        is_rr = algorithm_name == "RR"
        self.quantum_label.setVisible(is_rr)
        self.quantum_spin.setVisible(is_rr)
        self.quantum_spin.setEnabled(is_rr)
