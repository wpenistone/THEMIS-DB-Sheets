from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..designer.items import FieldItem
from ..designer.canvas import CanvasView


class InspectorWidget(QWidget):
    def __init__(self, canvas: CanvasView, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.canvas = canvas
        self._item: Optional[FieldItem] = None

        self.title = QLabel("Inspector")
        self.title.setStyleSheet("font-weight: bold; font-size: 14px; padding: 6px;")

        self.key_edit = QLineEdit()
        self.label_edit = QLineEdit()
        self.row_spin = QSpinBox()
        self.col_spin = QSpinBox()
        self.width_spin = QSpinBox()
        self.height_spin = QSpinBox()
        for sp in (self.row_spin, self.col_spin, self.width_spin, self.height_spin):
            sp.setRange(0, 10000)

        form = QFormLayout()
        form.addRow("Key", self.key_edit)
        form.addRow("Label", self.label_edit)
        form.addRow("Row", self.row_spin)
        form.addRow("Column", self.col_spin)
        form.addRow("Width", self.width_spin)
        form.addRow("Height", self.height_spin)
        group = QGroupBox("Field")
        group.setLayout(form)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.clicked.connect(self._apply)

        layout = QVBoxLayout(self)
        layout.addWidget(self.title)
        layout.addWidget(group)
        layout.addWidget(self.apply_btn)
        layout.addStretch(1)

        self.canvas.selectionChanged.connect(self._on_selection)
        self._on_selection()

    def _on_selection(self) -> None:
        items = self.canvas.selected_items()
        self._item = items[0] if items else None
        self._refresh()

    def _refresh(self) -> None:
        if self._item is None:
            self.key_edit.setEnabled(False)
            self.label_edit.setEnabled(False)
            self.row_spin.setEnabled(False)
            self.col_spin.setEnabled(False)
            self.width_spin.setEnabled(False)
            self.height_spin.setEnabled(False)
            self.key_edit.setText("")
            self.label_edit.setText("")
            self.row_spin.setValue(0)
            self.col_spin.setValue(0)
            self.width_spin.setValue(0)
            self.height_spin.setValue(0)
            return
        self.key_edit.setEnabled(True)
        self.label_edit.setEnabled(True)
        self.row_spin.setEnabled(True)
        self.col_spin.setEnabled(True)
        self.width_spin.setEnabled(True)
        self.height_spin.setEnabled(True)
        item = self._item
        self.key_edit.setText(item.key())
        self.label_edit.setText(item.label())
        cw = self.canvas.scene().grid.cell_width
        ch = self.canvas.scene().grid.cell_height
        r, c = item.cell(cw, ch)
        self.row_spin.setValue(r)
        self.col_spin.setValue(c)
        self.width_spin.setValue(int(item.rect().width()))
        self.height_spin.setValue(int(item.rect().height()))

    def _apply(self) -> None:
        item = self._item
        if item is None:
            return
        item.set_key(self.key_edit.text().strip())
        item.set_label(self.label_edit.text().strip())
        cw = self.canvas.scene().grid.cell_width
        ch = self.canvas.scene().grid.cell_height
        row = self.row_spin.value()
        col = self.col_spin.value()
        item.set_cell(row, col, cw, ch)
        item.setRect(0, 0, float(self.width_spin.value()), float(self.height_spin.value()))
        self.canvas.viewport().update()
