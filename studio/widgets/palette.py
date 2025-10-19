from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget


class PaletteWidget(QListWidget):
    fieldDropped = pyqtSignal(str, str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.setViewMode(self.ViewMode.ListMode)
        self.setSpacing(4)
        self.populate_default()

    def populate_default(self) -> None:
        fields = [
            ("username", "Username"),
            ("rank", "Rank"),
            ("discordId", "Discord ID"),
            ("region", "Region"),
            ("joinDate", "Join Date"),
            ("LOAcheckbox", "LOA"),
            ("notes", "Notes"),
            ("phase", "Phase"),
        ]
        for key, label in fields:
            it = QListWidgetItem(label)
            it.setData(Qt.ItemDataRole.UserRole, key)
            self.addItem(it)

    def startDrag(self, supportedActions: Qt.DropAction) -> None:  # type: ignore[override]
        it = self.currentItem()
        if it is None:
            return
        key = str(it.data(Qt.ItemDataRole.UserRole))
        label = it.text()
        self.fieldDropped.emit(key, label)

