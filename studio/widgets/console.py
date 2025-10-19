from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QPlainTextEdit, QWidget

from ..io.validators import ValidationIssue


class ConsoleWidget(QPlainTextEdit):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")

    def append_issue(self, issue: ValidationIssue) -> None:
        color = {"error": "#e03131", "warning": "#f08c00", "info": "#1971c2"}.get(issue.level, "#343a40")
        self.appendHtml(f"<span style='color:{color};'>[{issue.level.upper()}]</span> <b>{issue.path}</b>: {issue.message}")

    def show_issues(self, issues: List[ValidationIssue]) -> None:
        self.clear()
        if not issues:
            self.appendHtml("<span style='color:#2b8a3e;'><b>No issues found.</b></span>")
            return
        for i in issues:
            self.append_issue(i)
