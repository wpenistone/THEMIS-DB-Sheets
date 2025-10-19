from __future__ import annotations

from typing import Iterable, List, Tuple

from PyQt6.QtCore import QPointF, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen


class SnapGuide:
    def __init__(self) -> None:
        self.lines: List[Tuple[QPointF, QPointF]] = []
        self.color = QColor("#845ef7")

    def clear(self) -> None:
        self.lines.clear()

    def add_vertical(self, x: float, y1: float, y2: float) -> None:
        self.lines.append((QPointF(x, y1), QPointF(x, y2)))

    def add_horizontal(self, y: float, x1: float, x2: float) -> None:
        self.lines.append((QPointF(x1, y), QPointF(x2, y)))

    def draw(self, p: QPainter) -> None:
        if not self.lines:
            return
        pen = QPen(self.color, 1.5)
        p.setPen(pen)
        for a, b in self.lines:
            p.drawLine(a, b)


def compute_alignment_guides(moving_rect: QRectF, others: Iterable[QRectF], threshold: float = 6.0) -> SnapGuide:
    guide = SnapGuide()
    mx1, my1, mx2, my2 = moving_rect.left(), moving_rect.top(), moving_rect.right(), moving_rect.bottom()
    mcx, mcy = moving_rect.center().x(), moving_rect.center().y()
    for r in others:
        x1, y1, x2, y2 = r.left(), r.top(), r.right(), r.bottom()
        cx, cy = r.center().x(), r.center().y()
        if abs(mx1 - x1) <= threshold:
            guide.add_vertical(x1, min(my1, y1), max(my2, y2))
        if abs(mx2 - x2) <= threshold:
            guide.add_vertical(x2, min(my1, y1), max(my2, y2))
        if abs(mcx - cx) <= threshold:
            guide.add_vertical(cx, min(my1, y1), max(my2, y2))
        if abs(my1 - y1) <= threshold:
            guide.add_horizontal(y1, min(mx1, x1), max(mx2, x2))
        if abs(my2 - y2) <= threshold:
            guide.add_horizontal(y2, min(mx1, x1), max(mx2, x2))
        if abs(mcy - cy) <= threshold:
            guide.add_horizontal(cy, min(mx1, x1), max(mx2, x2))
    return guide
