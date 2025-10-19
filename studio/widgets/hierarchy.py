from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QWidget

from ..designer.canvas import CanvasView
from ..designer.items import FieldItem


class HierarchyWidget(QListWidget):
    def __init__(self, canvas: CanvasView, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.canvas = canvas
        self.setSelectionMode(self.SelectionMode.SingleSelection)
        self.canvas.itemsAdded.connect(self._on_items_added)
        self.canvas.selectionChanged.connect(self._on_canvas_selection)
        self.itemSelectionChanged.connect(self._on_self_selection)
        self.refresh()

    def refresh(self) -> None:
        self.clear()
        for it in [x for x in self.canvas.scene().items() if isinstance(x, FieldItem)]:
            w = QListWidgetItem(f"{it.key()} ({it.label()})")
            w.setData(Qt.ItemDataRole.UserRole, it)
            self.addItem(w)

    def _on_items_added(self, _items: list) -> None:  # type: ignore[override]
        self.refresh()

    def _on_canvas_selection(self) -> None:
        items = self.canvas.selected_items()
        self.blockSignals(True)
        try:
            for i in range(self.count()):
                it = self.item(i)
                obj = it.data(Qt.ItemDataRole.UserRole)
                it.setSelected(obj in items)
        finally:
            self.blockSignals(False)

    def _on_self_selection(self) -> None:
        items = []
        for it in self.selectedItems():
            obj: FieldItem = it.data(Qt.ItemDataRole.UserRole)
            items.append(obj)
        for it in [x for x in self.canvas.scene().items() if isinstance(x, FieldItem)]:
            it.setSelected(it in items)
