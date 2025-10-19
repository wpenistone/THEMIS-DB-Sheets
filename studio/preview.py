from __future__ import annotations

from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QPoint, QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QDialog, QGridLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget


class GridWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.cell_w = 80
        self.cell_h = 24
        self._fields: List[Dict[str, Any]] = []
        self.setMinimumSize(1600, 1200)

    def set_fields(self, fields: List[Dict[str, Any]]) -> None:
        self._fields = fields
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        p = QPainter(self)
        r = self.rect()
        p.fillRect(r, QColor("#ffffff"))
        p.setPen(QColor(235, 235, 235))
        for x in range(0, r.width(), self.cell_w):
            p.drawLine(x, 0, x, r.bottom())
        for y in range(0, r.height(), self.cell_h):
            p.drawLine(0, y, r.right(), y)
        p.setPen(QPen(QColor(210, 210, 210), 1))
        step = 5
        for x in range(0, r.width(), self.cell_w * step):
            p.drawLine(x, 0, x, r.bottom())
        for y in range(0, r.height(), self.cell_h * step):
            p.drawLine(0, y, r.right(), y)
        for f in self._fields:
            row = int(f.get("row", 0))
            col = int(f.get("col", 0))
            x = col * self.cell_w
            y = row * self.cell_h
            w = self.cell_w * 2
            h = int(self.cell_h * 1.5)
            rect = QRect(x, y, w, h)
            p.setBrush(QColor("#f1f3f5"))
            p.setPen(QColor("#adb5bd"))
            p.drawRoundedRect(rect, 3, 3)
            p.setPen(QColor("#212529"))
            p.drawText(rect.adjusted(6, 4, -6, -4), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, f.get("label", f.get("key", "")))


class PreviewDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Preview")
        self.resize(900, 600)
        self._grid = GridWidget()
        scroll = QScrollArea()
        scroll.setWidget(self._grid)
        scroll.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

    def set_fields(self, fields: List[Dict[str, Any]]) -> None:
        self._grid.set_fields(fields)

    def set_cell_size(self, w: int, h: int) -> None:
        self._grid.cell_w = max(8, int(w))
        self._grid.cell_h = max(8, int(h))
        self._grid.update()
