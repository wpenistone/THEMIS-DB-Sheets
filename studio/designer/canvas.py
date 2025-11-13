from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from PyQt6.QtCore import QPointF, QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QKeySequence, QPainter
from PyQt6.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsView, QMenu, QWidget

from ..commands import CommandStack, MoveItem
from ..utils import gen_id
from .grid import SheetGrid
from .guides import SnapGuide, compute_alignment_guides
from .items import FieldItem
from .arrange import smart_arrange


class CanvasScene(QGraphicsScene):
    def __init__(self) -> None:
        super().__init__()
        self.setSceneRect(QRectF(0, 0, 1600, 1200))
        self.grid = SheetGrid()
        self.guides = SnapGuide()
        self._selection_rect: Optional[QRectF] = None

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # type: ignore[override]
        painter.fillRect(rect, QColor("#ffffff"))
        self.grid.draw(painter, rect)

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:  # type: ignore[override]
        self.guides.draw(painter)

    def items_except(self, item: QGraphicsItem) -> Iterable[QGraphicsItem]:
        for it in self.items():
            if it is not item and isinstance(it, FieldItem):
                yield it


class CanvasView(QGraphicsView):
    selectionChanged = pyqtSignal()
    geometryChanged = pyqtSignal()
    itemsAdded = pyqtSignal(list)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)

        self._scene = CanvasScene()
        self.setScene(self._scene)

        self._stack = CommandStack()
        self._selected: List[FieldItem] = []
        self._last_drag_pos: Optional[QPointF] = None
        self._moving_items: Dict[FieldItem, QPointF] = {}
        self._zoom: float = 1.0

        self._create_actions()

        self._scene.selectionChanged.connect(self._on_selection_changed)

    def command_stack(self) -> CommandStack:
        return self._stack

    def clear(self) -> None:
        self.scene().clear()

    def add_field(self, key: str, label: str, row: int, col: int) -> FieldItem:
        pos = self._scene.grid.pos_for_cell(row, col)
        item = FieldItem(key, label, pos, QPointF(self._scene.grid.cell_width * 2, self._scene.grid.cell_height * 1.5))
        self._scene.addItem(item)
        item.geometryChanged.connect(self._on_geometry_changed)
        item.selectedChanged.connect(self._on_item_selected)
        return item

    def add_fields_from_list(self, fields: List[Dict[str, Any]]) -> List[FieldItem]:
        items: List[FieldItem] = []
        for f in fields:
            items.append(self.add_field(f.get("key", gen_id("field")), f.get("label", f.get("key", "Field")), int(f.get("row", 0)), int(f.get("col", 0))))
        self.itemsAdded.emit(items)
        return items

    def selected_items(self) -> List[FieldItem]:
        return [it for it in self._scene.selectedItems() if isinstance(it, FieldItem)]

    def _on_selection_changed(self) -> None:
        self.selectionChanged.emit()

    def _on_item_selected(self, _selected: bool) -> None:
        self.selectionChanged.emit()

    def _on_geometry_changed(self) -> None:
        self.geometryChanged.emit()

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.matches(QKeySequence.StandardKey.Delete):
            for it in self.selected_items():
                self._scene.removeItem(it)
            event.accept()
            return
        if event.matches(QKeySequence.StandardKey.SelectAll):
            for it in self._scene.items():
                it.setSelected(True)
            event.accept()
            return
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            dx = 0
            dy = 0
            if event.key() == Qt.Key.Key_Left:
                dx = -1
            elif event.key() == Qt.Key.Key_Right:
                dx = 1
            elif event.key() == Qt.Key.Key_Up:
                dy = -1
            elif event.key() == Qt.Key.Key_Down:
                dy = 1
            for it in self.selected_items():
                old = it.pos()
                it.setPos(old + QPointF(dx, dy))
                self._stack.perform(MoveItem(it, (old.x(), old.y()), (it.pos().x(), it.pos().y())))
            event.accept()
            return
        if event.key() == Qt.Key.Key_G:
            self.toggle_grid()
            event.accept()
            return
        super().keyPressEvent(event)

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.25 if event.angleDelta().y() > 0 else 0.8
            self.scale(factor, factor)
            self._zoom *= factor
            event.accept()
            return
        super().wheelEvent(event)

    def contextMenuEvent(self, event) -> None:  # type: ignore[override]
        menu = QMenu(self)
        menu.addAction(self.act_align_left)
        menu.addAction(self.act_align_right)
        menu.addAction(self.act_align_top)
        menu.addAction(self.act_align_bottom)
        menu.addSeparator()
        menu.addAction(self.act_distribute_h)
        menu.addAction(self.act_distribute_v)
        menu.addSeparator()
        menu.addAction(self.act_toggle_grid)
        menu.exec(event.globalPos())

    def _create_actions(self) -> None:
        self.act_align_left = QAction("Align Left", self)
        self.act_align_left.triggered.connect(lambda: self.align("left"))
        self.act_align_right = QAction("Align Right", self)
        self.act_align_right.triggered.connect(lambda: self.align("right"))
        self.act_align_top = QAction("Align Top", self)
        self.act_align_top.triggered.connect(lambda: self.align("top"))
        self.act_align_bottom = QAction("Align Bottom", self)
        self.act_align_bottom.triggered.connect(lambda: self.align("bottom"))
        self.act_distribute_h = QAction("Distribute Horizontally", self)
        self.act_distribute_h.triggered.connect(lambda: self.distribute("h"))
        self.act_distribute_v = QAction("Distribute Vertically", self)
        self.act_distribute_v.triggered.connect(lambda: self.distribute("v"))
        self.act_toggle_grid = QAction("Toggle Grid (G)", self)
        self.act_toggle_grid.triggered.connect(self.toggle_grid)

    def align(self, mode: str) -> None:
        items = self.selected_items()
        if len(items) < 2:
            return
        ref = items[0].sceneBoundingRect()
        for it in items[1:]:
            old = it.pos()
            r = it.sceneBoundingRect()
            if mode == "left":
                dx = ref.left() - r.left()
                it.setPos(it.pos() + QPointF(dx, 0))
            elif mode == "right":
                dx = ref.right() - r.right()
                it.setPos(it.pos() + QPointF(dx, 0))
            elif mode == "top":
                dy = ref.top() - r.top()
                it.setPos(it.pos() + QPointF(0, dy))
            elif mode == "bottom":
                dy = ref.bottom() - r.bottom()
                it.setPos(it.pos() + QPointF(0, dy))
            self._stack.perform(MoveItem(it, (old.x(), old.y()), (it.pos().x(), it.pos().y())))

    def distribute(self, axis: str) -> None:
        items = self.selected_items()
        if len(items) < 3:
            return
        rects = [it.sceneBoundingRect() for it in items]
        rects.sort(key=lambda r: r.left() if axis == "h" else r.top())
        if axis == "h":
            left = rects[0].left()
            right = rects[-1].right()
            total_w = sum(r.width() for r in rects)
            gap = (right - left - total_w) / (len(rects) - 1)
            x = left
            for it, r in zip(items, rects):
                old = it.pos()
                it.setPos(it.pos() + QPointF(x - r.left(), 0))
                x += r.width() + gap
                self._stack.perform(MoveItem(it, (old.x(), old.y()), (it.pos().x(), it.pos().y())))
        else:
            top = rects[0].top()
            bottom = rects[-1].bottom()
            total_h = sum(r.height() for r in rects)
            gap = (bottom - top - total_h) / (len(rects) - 1)
            y = top
            for it, r in zip(items, rects):
                old = it.pos()
                it.setPos(it.pos() + QPointF(0, y - r.top()))
                y += r.height() + gap
                self._stack.perform(MoveItem(it, (old.x(), old.y()), (it.pos().x(), it.pos().y())))

    def start_move(self, items: List[FieldItem], mouse_scene_pos: QPointF) -> None:
        self._moving_items = {it: it.pos() for it in items}
        self._last_drag_pos = mouse_scene_pos

    def update_move(self, mouse_scene_pos: QPointF) -> None:
        if self._last_drag_pos is None:
            return
        delta = mouse_scene_pos - self._last_drag_pos
        for it, start_pos in self._moving_items.items():
            it.setPos(start_pos + delta)
        r = self._moving_rect()
        others = [it.sceneBoundingRect() for it in self._scene.items() if isinstance(it, FieldItem) and it not in self._moving_items]
        self._scene.guides = compute_alignment_guides(r, others)
        self.viewport().update()

    def finish_move(self) -> None:
        if self._last_drag_pos is None:
            return
        for it, start_pos in self._moving_items.items():
            end_pos = it.pos()
            if start_pos != end_pos:
                self._stack.perform(MoveItem(it, (start_pos.x(), start_pos.y()), (end_pos.x(), end_pos.y())))
        self._moving_items = {}
        self._last_drag_pos = None
        self._scene.guides.clear()
        self.viewport().update()

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            items = [it for it in self.items(event.pos()) if isinstance(it, FieldItem)]
            if items:
                self.start_move(self.selected_items(), self.mapToScene(event.pos()))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._moving_items:
            self.update_move(self.mapToScene(event.pos()))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self._moving_items:
            self.finish_move()
        super().mouseReleaseEvent(event)

    def _moving_rect(self) -> QRectF:
        rects = [it.sceneBoundingRect() for it in self._moving_items]
        if not rects:
            return QRectF()
        r = rects[0]
        for rr in rects[1:]:
            r = r.united(rr)
        return r

    def export_fields(self) -> List[Dict[str, Any]]:
        fields: List[Dict[str, Any]] = []
        cw = self._scene.grid.cell_width
        ch = self._scene.grid.cell_height
        for it in [x for x in self._scene.items() if isinstance(x, FieldItem)]:
            row, col = it.cell(cw, ch)
            fields.append({"key": it.key(), "label": it.label(), "row": row, "col": col})
        fields.sort(key=lambda f: (f["row"], f["col"]))
        return fields

    def clear_items(self) -> None:
        for it in [x for x in self._scene.items() if isinstance(x, FieldItem)]:
            self._scene.removeItem(it)

    def load_fields(self, fields: List[Dict[str, Any]]) -> None:
        self.clear_items()
        self.add_fields_from_list(fields)

    def toggle_grid(self) -> None:
        self._scene.grid.visible = not self._scene.grid.visible
        self.viewport().update()

    def zoom_in(self) -> None:
        self.scale(1.2, 1.2)
        self._zoom *= 1.2

    def zoom_out(self) -> None:
        self.scale(1 / 1.2, 1 / 1.2)
        self._zoom /= 1.2

    def smart_arrange_selected(self, strategy: str = "grid") -> None:
        items = self.selected_items()
        if not items:
            return
        rects = [it.sceneBoundingRect() for it in items]
        area = self.sceneRect()
        start = rects[0].topLeft()
        arranged = smart_arrange(rects, strategy=strategy, grid_w=self._scene.grid.cell_width, grid_h=self._scene.grid.cell_height, start=start, area=area)
        for it, r in zip(items, arranged):
            old = it.pos()
            it.setPos(QPointF(r.left(), r.top()))
            self._stack.perform(MoveItem(it, (old.x(), old.y()), (it.pos().x(), it.pos().y())))
