from __future__ import annotations

from typing import List, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class RanksEditor(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Abbr", "Name"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)

        self.btn_add = QPushButton("Add Rank")
        self.btn_remove = QPushButton("Remove")
        self.btn_up = QPushButton("Up")
        self.btn_down = QPushButton("Down")

        self.btn_add.clicked.connect(self._add)
        self.btn_remove.clicked.connect(self._remove)
        self.btn_up.clicked.connect(self._up)
        self.btn_down.clicked.connect(self._down)

        v = QVBoxLayout(self)
        v.addWidget(self.table, 1)
        h = QHBoxLayout()
        h.addWidget(self.btn_add)
        h.addWidget(self.btn_remove)
        h.addWidget(self.btn_up)
        h.addWidget(self.btn_down)
        v.addLayout(h)

    def set_ranks(self, ranks: List[dict]) -> None:
        self.table.setRowCount(0)
        for r in ranks:
            self._append_row(r.get("abbr", ""), r.get("name", ""))

    def ranks(self) -> List[dict]:
        out: List[dict] = []
        for row in range(self.table.rowCount()):
            ab = self.table.item(row, 0).text().strip()
            name = self.table.item(row, 1).text().strip()
            if ab and name:
                out.append({"abbr": ab, "name": name})
        return out

    def _append_row(self, abbr: str, name: str) -> None:
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(abbr))
        self.table.setItem(r, 1, QTableWidgetItem(name))

    def _add(self) -> None:
        ab, ok = QInputDialog.getText(self, "Add Rank", "Abbreviation:", QLineEdit.EchoMode.Normal, "NEW")
        if not ok or not ab:
            return
        name, ok = QInputDialog.getText(self, "Add Rank", "Name:", QLineEdit.EchoMode.Normal, "New Rank")
        if not ok or not name:
            return
        self._append_row(ab, name)

    def _remove(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def _up(self) -> None:
        row = self.table.currentRow()
        if row > 0:
            self._swap_rows(row, row - 1)
            self.table.selectRow(row - 1)

    def _down(self) -> None:
        row = self.table.currentRow()
        if 0 <= row < self.table.rowCount() - 1:
            self._swap_rows(row, row + 1)
            self.table.selectRow(row + 1)

    def _swap_rows(self, a: int, b: int) -> None:
        for col in range(self.table.columnCount()):
            ia = self.table.item(a, col)
            ib = self.table.item(b, col)
            ta = ia.text() if ia else ""
            tb = ib.text() if ib else ""
            self.table.setItem(a, col, QTableWidgetItem(tb))
            self.table.setItem(b, col, QTableWidgetItem(ta))
