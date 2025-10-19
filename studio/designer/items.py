from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsSceneMouseEvent, QGraphicsSimpleTextItem


HANDLE_SIZE = 6.0


class SelectionHandle(QGraphicsRectItem):
    def __init__(self, owner: "FieldItem", cursor: Qt.CursorShape) -> None:
        super().__init__(0, 0, HANDLE_SIZE, HANDLE_SIZE, owner)
        self.owner = owner
        self.setBrush(QColor("#339af0"))
        self.setPen(Qt.PenStyle.NoPen)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setCursor(cursor)
        self._drag_start: Optional[QPointF] = None
        self._orig_rect: Optional[QRectF] = None

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._drag_start = event.scenePos()
        self._orig_rect = self.owner.rect()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._drag_start is None or self._orig_rect is None:
            return
        delta = event.scenePos() - self._drag_start
        r = QRectF(self._orig_rect)
        if self.cursor().shape() in (Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeAllCursor, Qt.CursorShape.SizeBDiagCursor):
            pass
        if self is self.owner.handle_tl:
            r.setLeft(r.left() + delta.x())
            r.setTop(r.top() + delta.y())
        elif self is self.owner.handle_tr:
            r.setRight(r.right() + delta.x())
            r.setTop(r.top() + delta.y())
        elif self is self.owner.handle_bl:
            r.setLeft(r.left() + delta.x())
            r.setBottom(r.bottom() + delta.y())
        elif self is self.owner.handle_br:
            r.setRight(r.right() + delta.x())
            r.setBottom(r.bottom() + delta.y())
        elif self is self.owner.handle_l:
            r.setLeft(r.left() + delta.x())
        elif self is self.owner.handle_r:
            r.setRight(r.right() + delta.x())
        elif self is self.owner.handle_t:
            r.setTop(r.top() + delta.y())
        elif self is self.owner.handle_b:
            r.setBottom(r.bottom() + delta.y())
        if r.width() < 10:
            r.setWidth(10)
        if r.height() < 10:
            r.setHeight(10)
        self.owner.setRect(r)
        self.owner.emit_geometry_changed()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self._drag_start = None
        self._orig_rect = None
        super().mouseReleaseEvent(event)


class FieldItem(QGraphicsRectItem):
    geometryChanged = pyqtSignal()
    selectedChanged = pyqtSignal(bool)

    def __init__(self, key: str, label: str, pos: QPointF, size: QPointF) -> None:
        super().__init__(0, 0, size.x(), size.y())
        self._key = key
        self._label = label
        self.setPos(pos)
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )
        self.setAcceptHoverEvents(True)
        self.text = QGraphicsSimpleTextItem(label, self)
        f = QFont()
        f.setPointSize(10)
        self.text.setFont(f)
        self.text.setPos(6, 4)
        self.bg = QColor("#f1f3f5")
        self.border = QColor("#adb5bd")
        self.sel = QColor("#4dabf7")
        self.text_color = QColor("#212529")
        self.handle_tl = SelectionHandle(self, Qt.CursorShape.SizeFDiagCursor)
        self.handle_tr = SelectionHandle(self, Qt.CursorShape.SizeBDiagCursor)
        self.handle_bl = SelectionHandle(self, Qt.CursorShape.SizeBDiagCursor)
        self.handle_br = SelectionHandle(self, Qt.CursorShape.SizeFDiagCursor)
        self.handle_l = SelectionHandle(self, Qt.CursorShape.SizeHorCursor)
        self.handle_r = SelectionHandle(self, Qt.CursorShape.SizeHorCursor)
        self.handle_t = SelectionHandle(self, Qt.CursorShape.SizeVerCursor)
        self.handle_b = SelectionHandle(self, Qt.CursorShape.SizeVerCursor)
        self._update_handles()

    def key(self) -> str:
        return self._key

    def set_key(self, key: str) -> None:
        self._key = key

    def label(self) -> str:
        return self._label

    def set_label(self, label: str) -> None:
        self._label = label
        self.text.setText(label)

    def emit_geometry_changed(self) -> None:
        self.geometryChanged.emit()

    def setRect(self, *args: Any) -> None:  # type: ignore[override]
        if len(args) == 1 and isinstance(args[0], QRectF):
            super().setRect(args[0])
        else:
            super().setRect(QRectF(args[0], args[1], args[2], args[3]))
        self._update_handles()

    def _update_handles(self) -> None:
        r = self.rect()
        hs = HANDLE_SIZE
        self.handle_tl.setPos(r.left() - hs / 2, r.top() - hs / 2)
        self.handle_tr.setPos(r.right() - hs / 2, r.top() - hs / 2)
        self.handle_bl.setPos(r.left() - hs / 2, r.bottom() - hs / 2)
        self.handle_br.setPos(r.right() - hs / 2, r.bottom() - hs / 2)
        self.handle_l.setPos(r.left() - hs / 2, r.center().y() - hs / 2)
        self.handle_r.setPos(r.right() - hs / 2, r.center().y() - hs / 2)
        self.handle_t.setPos(r.center().x() - hs / 2, r.top() - hs / 2)
        self.handle_b.setPos(r.center().x() - hs / 2, r.bottom() - hs / 2)
        for h in (self.handle_tl, self.handle_tr, self.handle_bl, self.handle_br, self.handle_l, self.handle_r, self.handle_t, self.handle_b):
            h.setVisible(self.isSelected())

    def hoverMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        super().hoverMoveEvent(event)

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            selected = bool(value)
            self.selectedChanged.emit(selected)
            for h in (self.handle_tl, self.handle_tr, self.handle_bl, self.handle_br, self.handle_l, self.handle_r, self.handle_t, self.handle_b):
                h.setVisible(selected)
        if change in (QGraphicsItem.GraphicsItemChange.ItemPositionChange, QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged, QGraphicsItem.GraphicsItemChange.ItemTransformHasChanged, QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged):
            self.geometryChanged.emit()
        return super().itemChange(change, value)

    def paint(self, painter: QPainter, option: Any, widget: Optional[QWidget] = None) -> None:  # type: ignore[name-defined]
        r = self.rect()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(self.bg)
        painter.setPen(QPen(self.border, 1))
        painter.drawRoundedRect(r, 3, 3)
        if self.isSelected():
            painter.setPen(QPen(self.sel, 1.5, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(r.adjusted(-2, -2, 2, 2), 4, 4)
        self.text.setBrush(self.text_color)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self._key,
            "label": self._label,
            "x": float(self.pos().x()),
            "y": float(self.pos().y()),
            "w": float(self.rect().width()),
            "h": float(self.rect().height()),
        }

    def set_from_dict(self, d: Dict[str, Any]) -> None:
        self._key = d.get("key", self._key)
        self._label = d.get("label", self._label)
        self.text.setText(self._label)
        self.setPos(QPointF(float(d.get("x", self.pos().x())), float(d.get("y", self.pos().y()))))
        self.setRect(0, 0, float(d.get("w", self.rect().width())), float(d.get("h", self.rect().height())))

    def set_cell(self, row: int, col: int, cell_w: float, cell_h: float) -> None:
        self.setPos(QPointF(col * cell_w, row * cell_h))

    def cell(self, cell_w: float, cell_h: float) -> Tuple[int, int]:
        col = int(round(self.pos().x() / cell_w))
        row = int(round(self.pos().y() / cell_h))
        return row, col
