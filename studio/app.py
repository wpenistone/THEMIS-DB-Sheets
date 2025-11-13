from __future__ import annotations

import os
import sys
from typing import Optional

from PyQt6.QtWidgets import QApplication


class StudioApp(QApplication):
    def __init__(self, argv: Optional[list[str]] = None) -> None:
        super().__init__(argv or sys.argv)
        self.setApplicationName("THEMIS Configuration Studio")
        self.setOrganizationName("THEMIS")
        self.setOrganizationDomain("themis.local")
        self._apply_style()

    def _apply_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow { background: #f8f9fa; }
            QToolBar { background: #f1f3f5; spacing: 6px; }
            QStatusBar { background: #f1f3f5; }
            QDockWidget::title { background: #dee2e6; padding: 4px; }
            QTreeWidget, QListWidget, QPlainTextEdit, QTextEdit { background: white; }
            QGroupBox { border: 1px solid #dee2e6; border-radius: 4px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QPushButton { background: #339af0; color: white; border: 0; padding: 6px 10px; border-radius: 4px; }
            QPushButton:hover { background: #228be6; }
            QPushButton:disabled { background: #ced4da; color: #495057; }
            """
        )
