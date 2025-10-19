from __future__ import annotations

from typing import Any, Dict, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from .model import OrgNode


class OrgTreeEditor(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Name", "Sheet Name"])
        self.tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.tree.itemSelectionChanged.connect(self._on_selection)

        self.btn_add = QPushButton("Add Child")
        self.btn_add.clicked.connect(self._add_child)
        self.btn_remove = QPushButton("Remove")
        self.btn_remove.clicked.connect(self._remove)
        self.btn_rename = QPushButton("Rename")
        self.btn_rename.clicked.connect(self._rename)
        self.btn_set_sheet = QPushButton("Set Sheet Name")
        self.btn_set_sheet.clicked.connect(self._set_sheet)

        layout = QHBoxLayout(self)
        layout.addWidget(self.tree, 1)
        btns = QWidget()
        bl = QHBoxLayout(btns)
        bl.setContentsMargins(8, 8, 8, 8)
        bl.addWidget(self.btn_add)
        bl.addWidget(self.btn_remove)
        bl.addWidget(self.btn_rename)
        bl.addWidget(self.btn_set_sheet)
        layout.addWidget(btns, 0)

        self._root = OrgNode("Legio VI", "Legio VI")
        self.refresh()

    def root(self) -> OrgNode:
        return self._root

    def set_root(self, root: OrgNode) -> None:
        self._root = root
        self.refresh()
        self.changed.emit()

    def to_dict(self) -> Dict[str, Any]:
        return self._root.to_dict()

    def refresh(self) -> None:
        self.tree.clear()
        self._add_node_item(None, self._root)
        self.tree.expandAll()

    def _add_node_item(self, parent: Optional[QTreeWidgetItem], node: OrgNode) -> None:
        item = QTreeWidgetItem([node.name, node.sheet_name])
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        item.setData(0, Qt.ItemDataRole.UserRole, node)
        if parent is None:
            self.tree.addTopLevelItem(item)
        else:
            parent.addChild(item)
        for c in node.children:
            self._add_node_item(item, c)

    def _current_node_item(self) -> Optional[QTreeWidgetItem]:
        items = self.tree.selectedItems()
        return items[0] if items else None

    def _add_child(self) -> None:
        item = self._current_node_item()
        if item is None:
            return
        node: OrgNode = item.data(0, Qt.ItemDataRole.UserRole)
        name, ok = QInputDialog.getText(self, "Add Child", "Name:", QLineEdit.EchoMode.Normal, "New Unit")
        if not ok or not name:
            return
        sheet, ok2 = QInputDialog.getText(self, "Add Child", "Sheet Name:", QLineEdit.EchoMode.Normal, name)
        if not ok2:
            return
        child = OrgNode(name, sheet)
        node.add_child(child)
        self.refresh()
        self.changed.emit()

    def _remove(self) -> None:
        item = self._current_node_item()
        if item is None:
            return
        if item.parent() is None:
            QMessageBox.warning(self, "Cannot Remove", "Cannot remove root node")
            return
        node: OrgNode = item.data(0, Qt.ItemDataRole.UserRole)
        parent_item = item.parent()
        parent_node: OrgNode = parent_item.data(0, Qt.ItemDataRole.UserRole)
        parent_node.remove_child(node)
        self.refresh()
        self.changed.emit()

    def _rename(self) -> None:
        item = self._current_node_item()
        if item is None:
            return
        self.tree.editItem(item, 0)

    def _set_sheet(self) -> None:
        item = self._current_node_item()
        if item is None:
            return
        text, ok = QInputDialog.getText(self, "Sheet Name", "Sheet Name:", QLineEdit.EchoMode.Normal, item.text(1))
        if ok:
            item.setText(1, text)
            node: OrgNode = item.data(0, Qt.ItemDataRole.UserRole)
            node.sheet_name = text
            self.changed.emit()

    def _on_item_changed(self, item: QTreeWidgetItem, col: int) -> None:
        node: OrgNode = item.data(0, Qt.ItemDataRole.UserRole)
        if col == 0:
            node.name = item.text(0)
        elif col == 1:
            node.sheet_name = item.text(1)
        self.changed.emit()

    def _on_item_double_clicked(self, item: QTreeWidgetItem, col: int) -> None:
        self.tree.editItem(item, col)

    def _on_selection(self) -> None:
        pass
