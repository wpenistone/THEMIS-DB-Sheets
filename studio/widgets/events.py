from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class EventTypesEditor(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Name", "Aliases (comma-separated)"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)

        self.btn_add = QPushButton("Add Type")
        self.btn_remove = QPushButton("Remove")
        self.btn_add.clicked.connect(self._add)
        self.btn_remove.clicked.connect(self._remove)

        v = QVBoxLayout(self)
        v.addWidget(self.table, 1)
        h = QHBoxLayout()
        h.addWidget(self.btn_add)
        h.addWidget(self.btn_remove)
        v.addLayout(h)

    def set_event_types(self, types: List[dict]) -> None:
        self.table.setRowCount(0)
        for t in types:
            self._append_row(t.get("name", ""), ", ".join(t.get("aliases", [])))

    def event_types(self) -> List[dict]:
        out: List[dict] = []
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().strip()
            aliases = [x.strip() for x in (self.table.item(row, 1).text() if self.table.item(row, 1) else "").split(",") if x.strip()]
            if name:
                out.append({"name": name, "aliases": aliases})
        return out

    def _append_row(self, name: str, aliases: str) -> None:
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(name))
        self.table.setItem(r, 1, QTableWidgetItem(aliases))

    def _add(self) -> None:
        name, ok = QInputDialog.getText(self, "Add Event Type", "Name:", QLineEdit.EchoMode.Normal, "New Event")
        if not ok or not name:
            return
        self._append_row(name, "")

    def _remove(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
