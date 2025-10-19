from __future__ import annotations

from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPixmap, QPolygonF


def _make_icon(draw_fn, size: int = 64) -> QIcon:
    pm = QPixmap(size, size)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    draw_fn(p, size)
    p.end()
    return QIcon(pm)


def icon_add() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.fillRect(QRect(0, 0, s, s), QColor(0, 0, 0, 0))
        p.setPen(QColor("#2c7be5"))
        p.setBrush(QColor("#2c7be5"))
        w = s * 0.15
        p.drawRect(QRect(int((s - w) / 2), int(s * 0.2), int(w), int(s * 0.6)))
        p.drawRect(QRect(int(s * 0.2), int((s - w) / 2), int(s * 0.6), int(w)))
    return _make_icon(draw)


def icon_delete() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#e55353"))
        p.setBrush(QColor("#e55353"))
        w = int(s * 0.15)
        p.drawRect(QRect(int(s * 0.2), int((s - w) / 2), int(s * 0.6), int(w)))
    return _make_icon(draw)


def icon_save() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#343a40"))
        p.setBrush(QColor("#51cf66"))
        p.drawRoundedRect(QRectF(s * 0.15, s * 0.15, s * 0.7, s * 0.7), 6, 6)
        p.setBrush(QColor("#ffffff"))
        p.drawRect(QRectF(s * 0.25, s * 0.25, s * 0.5, s * 0.2))
        p.drawRect(QRectF(s * 0.25, s * 0.5, s * 0.5, s * 0.2))
    return _make_icon(draw)


def icon_open() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#2b8a3e"))
        p.setBrush(QColor("#2b8a3e"))
        p.drawRoundedRect(QRectF(s * 0.15, s * 0.35, s * 0.7, s * 0.45), 6, 6)
        p.setBrush(QColor("#ffe066"))
        p.drawRect(QRectF(s * 0.2, s * 0.25, s * 0.4, s * 0.2))
    return _make_icon(draw)


def icon_undo() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#5c7cfa"))
        p.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        path.moveTo(s * 0.7, s * 0.35)
        path.cubicTo(s * 0.5, s * 0.15, s * 0.2, s * 0.25, s * 0.25, s * 0.55)
        path.cubicTo(s * 0.3, s * 0.85, s * 0.65, s * 0.85, s * 0.75, s * 0.6)
        p.drawPath(path)
        p.setBrush(QColor("#5c7cfa"))
        tri = QPolygonF([QPointF(s * 0.25, s * 0.5), QPointF(s * 0.35, s * 0.45), QPointF(s * 0.3, s * 0.6)])
        p.drawPolygon(tri)
    return _make_icon(draw)


def icon_redo() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#5c7cfa"))
        p.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        path.moveTo(s * 0.3, s * 0.35)
        path.cubicTo(s * 0.5, s * 0.15, s * 0.8, s * 0.25, s * 0.75, s * 0.55)
        path.cubicTo(s * 0.7, s * 0.85, s * 0.35, s * 0.85, s * 0.25, s * 0.6)
        p.drawPath(path)
        p.setBrush(QColor("#5c7cfa"))
        tri = QPolygonF([QPointF(s * 0.75, s * 0.5), QPointF(s * 0.65, s * 0.45), QPointF(s * 0.7, s * 0.6)])
        p.drawPolygon(tri)
    return _make_icon(draw)


def icon_run() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#20c997"))
        p.setBrush(QColor("#20c997"))
        tri = QPolygonF([QPointF(s * 0.35, s * 0.25), QPointF(s * 0.7, s * 0.5), QPointF(s * 0.35, s * 0.75)])
        p.drawPolygon(tri)
    return _make_icon(draw)


def icon_grid() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#868e96"))
        for i in range(4, s, 8):
            p.drawLine(i, 0, i, s)
            p.drawLine(0, i, s, i)
    return _make_icon(draw)


def icon_layout() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#adb5bd"))
        p.drawRect(QRectF(s * 0.1, s * 0.1, s * 0.8, s * 0.8))
        p.setBrush(QColor("#339af0"))
        p.drawRect(QRectF(s * 0.15, s * 0.15, s * 0.5, s * 0.3))
        p.setBrush(QColor("#faa2c1"))
        p.drawRect(QRectF(s * 0.15, s * 0.5, s * 0.4, s * 0.25))
        p.setBrush(QColor("#51cf66"))
        p.drawRect(QRectF(s * 0.6, s * 0.5, s * 0.25, s * 0.25))
    return _make_icon(draw)


def icon_tree() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setBrush(QColor("#e599f7"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPoint(int(s * 0.5), int(s * 0.2)), int(s * 0.12), int(s * 0.12))
        p.drawEllipse(QPoint(int(s * 0.3), int(s * 0.45)), int(s * 0.1), int(s * 0.1))
        p.drawEllipse(QPoint(int(s * 0.7), int(s * 0.45)), int(s * 0.1), int(s * 0.1))
        p.setPen(QColor("#495057"))
        p.setBrush(QColor("#495057"))
        p.drawRect(QRect(int(s * 0.48), int(s * 0.3), int(s * 0.04), int(s * 0.5)))
        p.setPen(QColor("#495057"))
        p.drawLine(int(s * 0.5), int(s * 0.35), int(s * 0.3), int(s * 0.45))
        p.drawLine(int(s * 0.5), int(s * 0.35), int(s * 0.7), int(s * 0.45))
    return _make_icon(draw)


def icon_validate() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#51cf66"))
        p.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        path.addRoundedRect(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6), 8, 8)
        p.drawPath(path)
        p.setBrush(QColor("#51cf66"))
        p.setPen(Qt.PenStyle.NoPen)
        check = QPolygonF([
            QPointF(s * 0.3, s * 0.5),
            QPointF(s * 0.45, s * 0.65),
            QPointF(s * 0.7, s * 0.35),
            QPointF(s * 0.7, s * 0.5),
            QPointF(s * 0.45, s * 0.8),
            QPointF(s * 0.3, s * 0.6),
        ])
        p.drawPolygon(check)
    return _make_icon(draw)


def icon_preview() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#15aabf"))
        p.setBrush(QColor("#15aabf"))
        p.drawRoundedRect(QRectF(s * 0.18, s * 0.22, s * 0.64, s * 0.52), 6, 6)
        p.setBrush(QColor("#e9ecef"))
        p.drawRect(QRectF(s * 0.22, s * 0.28, s * 0.4, s * 0.14))
        p.drawRect(QRectF(s * 0.22, s * 0.46, s * 0.36, s * 0.14))
    return _make_icon(draw)


def icon_zoom_in() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(QColor("#343a40"))
        p.setBrush(QColor("#e9ecef"))
        p.drawEllipse(QRectF(s * 0.15, s * 0.15, s * 0.5, s * 0.5))
        p.setBrush(QColor("#343a40"))
        p.drawRect(QRectF(s * 0.32, s * 0.36, s * 0.16, s * 0.08))
        p.drawRect(QRectF(s * 0.36, s * 0.32, s * 0.08, s * 0.16))
        p.setPen(QColor("#495057"))
        p.setBrush(QColor("#495057"))
        p.drawRect(QRectF(s * 0.52, s * 0.52, s * 0.24, s * 0.08))
    return _make_icon(draw)


def icon_zoom_out() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setPen(QColor("#343a40"))
        p.setBrush(QColor("#e9ecef"))
        p.drawEllipse(QRectF(s * 0.15, s * 0.15, s * 0.5, s * 0.5))
        p.setBrush(QColor("#343a40"))
        p.drawRect(QRectF(s * 0.32, s * 0.36, s * 0.16, s * 0.08))
        p.setPen(QColor("#495057"))
        p.setBrush(QColor("#495057"))
        p.drawRect(QRectF(s * 0.52, s * 0.52, s * 0.24, s * 0.08))
    return _make_icon(draw)


def icon_select() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#339af0"))
        tri = QPolygonF([
            QPointF(s * 0.25, s * 0.2),
            QPointF(s * 0.45, s * 0.65),
            QPointF(s * 0.6, s * 0.5),
        ])
        p.drawPolygon(tri)
        p.setBrush(QColor("#495057"))
        p.drawRect(QRectF(s * 0.45, s * 0.55, s * 0.2, s * 0.1))
    return _make_icon(draw)


def icon_hand() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#343a40"))
        p.setBrush(QColor("#ffd43b"))
        path = QPainterPath()
        path.moveTo(s * 0.3, s * 0.65)
        path.cubicTo(s * 0.35, s * 0.4, s * 0.65, s * 0.45, s * 0.7, s * 0.6)
        path.lineTo(s * 0.55, s * 0.8)
        path.lineTo(s * 0.35, s * 0.8)
        path.closeSubpath()
        p.drawPath(path)
    return _make_icon(draw)


def icon_snap() -> QIcon:
    def draw(p: QPainter, s: int) -> None:
        p.setPen(QColor("#12b886"))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawRect(QRectF(s * 0.2, s * 0.2, s * 0.6, s * 0.6))
        p.setPen(QColor("#12b886"))
        p.drawLine(int(s * 0.2), int(s * 0.5), int(s * 0.8), int(s * 0.5))
        p.drawLine(int(s * 0.5), int(s * 0.2), int(s * 0.5), int(s * 0.8))
    return _make_icon(draw)
