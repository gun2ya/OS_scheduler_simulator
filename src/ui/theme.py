from __future__ import annotations


APP_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #23231f;
    color: #d9d2c3;
    font-family: "Arial", "Helvetica";
    font-size: 14px;
}

QLabel {
    background: transparent;
}

QWidget#appRoot {
    background-color: #23231f;
}

QWidget#toolbarWidget {
    background-color: qlineargradient(
        x1: 0, y1: 0, x2: 1, y2: 1,
        stop: 0 #373326,
        stop: 0.58 #30302b,
        stop: 1 #2b342d
    );
    border: 1px solid #5e5848;
    border-radius: 14px;
    min-height: 112px;
}

QLabel#brandTitle {
    color: #eee7d7;
    font-size: 19px;
    font-weight: 900;
    letter-spacing: 0;
}

QLabel#brandSubtitle {
    color: #aeb89c;
    font-size: 11px;
    font-weight: 700;
}

QLabel#toolbarLabel {
    color: #c8c0b2;
    font-weight: 700;
}

QLabel#topLogo {
    background-color: rgba(0, 0, 0, 0);
    padding: 0;
}

QFrame#sectionPanel {
    background-color: #30302b;
    border: 1px solid #575143;
    border-radius: 12px;
}

QLabel#sectionTitle {
    color: #e9dfcc;
    font-size: 14px;
    font-weight: 900;
}

QGroupBox {
    background-color: #2c2c27;
    border: 1px solid #554f43;
    border-radius: 12px;
    font-weight: 700;
    margin-top: 14px;
    padding: 16px 10px 10px 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 4px;
    color: #bcc5a6;
}

QComboBox, QSpinBox {
    background-color: #1f211f;
    border: 1px solid #6a6251;
    border-radius: 8px;
    color: #eee6d8;
    min-height: 34px;
    padding: 2px 8px;
}

QSpinBox {
    padding-right: 38px;
}

QSpinBox#quantumSpin {
    min-width: 92px;
    min-height: 38px;
    padding: 2px 40px 2px 10px;
    font-size: 15px;
    font-weight: 900;
}

QSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 32px;
    background-color: #c4b37f;
    border-left: 1px solid #6a6251;
    border-top-right-radius: 7px;
}

QSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 32px;
    background-color: #aeb89c;
    border-left: 1px solid #6a6251;
    border-bottom-right-radius: 7px;
}

QSpinBox::up-button:hover {
    background-color: #d6c591;
}

QSpinBox::down-button:hover {
    background-color: #c0c9ae;
}

QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
    background-color: #9c8d6f;
}

QSpinBox#quantumSpin::up-button,
QSpinBox#quantumSpin::down-button {
    width: 34px;
}

QComboBox:focus, QSpinBox:focus {
    border: 1px solid #d0bd87;
}

QPushButton {
    background-color: #c4b37f;
    border: 1px solid #d9c895;
    border-radius: 9px;
    color: #151411;
    font-weight: 900;
    min-height: 32px;
    padding: 4px 16px;
}

QPushButton:hover {
    background-color: #d2c08a;
}

QPushButton:pressed {
    background-color: #aa9560;
}

QPushButton#secondaryButton {
    background-color: #30302b;
    border: 1px solid #6a6251;
    color: #ddd4c4;
}

QPushButton#secondaryButton:hover {
    background-color: #3a3932;
}

QLabel#summaryLabel {
    color: #d0bd87;
    font-weight: 700;
    padding: 8px 2px 0 2px;
}

QFrame#coreCard {
    background-color: #383730;
    border: 1px solid #615a4b;
    border-radius: 12px;
}

QFrame#coreCard[coreType="P"] {
    background-color: #3f3527;
    border: 1px solid #c4a266;
}

QFrame#coreCard[coreType="E"] {
    background-color: #2d3a30;
    border: 1px solid #9caf8a;
}

QLabel#coreTitle {
    color: #eee7d7;
    font-size: 15px;
    font-weight: 800;
}

QLabel#metricLabel {
    color: #c5bdae;
    font-size: 12px;
}

QTableWidget#telemetryTable {
    border-radius: 8px;
}

QTableWidget#telemetryTable::item {
    padding: 5px 6px;
}

QTableWidget {
    background-color: #20221f;
    border: 1px solid #595244;
    border-radius: 10px;
    color: #ddd5c7;
    gridline-color: #444238;
    alternate-background-color: #282a25;
    selection-background-color: #5b6248;
    selection-color: #f6eddd;
}

QTableWidget::item {
    padding: 4px;
}

QHeaderView::section {
    background-color: #3a382f;
    border: 0;
    border-right: 1px solid #595244;
    border-bottom: 1px solid #595244;
    color: #d0bd87;
    font-weight: 700;
    padding: 8px 6px;
}

QSplitter::handle {
    background-color: #464237;
}
"""


BURST_COLUMN_BACKGROUND = "#373b2e"
BURST_COLUMN_FOREGROUND = "#d4c289"

CHART_BACKGROUND = "#30302b"
CHART_PANEL = "#20221f"
CHART_TEXT = "#ddd5c7"
CHART_GRID = "#48463d"
CHART_IDLE = "#34362f"
PROCESS_COLORS = [
    "#9caf8a",
    "#d0bd87",
    "#b97862",
    "#7894a3",
    "#9480aa",
    "#bf914f",
    "#6f9a88",
    "#a46d78",
    "#8e958f",
    "#a88f58",
]
