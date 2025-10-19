from __future__ import annotations

import sys

from .app import StudioApp
from .main_window import MainWindow


def main() -> int:
    app = StudioApp()
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
