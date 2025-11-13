from __future__ import annotations

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QColor, QPainter


class SheetGrid:
    def __init__(self) -> None:
        self.visible = True
        self.cell_width = 80.0
        self.cell_height = 24.0
        self.major_step = 5
        self.color_minor = QColor(230, 230, 230)
        self.color_major = QColor(210, 210, 210)

    def draw(self, p: QPainter, rect: QRectF) -> None:
        if not self.visible:
            return
        left = int(rect.left() // self.cell_width) - 1
        right = int(rect.right() // self.cell_width) + 1
        top = int(rect.top() // self.cell_height) - 1
        bottom = int(rect.bottom() // self.cell_height) + 1
        p.setPen(self.color_minor)
        for c in range(left, right + 1):
            x = c * self.cell_width
            p.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
        for r in range(top, bottom + 1):
            y = r * self.cell_height
            p.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
        p.setPen(self.color_major)
        for c in range(left, right + 1):
            if c % self.major_step == 0:
                x = c * self.cell_width
                p.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
        for r in range(top, bottom + 1):
            if r % self.major_step == 0:
                y = r * self.cell_height
                p.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))

    def snap_point(self, pos: QPointF) -> QPointF:
        x = round(pos.x() / self.cell_width) * self.cell_width
        y = round(pos.y() / self.cell_height) * self.cell_height
        return QPointF(x, y)

    def cell_at(self, pos: QPointF) -> tuple[int, int]:
        col = int(round(pos.x() / self.cell_width))
        row = int(round(pos.y() / self.cell_height))
        return row, col

    def pos_for_cell(self, row: int, col: int) -> QPointF:
        return QPointF(col * self.cell_width, row * self.cell_height)
