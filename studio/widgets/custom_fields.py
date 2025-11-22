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


class CustomFieldsEditor(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Key", "Label", "Default", "Type", "Required"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.SelectedClicked)

        self.btn_add = QPushButton("Add Field")
        self.btn_remove = QPushButton("Remove")
        self.btn_add.clicked.connect(self._add)
        self.btn_remove.clicked.connect(self._remove)

        v = QVBoxLayout(self)
        v.addWidget(self.table, 1)
        h = QHBoxLayout()
        h.addWidget(self.btn_add)
        h.addWidget(self.btn_remove)
        v.addLayout(h)

    def set_fields(self, fields: List[dict]) -> None:
        self.table.setRowCount(0)
        for f in fields:
            self._append_row(
                f.get("key", ""),
                f.get("label", ""),
                str(f.get("defaultValue", "")),
                f.get("type", "string"),
                "yes" if f.get("required", False) else "no",
            )

    def fields(self) -> List[dict]:
        out: List[dict] = []
        for row in range(self.table.rowCount()):
            key = self.table.item(row, 0).text().strip()
            label = self.table.item(row, 1).text().strip()
            default = self.table.item(row, 2).text().strip()
            typ = self.table.item(row, 3).text().strip() or "string"
            req = self.table.item(row, 4).text().strip().lower() in {"yes", "true", "1"}
            if key:
                out.append({"key": key, "label": label or key, "defaultValue": default, "type": typ, "required": req})
        return out

    def _append_row(self, key: str, label: str, default: str, typ: str, required: str) -> None:
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(key))
        self.table.setItem(r, 1, QTableWidgetItem(label))
        self.table.setItem(r, 2, QTableWidgetItem(default))
        self.table.setItem(r, 3, QTableWidgetItem(typ))
        self.table.setItem(r, 4, QTableWidgetItem(required))

    def _add(self) -> None:
        key, ok = QInputDialog.getText(self, "Add Field", "Key:", QLineEdit.EchoMode.Normal, "customKey")
        if not ok or not key:
            return
        label, ok = QInputDialog.getText(self, "Add Field", "Label:", QLineEdit.EchoMode.Normal, key)
        if not ok:
            return
        self._append_row(key, label, "", "string", "no")

    def _remove(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
