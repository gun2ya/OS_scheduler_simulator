from __future__ import annotations

import sys

def main() -> int:
    try:
        from PyQt6.QtWidgets import QApplication

        from src.ui.main_window import MainWindow
    except ImportError as exc:
        print("PyQt6/matplotlib UI dependencies are missing.")
        print("Install them with: pip install -r requirements.txt")
        print(f"Import error: {exc}")
        return 1

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

