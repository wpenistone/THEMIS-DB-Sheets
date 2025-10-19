from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QWidget

from .resources import (
    icon_add,
    icon_delete,
    icon_open,
    icon_save,
    icon_undo,
    icon_redo,
    icon_run,
    icon_preview,
    icon_zoom_in,
    icon_zoom_out,
)


class ActionFactory:
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        self.parent = parent

    def action(self, text: str, shortcut: Optional[str] = None, icon: Optional[Callable[[], object]] = None, tip: Optional[str] = None, callback: Optional[Callable] = None) -> QAction:
        act = QAction(text, self.parent)
        if shortcut:
            act.setShortcut(shortcut)
        if icon:
            act.setIcon(icon())
        if tip:
            act.setStatusTip(tip)
            act.setToolTip(tip)
        if callback:
            act.triggered.connect(callback)
        return act

    def file_open(self, cb: Callable) -> QAction:
        return self.action("Open...", "Ctrl+O", icon_open, "Open configuration", cb)

    def file_save(self, cb: Callable) -> QAction:
        return self.action("Save", "Ctrl+S", icon_save, "Save configuration", cb)

    def file_save_as(self, cb: Callable) -> QAction:
        return self.action("Save As...", None, icon_save, "Save configuration as", cb)

    def edit_undo(self, cb: Callable) -> QAction:
        return self.action("Undo", "Ctrl+Z", icon_undo, "Undo last action", cb)

    def edit_redo(self, cb: Callable) -> QAction:
        return self.action("Redo", "Ctrl+Shift+Z", icon_redo, "Redo last action", cb)

    def add_field(self, cb: Callable) -> QAction:
        return self.action("Add Field", "A", icon_add, "Add a field to layout", cb)

    def remove(self, cb: Callable) -> QAction:
        return self.action("Remove", "Del", icon_delete, "Remove selected", cb)

    def run_validate(self, cb: Callable) -> QAction:
        return self.action("Validate", None, icon_run, "Run validation", cb)

    def preview(self, cb: Callable) -> QAction:
        return self.action("Preview", "Ctrl+P", icon_preview, "Preview layout", cb)

    def zoom_in(self, cb: Callable) -> QAction:
        return self.action("Zoom In", "Ctrl++", icon_zoom_in, "Zoom in", cb)

    def zoom_out(self, cb: Callable) -> QAction:
        return self.action("Zoom Out", "Ctrl+-", icon_zoom_out, "Zoom out", cb)
