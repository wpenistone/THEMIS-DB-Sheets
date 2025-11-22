from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Tuple

from PyQt6.QtGui import QUndoCommand, QUndoStack


class Command(QUndoCommand):
    def __init__(self, text: str) -> None:
        super().__init__(text)


class CompositeCommand(Command):
    def __init__(self, text: str) -> None:
        super().__init__(text)
        self.children: List[QUndoCommand] = []

    def push(self, cmd: QUndoCommand) -> None:
        self.children.append(cmd)

    def undo(self) -> None:
        for cmd in reversed(self.children):
            cmd.undo()

    def redo(self) -> None:
        for cmd in self.children:
            cmd.redo()


class SetProperty(Command):
    def __init__(self, target: Any, prop: str, new_value: Any, text: Optional[str] = None) -> None:
        super().__init__(text or f"Set {prop}")
        self.target = target
        self.prop = prop
        self.new_value = new_value
        self.old_value = getattr(target, self.prop) if hasattr(target, self.prop) else target.property(self.prop)

    def undo(self) -> None:
        self._set(self.old_value)

    def redo(self) -> None:
        self._set(self.new_value)

    def _set(self, value: Any) -> None:
        if hasattr(self.target, self.prop):
            setattr(self.target, self.prop, value)
        else:
            self.target.setProperty(self.prop, value)
        if hasattr(self.target, "propertyChanged"):
            try:
                self.target.propertyChanged.emit(self.prop, value)
            except Exception:
                pass


class MapProperty(Command):
    def __init__(self, target: Any, getter: Callable[[], Any], setter: Callable[[Any], None], new_value: Any, text: str) -> None:
        super().__init__(text)
        self.target = target
        self.getter = getter
        self.setter = setter
        self.new_value = new_value
        self.old_value = getter()

    def undo(self) -> None:
        self.setter(self.old_value)

    def redo(self) -> None:
        self.setter(self.new_value)


class MoveItem(Command):
    def __init__(self, item: Any, old_pos: Tuple[float, float], new_pos: Tuple[float, float]) -> None:
        super().__init__("Move")
        self.item = item
        self.old_pos = old_pos
        self.new_pos = new_pos

    def undo(self) -> None:
        self.item.setPos(*self.old_pos)
        if hasattr(self.item, "emit_geometry_changed"):
            self.item.emit_geometry_changed()

    def redo(self) -> None:
        self.item.setPos(*self.new_pos)
        if hasattr(self.item, "emit_geometry_changed"):
            self.item.emit_geometry_changed()


class ResizeItem(Command):
    def __init__(self, item: Any, old_rect: Tuple[float, float, float, float], new_rect: Tuple[float, float, float, float]) -> None:
        super().__init__("Resize")
        self.item = item
        self.old_rect = old_rect
        self.new_rect = new_rect

    def undo(self) -> None:
        self.item.setRect(*self.old_rect)
        if hasattr(self.item, "emit_geometry_changed"):
            self.item.emit_geometry_changed()

    def redo(self) -> None:
        self.item.setRect(*self.new_rect)
        if hasattr(self.item, "emit_geometry_changed"):
            self.item.emit_geometry_changed()


class AddItem(Command):
    def __init__(self, scene: Any, item: Any) -> None:
        super().__init__("Add Item")
        self.scene = scene
        self.item = item

    def undo(self) -> None:
        self.scene.removeItem(self.item)

    def redo(self) -> None:
        self.scene.addItem(self.item)


class RemoveItem(Command):
    def __init__(self, scene: Any, item: Any) -> None:
        super().__init__("Remove Item")
        self.scene = scene
        self.item = item

    def undo(self) -> None:
        self.scene.addItem(self.item)

    def redo(self) -> None:
        self.scene.removeItem(self.item)


class DuplicateItems(Command):
    def __init__(self, scene: Any, items: List[Any]) -> None:
        super().__init__("Duplicate")
        self.scene = scene
        self.items = items
        self.clones: List[Any] = []

    def undo(self) -> None:
        for it in self.clones:
            self.scene.removeItem(it)
        self.clones.clear()

    def redo(self) -> None:
        if not self.clones:
            for it in self.items:
                clone = it.__class__(it.key(), it.label(), it.pos() + (it.pos() - it.pos()) + self._offset(), it.rect().bottomRight())
                try:
                    clone.set_from_dict(it.to_dict())
                except Exception:
                    pass
                self.scene.addItem(clone)
                self.clones.append(clone)
        else:
            for it in self.clones:
                self.scene.addItem(it)

    def _offset(self) -> Any:
        from PyQt6.QtCore import QPointF as _Q

        return _Q(12, 12)


class BatchMove(Command):
    def __init__(self, items: List[Any], delta: Tuple[float, float]) -> None:
        super().__init__("Batch Move")
        self.items = items
        self.delta = delta
        self.originals: List[Tuple[float, float]] = [(it.pos().x(), it.pos().y()) for it in items]

    def undo(self) -> None:
        for it, (x, y) in zip(self.items, self.originals):
            it.setPos(x, y)

    def redo(self) -> None:
        dx, dy = self.delta
        for it in self.items:
            it.setPos(it.pos().x() + dx, it.pos().y() + dy)


class BatchResize(Command):
    def __init__(self, items: List[Any], factor: float) -> None:
        super().__init__("Batch Resize")
        self.items = items
        self.factor = factor
        self.originals: List[Tuple[float, float, float, float]] = [(it.rect().x(), it.rect().y(), it.rect().width(), it.rect().height()) for it in items]

    def undo(self) -> None:
        for it, (x, y, w, h) in zip(self.items, self.originals):
            it.setRect(x, y, w, h)

    def redo(self) -> None:
        for it in self.items:
            r = it.rect()
            it.setRect(r.x(), r.y(), r.width() * self.factor, r.height() * self.factor)


class ReorderZ(Command):
    def __init__(self, items: List[Any], front: bool) -> None:
        super().__init__("Bring To Front" if front else "Send To Back")
        self.items = items
        self.front = front
        self.originals: List[float] = [float(getattr(it, "zValue", lambda: 0.0)()) for it in items]

    def undo(self) -> None:
        for it, z in zip(self.items, self.originals):
            try:
                it.setZValue(z)
            except Exception:
                pass

    def redo(self) -> None:
        z = 1000.0 if self.front else -1000.0
        for it in self.items:
            try:
                it.setZValue(z)
            except Exception:
                pass


class CommandStack(QUndoStack):
    def __init__(self) -> None:
        super().__init__()

    def perform(self, cmd: QUndoCommand) -> None:
        self.push(cmd)
