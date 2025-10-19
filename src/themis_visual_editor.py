#!/usr/bin/env python3
"""
THEMIS Configuration Studio (Visual Editor)

A single-file PyQt6 application to design and manage THEMIS configuration
for Google Sheets-based administration utilities as described in README.md
and compatible with the structures used by src/Code.js and Example_configs.

Key capabilities:
- Spreadsheet Layout Designer: drag-and-drop fields onto a grid to define
  LAYOUT_BLUEPRINTS offsets with an explicit anchor.
- Slot Blueprint Manager: define SLOT_BLUEPRINTS with per-slot layout,
  ranks/rank groups, counts and flexible location specifications.
- Organization Editor: manage ORGANIZATION_HIERARCHY visually with a tree,
  per-node properties (sheetName, layout, startCol, shortcuts, useSlotsFrom),
  and node-specific command slots.
- Ranks, Fields, Validation and Settings editors: define supporting data like
  RANK_HIERARCHY, CUSTOM_FIELDS, VALIDATION_RULES, TIME_IN_RANK_REQUIREMENTS,
  date formats and sheet names for logs.
- Live validation and preview. Export to JSON and to a JS file that declares
  const THEMIS_CONFIG = {...};

Keep this file self-contained; no external modules beyond PyQt6 and stdlib.
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
except Exception as e:  # pragma: no cover - this file may be linted without PyQt installed
    raise


# ------------------------------
# Data model and helpers
# ------------------------------

DEFAULT_FIELDS_PALETTE = [
    "rank",
    "username",
    "discordId",
    "region",
    "joinDate",
    "LOAcheckbox",
    "BTcheckbox",
]

DEFAULT_RANKS = [
    {"abbr": "AUX", "name": "Auxilia"},
    {"abbr": "TIR", "name": "Tirones"},
    {"abbr": "MIL", "name": "Milites"},
    {"abbr": "IMM", "name": "Immunes"},
    {"abbr": "DEC", "name": "Decanus"},
    {"abbr": "COR", "name": "Cornicen"},
]


def dict_deepcopy(d: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(d))


def pretty_json(d: Dict[str, Any]) -> str:
    return json.dumps(d, indent=2, ensure_ascii=False)


def to_js_const(name: str, d: Dict[str, Any]) -> str:
    text = pretty_json(d)
    return f"const {name} = {text};\n"


def sanitize_js_like_to_json(text: str) -> str:
    """Best-effort conversion of a simple JS object literal to JSON.
    This is intentionally conservative and supports the Example_configs format.
    - Replaces single quotes with double quotes if it seems safe
    - Ensures trailing commas are removed
    - Allows for const/var THEMIS_CONFIG = {...};
    """
    # Extract the object body if it's wrapped in a declaration
    m = re.search(r"THEMIS_CONFIG\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if m:
        text = m.group(1)
    # Replace single quotes outside of escaped contexts (rough approach)
    # Prefer not to touch if there are URLs with single quotes; the example configs use double quotes already.
    # Remove trailing commas before } or ]
    text = re.sub(r",\s*(\}|\])", r"\1", text)
    return text


@dataclass
class ThemisConfigModel:
    data: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def default() -> "ThemisConfigModel":
        base = {
            "DATE_FORMAT": "MM/DD/YY",
            "RECRUITMENT_LOG_SHEET_NAME": "Recruitment Logbook",
            "RECRUITMENT_LOG_START_ROW": 4,
            "RECRUITMENT_LOG_END_ROW": 100,
            "RECRUITMENT_LOG_COLUMNS": {
                "DATE": 3,
                "USERNAME": 4,
                "DISCORD_ID": 5,
                "REGION": 6,
                "SQUAD": 7,
                "RECRUITER": 8,
            },
            "EVENT_LOG_SHEET_NAME": "Event Logbook",
            "EVENT_LOG_COLUMNS": {"SECTION": 0, "DAY": 1, "HOST": 2, "TYPE": 3},
            "ATTENDANCE_SHEET_NAME": "Attendance Logbook",
            "ATTENDANCE_DATA_START_ROW": 5,
            "ATTENDANCE_DATA_END_ROW": 150,
            "ATTENDANCE_DAY_COLUMNS": {
                "Monday": 3,
                "Tuesday": 5,
                "Wednesday": 7,
                "Thursday": 9,
                "Friday": 11,
                "Saturday": 13,
                "Sunday": 15,
            },
            "LAYOUT_BLUEPRINTS": {
                # Provide a sensible initial layout
                "BILLET_OFFSETS": {
                    "offsets": {
                        "username": {"row": 0, "col": 0},
                        "region": {"row": 1, "col": -1},
                        "joinDate": {"row": 1, "col": 0},
                        "discordId": {"row": 1, "col": 1},
                        "LOAcheckbox": {"row": 1, "col": 2},
                    }
                },
                "BILLET_NCO_OFFSETS": {
                    "offsets": {
                        "rank": {"row": 0, "col": 0},
                        "username": {"row": 0, "col": 1},
                        "discordId": {"row": 0, "col": 4},
                        "region": {"row": 0, "col": 5},
                        "joinDate": {"row": 0, "col": 6},
                        "LOAcheckbox": {"row": 0, "col": 7}
                    }
                },
                "SQUAD_OFFSETS": {
                    "offsets": {
                        "rank": {"row": 0, "col": 0},
                        "username": {"row": 0, "col": 1},
                        "discordId": {"row": 0, "col": 4},
                        "region": {"row": 0, "col": 5},
                        "joinDate": {"row": 0, "col": 6},
                        "LOAcheckbox": {"row": 0, "col": 7},
                        "BTcheckbox": {"row": 0, "col": 8}
                    }
                }
            },
            "SLOT_BLUEPRINTS": {
                # Example blueprint matching README
                "STANDARD_CONTUBERNIUM": [
                    {
                        "layout": "BILLET_NCO_OFFSETS",
                        "rank": "Decanus",
                        "count": 1,
                        "location": {"rows": [12]},
                    },
                    {
                        "layout": "BILLET_NCO_OFFSETS",
                        "rank": "Cornicen",
                        "location": {"startRow": 14, "endRow": 15},
                        "count": 2,
                    },
                    {
                        "ranks": ["Tirones", "Auxilia", "Milites", "Immunes"],
                        "count": 23,
                        "location": {"startRow": 17, "endRow": 39},
                    },
                ]
            },
            "ORGANIZATION_HIERARCHY": [
                {
                    "name": "Legio VI",
                    "sheetName": "Legio VI",
                    "children": [
                        {
                            "name": "First Cohort",
                            "sheetName": "VI 1C",
                            "children": [
                                {
                                    "name": "First Aquilia Contubernium",
                                    "shortcuts": ["VI 1A"],
                                    "useSlotsFrom": "STANDARD_CONTUBERNIUM",
                                    "layout": "SQUAD_OFFSETS",
                                    "location": {"startCol": 4},
                                }
                            ],
                        }
                    ],
                }
            ],
            "RANK_HIERARCHY": DEFAULT_RANKS[:],
            "EVENT_TYPE_DEFINITIONS": [
                {"name": "Combat Training", "aliases": ["CT"]},
                {"name": "Crate Run", "aliases": ["Crates"]},
            ],
            "TIME_IN_RANK_REQUIREMENTS": {
                "DECANUS": 14,
                "CORNICEN": 14,
            },
            "WEBHOOK_URL": "",
            "THEMIS_CLIENT_API_KEY": "",
            "LOA_MENTION_ROLE_ID": "your_role_id",
            "LOCK_TIMEOUT_MS": 15000,
            "CACHE_KEYS": {
                "COMPANY": "global_companymen_cache_v9",
                "RECRUIT_DATA": "recruit_data_cache_v9",
                "SHEET_DATA_PREFIX": "sheet_data_v2_",
                "USER_DATA_PREFIX": "user_data_",
                "TOTAL_SLOTS_MAP": "total_slots_map_cache_v2",
                "WEBHOOK_QUEUE_KEY": "webhook_queue_v1",
            },
            "CACHE_DURATIONS": {"LONG": 21600, "STANDARD": 3600, "SHORT": 1800},
            "UBT_SETTINGS": {
                "NAME": "UBT",
                "PROMPT_MESSAGE": "This promotion requires the member to be {name} passed. Is this correct?",
                "TRIGGER_RANK": "Private First Class",
            },
            "LOGIC_THRESHOLDS": {
                "EMAIL_REQUIRED_MIN_RANK": {
                    "CONDITION": ">=Staff Sergeant",
                    "PROMPT": "Promotions to this rank or higher require an email on file. Please provide one for this member.",
                },
                "MIN_HOST_RANK": "Corporal",
            },
            "VALIDATION_RULES": {
                "USERNAME": {
                    "REGEX": "^[a-zA-Z0-9_]+$",
                    "REGEX_ERROR": "Invalid characters used.",
                    "MIN_LENGTH": 3,
                    "MAX_LENGTH": 20,
                    "LENGTH_ERROR": "Must be 3-20 characters.",
                    "NO_START_END_UNDERSCORE": True,
                    "START_END_UNDERSCORE_ERROR": "Cannot start or end with an underscore.",
                    "MAX_UNDERSCORES": 1,
                    "MAX_UNDERSCORES_ERROR": "Only one underscore is allowed.",
                }
            },
            "SHEET_ACCESS_MANAGEMENT": {"ON_RECRUIT": "ALWAYS", "ON_DELETE": "ALWAYS"},
            "CUSTOM_FIELDS": [],
            "CUSTOM_FIELDS_UI_EDITABLE": False,
        }
        return ThemisConfigModel(base)

    def to_json(self) -> str:
        return pretty_json(self.data)

    def to_js(self) -> str:
        return to_js_const("THEMIS_CONFIG", self.data)

    def add_layout(self, name: str) -> None:
        if name and name not in self.data["LAYOUT_BLUEPRINTS"]:
            self.data["LAYOUT_BLUEPRINTS"][name] = {"offsets": {}}

    def remove_layout(self, name: str) -> None:
        if name in self.data["LAYOUT_BLUEPRINTS"]:
            del self.data["LAYOUT_BLUEPRINTS"][name]

    def set_layout_offset(self, layout: str, field_key: str, row: int, col: int) -> None:
        if layout not in self.data["LAYOUT_BLUEPRINTS"]:
            self.add_layout(layout)
        self.data["LAYOUT_BLUEPRINTS"][layout].setdefault("offsets", {})
        self.data["LAYOUT_BLUEPRINTS"][layout]["offsets"][field_key] = {"row": row, "col": col}

    def remove_layout_offset(self, layout: str, field_key: str) -> None:
        try:
            del self.data["LAYOUT_BLUEPRINTS"][layout]["offsets"][field_key]
        except KeyError:
            pass

    def list_layouts(self) -> List[str]:
        return list(self.data.get("LAYOUT_BLUEPRINTS", {}).keys())

    def list_fields_palette(self) -> List[str]:
        keys = set(DEFAULT_FIELDS_PALETTE)
        for f in self.data.get("CUSTOM_FIELDS", []):
            ok = f.get("offsetKey")
            if ok:
                keys.add(ok)
        return sorted(keys)

    def validate(self) -> Tuple[List[str], List[str]]:
        errors: List[str] = []
        warnings: List[str] = []

        cfg = self.data
        # Ranks must be unique by name/abbr
        seen_names = set()
        seen_abbr = set()
        for r in cfg.get("RANK_HIERARCHY", []):
            name = (r.get("name") or "").strip().lower()
            abbr = (r.get("abbr") or "").strip().lower()
            if not name:
                errors.append("Rank with empty name detected.")
            if name in seen_names:
                errors.append(f"Duplicate rank name: {r.get('name')}")
            seen_names.add(name)
            if abbr:
                if abbr in seen_abbr:
                    warnings.append(f"Duplicate rank abbr: {r.get('abbr')}")
                seen_abbr.add(abbr)

        # Layouts: username offset is recommended and used by Code.js in some paths
        for lname, ldef in cfg.get("LAYOUT_BLUEPRINTS", {}).items():
            offsets = ldef.get("offsets", {})
            if "username" not in offsets:
                warnings.append(f"Layout '{lname}' lacks 'username' offset (recommended/used by Code.js).")

        # SLOT_BLUEPRINTS references valid layouts
        layouts = set(cfg.get("LAYOUT_BLUEPRINTS", {}).keys())
        for bp_name, slots in cfg.get("SLOT_BLUEPRINTS", {}).items():
            for s in slots:
                lay = s.get("layout")
                if lay and lay not in layouts:
                    errors.append(f"Slot blueprint '{bp_name}' references missing layout '{lay}'.")

        # ORG_HIERARCHY uses valid references
        def visit(nodes, path):
            for n in nodes:
                lname = n.get("layout")
                if lname and lname not in layouts:
                    errors.append(f"Node '{n.get('name')}' at '{'>' .join(path+[n.get('name','')])}' uses missing layout '{lname}'.")
                usf = n.get("useSlotsFrom")
                if usf and usf not in cfg.get("SLOT_BLUEPRINTS", {}):
                    errors.append(f"Node '{n.get('name')}' uses missing slot blueprint '{usf}'.")
                # children
                if n.get("children"):
                    visit(n["children"], path + [n.get("name", "?")])
        visit(cfg.get("ORGANIZATION_HIERARCHY", []), [])

        # Ensure required sheet keys exist
        for key in [
            "RECRUITMENT_LOG_SHEET_NAME",
            "EVENT_LOG_SHEET_NAME",
            "ATTENDANCE_SHEET_NAME",
        ]:
            if not cfg.get(key):
                warnings.append(f"Recommended setting missing: {key}")

        return errors, warnings

    def set_data(self, new_data: Dict[str, Any]) -> None:
        self.data = new_data


# ------------------------------
# GUI Components
# ------------------------------

class DraggableFieldItem(QtWidgets.QListWidgetItem):
    def __init__(self, field_key: str):
        super().__init__(field_key)
        self.field_key = field_key


class FieldPalette(QtWidgets.QListWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)
        self.model = model
        self.refresh()

    def refresh(self) -> None:
        self.clear()
        for key in self.model.list_fields_palette():
            self.addItem(DraggableFieldItem(key))

    def startDrag(self, supportedActions: QtCore.Qt.DropActions) -> None:
        item = self.currentItem()
        if not item:
            return
        mime = QtCore.QMimeData()
        mime.setText(item.text())
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime)
        pix = QtGui.QPixmap(100, 24)
        pix.fill(QtGui.QColor("#cce5ff"))
        painter = QtGui.QPainter(pix)
        painter.setPen(QtGui.QColor("#004085"))
        painter.drawText(6, 16, item.text())
        painter.end()
        drag.setPixmap(pix)
        drag.exec()


class LayoutGrid(QtWidgets.QTableWidget):
    fieldDropped = QtCore.pyqtSignal(int, int, str)  # row, col, field_key
    anchorPicked = QtCore.pyqtSignal(int, int)

    def __init__(self, rows: int = 30, cols: int = 30):
        super().__init__(rows, cols)
        self.setAcceptDrops(True)
        self._anchor_mode = False
        # Visuals
        self.horizontalHeader().setVisible(True)
        self.verticalHeader().setVisible(True)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        self._update_headers()
        self.setStyleSheet("QTableWidget::item{padding:0px}")

    def _update_headers(self):
        for c in range(self.columnCount()):
            self.setHorizontalHeaderItem(c, QtWidgets.QTableWidgetItem(str(c + 1)))
        for r in range(self.rowCount()):
            self.setVerticalHeaderItem(r, QtWidgets.QTableWidgetItem(str(r + 1)))

    def enable_anchor_pick(self, enable: bool):
        self._anchor_mode = enable
        cursor = QtCore.Qt.CursorShape.CrossCursor if enable else QtCore.Qt.CursorShape.ArrowCursor
        self.viewport().setCursor(cursor)

    def dragEnterEvent(self, e: QtGui.QDragEnterEvent) -> None:
        if e.mimeData().hasText():
            e.acceptProposedAction()
        else:
            super().dragEnterEvent(e)

    def dragMoveEvent(self, e: QtGui.QDragMoveEvent) -> None:
        if e.mimeData().hasText():
            e.acceptProposedAction()
        else:
            super().dragMoveEvent(e)

    def dropEvent(self, e: QtGui.QDropEvent) -> None:
        if not e.mimeData().hasText():
            return super().dropEvent(e)
        pos = e.position().toPoint()
        row = self.rowAt(pos.y())
        col = self.columnAt(pos.x())
        if row < 0 or col < 0:
            return
        field_key = e.mimeData().text()
        self.fieldDropped.emit(row, col, field_key)
        e.acceptProposedAction()

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if self._anchor_mode and e.button() == QtCore.Qt.MouseButton.LeftButton:
            pos = e.position().toPoint()
            row = self.rowAt(pos.y())
            col = self.columnAt(pos.x())
            if row >= 0 and col >= 0:
                self.anchorPicked.emit(row, col)
                return
        super().mousePressEvent(e)


class LayoutDesignerWidget(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self.current_layout: Optional[str] = None
        self.anchor: Optional[Tuple[int, int]] = (5, 5)
        self._build_ui()
        self._connect()
        self._load_initial()

    def _build_ui(self):
        main = QtWidgets.QVBoxLayout(self)

        # Top bar: layout select + actions
        top = QtWidgets.QHBoxLayout()
        self.layout_combo = QtWidgets.QComboBox()
        self.add_layout_btn = QtWidgets.QPushButton("New Layout")
        self.del_layout_btn = QtWidgets.QPushButton("Delete Layout")
        self.anchor_toggle = QtWidgets.QPushButton("Pick Anchor")
        self.anchor_toggle.setCheckable(True)
        self.zoom_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.zoom_slider.setRange(16, 64)
        self.zoom_slider.setValue(28)
        top.addWidget(QtWidgets.QLabel("Layout:"))
        top.addWidget(self.layout_combo, 1)
        top.addWidget(self.add_layout_btn)
        top.addWidget(self.del_layout_btn)
        top.addSpacing(16)
        top.addWidget(self.anchor_toggle)
        top.addSpacing(16)
        top.addWidget(QtWidgets.QLabel("Cell Size"))
        top.addWidget(self.zoom_slider)

        # Body: palette | grid | properties
        body = QtWidgets.QHBoxLayout()
        self.palette = FieldPalette(self.model)
        self.grid = LayoutGrid(40, 40)
        self.props = QtWidgets.QGroupBox("Layout Offsets")
        props_layout = QtWidgets.QVBoxLayout(self.props)
        self.anchor_label = QtWidgets.QLabel("Anchor: (6, 6)")
        self.offsets_list = QtWidgets.QTableWidget(0, 3)
        self.offsets_list.setHorizontalHeaderLabels(["Field", "Row Offset", "Col Offset"])
        self.offsets_list.horizontalHeader().setStretchLastSection(True)
        self.remove_field_btn = QtWidgets.QPushButton("Remove Selected Field")
        props_layout.addWidget(self.anchor_label)
        props_layout.addWidget(self.offsets_list, 1)
        props_layout.addWidget(self.remove_field_btn)

        body.addWidget(self.palette, 0)
        body.addWidget(self.grid, 1)
        body.addWidget(self.props, 0)

        main.addLayout(top)
        main.addLayout(body, 1)

    def _connect(self):
        self.grid.fieldDropped.connect(self._handle_field_dropped)
        self.grid.anchorPicked.connect(self._handle_anchor_picked)
        self.add_layout_btn.clicked.connect(self._add_layout)
        self.del_layout_btn.clicked.connect(self._delete_layout)
        self.anchor_toggle.toggled.connect(self.grid.enable_anchor_pick)
        self.zoom_slider.valueChanged.connect(self._apply_zoom)
        self.layout_combo.currentTextChanged.connect(self._switch_layout)
        self.remove_field_btn.clicked.connect(self._remove_selected_field)
        self.offsets_list.cellChanged.connect(self._offset_cell_changed)

    def _load_initial(self):
        self.layout_combo.clear()
        for name in self.model.list_layouts():
            self.layout_combo.addItem(name)
        if self.layout_combo.count() == 0:
            self.model.add_layout("BILLET_OFFSETS")
            self.layout_combo.addItem("BILLET_OFFSETS")
        self.current_layout = self.layout_combo.currentText()
        self._apply_zoom(self.zoom_slider.value())
        self.refresh()

    def _apply_zoom(self, v: int):
        for r in range(self.grid.rowCount()):
            self.grid.setRowHeight(r, v)
        for c in range(self.grid.columnCount()):
            self.grid.setColumnWidth(c, v * 2)

    def _switch_layout(self, name: str):
        self.current_layout = name
        self.refresh()

    def _add_layout(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "New Layout", "Layout name:")
        if not ok or not name:
            return
        if name in self.model.data["LAYOUT_BLUEPRINTS"]:
            QtWidgets.QMessageBox.warning(self, "Exists", "Layout already exists.")
            return
        self.model.add_layout(name)
        self.layout_combo.addItem(name)
        self.layout_combo.setCurrentText(name)

    def _delete_layout(self):
        name = self.layout_combo.currentText()
        if not name:
            return
        if QtWidgets.QMessageBox.question(self, "Delete", f"Delete layout '{name}'?") != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self.model.remove_layout(name)
        self._load_initial()

    def _handle_anchor_picked(self, row: int, col: int):
        self.anchor = (row, col)
        self.anchor_label.setText(f"Anchor: ({row + 1}, {col + 1})")
        self.anchor_toggle.setChecked(False)
        self.refresh()

    def _handle_field_dropped(self, row: int, col: int, field_key: str):
        if not self.current_layout:
            return
        if not self.anchor:
            QtWidgets.QMessageBox.warning(self, "No Anchor", "Pick an anchor cell first.")
            return
        r_off = row - self.anchor[0]
        c_off = col - self.anchor[1]
        self.model.set_layout_offset(self.current_layout, field_key, r_off, c_off)
        self.refresh()

    def refresh(self):
        # Clear grid contents
        self.grid.clearContents()
        self.offsets_list.blockSignals(True)
        self.offsets_list.setRowCount(0)
        self.offsets_list.blockSignals(False)

        # Draw anchor
        if self.anchor:
            r, c = self.anchor
            item = QtWidgets.QTableWidgetItem("A")
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            item.setForeground(QtGui.QBrush(QtGui.QColor("#1a1a1a")))
            item.setBackground(QtGui.QBrush(QtGui.QColor("#ffd966")))
            self.grid.setItem(r, c, item)

        # Place fields
        layout_def = self.model.data.get("LAYOUT_BLUEPRINTS", {}).get(self.current_layout, {"offsets": {}})
        offsets: Dict[str, Dict[str, int]] = layout_def.get("offsets", {})
        if self.anchor:
            ar, ac = self.anchor
            for field_key, rc in offsets.items():
                rr = ar + int(rc.get("row", 0))
                cc = ac + int(rc.get("col", 0))
                if 0 <= rr < self.grid.rowCount() and 0 <= cc < self.grid.columnCount():
                    item = QtWidgets.QTableWidgetItem(field_key)
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QtGui.QBrush(QtGui.QColor("#003366")))
                    item.setBackground(QtGui.QBrush(QtGui.QColor("#cce5ff")))
                    self.grid.setItem(rr, cc, item)

        # Populate offsets table
        self.offsets_list.blockSignals(True)
        for field_key, rc in sorted(offsets.items()):
            row = self.offsets_list.rowCount()
            self.offsets_list.insertRow(row)
            self.offsets_list.setItem(row, 0, QtWidgets.QTableWidgetItem(field_key))
            self.offsets_list.setItem(row, 1, QtWidgets.QTableWidgetItem(str(rc.get("row", 0))))
            self.offsets_list.setItem(row, 2, QtWidgets.QTableWidgetItem(str(rc.get("col", 0))))
        self.offsets_list.blockSignals(False)
        self.palette.refresh()

    def _remove_selected_field(self):
        row = self.offsets_list.currentRow()
        if row < 0:
            return
        field_key = self.offsets_list.item(row, 0).text()
        if self.current_layout:
            self.model.remove_layout_offset(self.current_layout, field_key)
            self.refresh()

    def _offset_cell_changed(self, row: int, col: int):
        if col not in (1, 2):
            return
        if row < 0:
            return
        field_key = self.offsets_list.item(row, 0).text()
        try:
            r_off = int(self.offsets_list.item(row, 1).text())
            c_off = int(self.offsets_list.item(row, 2).text())
        except Exception:
            return
        if self.current_layout:
            self.model.set_layout_offset(self.current_layout, field_key, r_off, c_off)
            self.refresh()


class RankTable(QtWidgets.QTableWidget):
    def __init__(self):
        super().__init__(0, 2)
        self.setHorizontalHeaderLabels(["Abbr", "Name"])
        self.horizontalHeader().setStretchLastSection(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked | QtWidgets.QAbstractItemView.EditTrigger.EditKeyPressed)

    def to_list(self) -> List[Dict[str, str]]:
        out = []
        for r in range(self.rowCount()):
            abbr = self.item(r, 0).text() if self.item(r, 0) else ""
            name = self.item(r, 1).text() if self.item(r, 1) else ""
            if name.strip():
                out.append({"abbr": abbr.strip(), "name": name.strip()})
        return out

    def load(self, ranks: List[Dict[str, str]]):
        self.setRowCount(0)
        for r in ranks:
            row = self.rowCount()
            self.insertRow(row)
            self.setItem(row, 0, QtWidgets.QTableWidgetItem(r.get("abbr", "")))
            self.setItem(row, 1, QtWidgets.QTableWidgetItem(r.get("name", "")))


class RanksSettingsWidget(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self._build_ui()
        self._connect()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)

        # Left: Ranks
        ranks_box = QtWidgets.QGroupBox("Rank Hierarchy")
        rbox = QtWidgets.QVBoxLayout(ranks_box)
        self.rank_table = RankTable()
        btns = QtWidgets.QHBoxLayout()
        self.add_rank_btn = QtWidgets.QPushButton("Add Rank")
        self.del_rank_btn = QtWidgets.QPushButton("Delete Rank")
        btns.addWidget(self.add_rank_btn)
        btns.addWidget(self.del_rank_btn)
        rbox.addWidget(self.rank_table, 1)
        rbox.addLayout(btns)

        # Right: Settings
        settings_box = QtWidgets.QGroupBox("Core Settings")
        form = QtWidgets.QFormLayout(settings_box)
        self.date_format = QtWidgets.QComboBox()
        self.date_format.addItems(["MM/DD/YY", "DD/MM/YY", "YYYY-MM-DD"]) 
        self.rec_sheet = QtWidgets.QLineEdit()
        self.event_sheet = QtWidgets.QLineEdit()
        self.att_sheet = QtWidgets.QLineEdit()
        self.webhook_url = QtWidgets.QLineEdit()
        self.lock_timeout = QtWidgets.QSpinBox()
        self.lock_timeout.setRange(1000, 120000)
        self.lock_timeout.setSingleStep(1000)
        form.addRow("Date Format", self.date_format)
        form.addRow("Recruit Log Sheet", self.rec_sheet)
        form.addRow("Event Log Sheet", self.event_sheet)
        form.addRow("Attendance Sheet", self.att_sheet)
        form.addRow("Webhook URL", self.webhook_url)
        form.addRow("Lock Timeout (ms)", self.lock_timeout)

        splitter.addWidget(ranks_box)
        splitter.addWidget(settings_box)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter, 1)
        self.save_btn = QtWidgets.QPushButton("Apply Changes")
        layout.addWidget(self.save_btn)

    def _connect(self):
        self.add_rank_btn.clicked.connect(self._add_rank)
        self.del_rank_btn.clicked.connect(self._del_rank)
        self.save_btn.clicked.connect(self._apply_settings)

    def refresh(self):
        self.rank_table.load(self.model.data.get("RANK_HIERARCHY", []))
        self.date_format.setCurrentText(self.model.data.get("DATE_FORMAT", "MM/DD/YY"))
        self.rec_sheet.setText(self.model.data.get("RECRUITMENT_LOG_SHEET_NAME", ""))
        self.event_sheet.setText(self.model.data.get("EVENT_LOG_SHEET_NAME", ""))
        self.att_sheet.setText(self.model.data.get("ATTENDANCE_SHEET_NAME", ""))
        self.webhook_url.setText(self.model.data.get("WEBHOOK_URL", ""))
        self.lock_timeout.setValue(int(self.model.data.get("LOCK_TIMEOUT_MS", 15000)))

    def _add_rank(self):
        row = self.rank_table.rowCount()
        self.rank_table.insertRow(row)
        self.rank_table.setItem(row, 0, QtWidgets.QTableWidgetItem(""))
        self.rank_table.setItem(row, 1, QtWidgets.QTableWidgetItem("New Rank"))

    def _del_rank(self):
        row = self.rank_table.currentRow()
        if row >= 0:
            self.rank_table.removeRow(row)

    def _apply_settings(self):
        self.model.data["RANK_HIERARCHY"] = self.rank_table.to_list()
        self.model.data["DATE_FORMAT"] = self.date_format.currentText()
        self.model.data["RECRUITMENT_LOG_SHEET_NAME"] = self.rec_sheet.text().strip()
        self.model.data["EVENT_LOG_SHEET_NAME"] = self.event_sheet.text().strip()
        self.model.data["ATTENDANCE_SHEET_NAME"] = self.att_sheet.text().strip()
        self.model.data["WEBHOOK_URL"] = self.webhook_url.text().strip()
        self.model.data["LOCK_TIMEOUT_MS"] = int(self.lock_timeout.value())
        QtWidgets.QMessageBox.information(self, "Saved", "Settings applied.")


class SlotEditorDialog(QtWidgets.QDialog):
    def __init__(self, model: ThemisConfigModel, ranks: List[str], layouts: List[str], parent=None):
        super().__init__(parent)
        self.model = model
        self.ranks = ranks
        self.layouts = layouts
        self.result_slot: Optional[Dict[str, Any]] = None
        self._build_ui()

    def _build_ui(self):
        self.setWindowTitle("Edit Slot")
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.title_edit = QtWidgets.QLineEdit()
        self.layout_combo = QtWidgets.QComboBox()
        self.layout_combo.addItems(self.layouts)

        self.rank_mode = QtWidgets.QComboBox()
        self.rank_mode.addItems(["Single Rank", "Multiple Ranks"])
        self.single_rank = QtWidgets.QComboBox()
        self.single_rank.addItems(["(none)"] + self.ranks)
        self.multi_ranks = QtWidgets.QListWidget()
        self.multi_ranks.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        for r in self.ranks:
            self.multi_ranks.addItem(r)

        self.count_spin = QtWidgets.QSpinBox()
        self.count_spin.setRange(1, 200)
        self.count_spin.setValue(1)

        self.location_mode = QtWidgets.QComboBox()
        self.location_mode.addItems(["Rows List", "Row Range", "Explicit Coordinates"])
        # Rows list
        self.rows_list_edit = QtWidgets.QLineEdit()
        self.rows_list_edit.setPlaceholderText("e.g. 12, 15, 18")
        # Range
        self.start_row = QtWidgets.QSpinBox(); self.start_row.setRange(1, 10000)
        self.end_row = QtWidgets.QSpinBox(); self.end_row.setRange(1, 10000)
        # Explicit
        self.coords_table = QtWidgets.QTableWidget(0, 2)
        self.coords_table.setHorizontalHeaderLabels(["Row", "Col"])
        self.add_coord_btn = QtWidgets.QPushButton("Add Coordinate")
        self.remove_coord_btn = QtWidgets.QPushButton("Remove Coordinate")

        self.col_override = QtWidgets.QSpinBox(); self.col_override.setRange(1, 10000)
        self.sheet_override = QtWidgets.QLineEdit()
        self.sheet_override.setPlaceholderText("Optional override sheet name")

        form.addRow("Title (optional)", self.title_edit)
        form.addRow("Layout", self.layout_combo)
        form.addRow("Rank Mode", self.rank_mode)
        form.addRow("Single Rank", self.single_rank)
        form.addRow("Multiple Ranks", self.multi_ranks)
        form.addRow("Count", self.count_spin)
        form.addRow("Location Mode", self.location_mode)
        form.addRow("Rows List", self.rows_list_edit)
        row_range_box = QtWidgets.QHBoxLayout(); row_range_box.addWidget(self.start_row); row_range_box.addWidget(QtWidgets.QLabel("to")); row_range_box.addWidget(self.end_row)
        form.addRow("Row Range", row_range_box)
        form.addRow("Explicit Coords", self.coords_table)
        coords_btn_line = QtWidgets.QHBoxLayout(); coords_btn_line.addWidget(self.add_coord_btn); coords_btn_line.addWidget(self.remove_coord_btn)
        form.addRow("", coords_btn_line)
        form.addRow("Col Override", self.col_override)
        form.addRow("Sheet Override", self.sheet_override)

        layout.addLayout(form)

        btns = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        layout.addWidget(btns)

        self.rank_mode.currentIndexChanged.connect(self._toggle_rank_inputs)
        self.location_mode.currentIndexChanged.connect(self._toggle_location_inputs)
        self.add_coord_btn.clicked.connect(self._add_coord_row)
        self.remove_coord_btn.clicked.connect(self._remove_coord_row)
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)

        self._toggle_rank_inputs()
        self._toggle_location_inputs()

    def _toggle_rank_inputs(self):
        single = self.rank_mode.currentIndex() == 0
        self.single_rank.setEnabled(single)
        self.multi_ranks.setEnabled(not single)

    def _toggle_location_inputs(self):
        mode = self.location_mode.currentIndex()
        self.rows_list_edit.setEnabled(mode == 0)
        self.start_row.setEnabled(mode == 1)
        self.end_row.setEnabled(mode == 1)
        self.coords_table.setEnabled(mode == 2)
        self.add_coord_btn.setEnabled(mode == 2)
        self.remove_coord_btn.setEnabled(mode == 2)

    def _add_coord_row(self):
        r = self.coords_table.rowCount()
        self.coords_table.insertRow(r)
        self.coords_table.setItem(r, 0, QtWidgets.QTableWidgetItem("1"))
        self.coords_table.setItem(r, 1, QtWidgets.QTableWidgetItem("1"))

    def _remove_coord_row(self):
        r = self.coords_table.currentRow()
        if r >= 0:
            self.coords_table.removeRow(r)

    def load_from(self, slot: Dict[str, Any]):
        self.title_edit.setText(slot.get("title", ""))
        lay = slot.get("layout")
        if lay:
            ix = self.layout_combo.findText(lay)
            if ix >= 0:
                self.layout_combo.setCurrentIndex(ix)
        if "rank" in slot:
            self.rank_mode.setCurrentIndex(0)
            rname = slot.get("rank")
            ix = max(0, self.single_rank.findText(rname))
            self.single_rank.setCurrentIndex(ix)
        elif "ranks" in slot:
            self.rank_mode.setCurrentIndex(1)
            rset = set(slot.get("ranks", []))
            for i in range(self.multi_ranks.count()):
                it = self.multi_ranks.item(i)
                it.setSelected(it.text() in rset)
        self.count_spin.setValue(int(slot.get("count", 1)))
        loc = slot.get("location", {})
        col = loc.get("col")
        if col is not None:
            self.col_override.setValue(int(col))
        sheet = loc.get("sheetName")
        if sheet:
            self.sheet_override.setText(sheet)
        if "rows" in loc:
            self.location_mode.setCurrentIndex(0)
            self.rows_list_edit.setText(", ".join(str(x) for x in loc.get("rows", [])))
        elif "startRow" in loc and "endRow" in loc:
            self.location_mode.setCurrentIndex(1)
            self.start_row.setValue(int(loc.get("startRow", 1)))
            self.end_row.setValue(int(loc.get("endRow", 1)))
        elif "locations" in slot:
            self.location_mode.setCurrentIndex(2)
            self.coords_table.setRowCount(0)
            for coord in slot.get("locations", []):
                r = self.coords_table.rowCount()
                self.coords_table.insertRow(r)
                self.coords_table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(coord.get("row", 1))))
                self.coords_table.setItem(r, 1, QtWidgets.QTableWidgetItem(str(coord.get("col", 1))))

    def _accept(self):
        out: Dict[str, Any] = {}
        title = self.title_edit.text().strip()
        if title:
            out["title"] = title
        lay = self.layout_combo.currentText().strip()
        if lay:
            out["layout"] = lay
        if self.rank_mode.currentIndex() == 0:
            r = self.single_rank.currentText()
            if r and r != "(none)":
                out["rank"] = r
        else:
            rs = [self.multi_ranks.item(i).text() for i in range(self.multi_ranks.count()) if self.multi_ranks.item(i).isSelected()]
            if rs:
                out["ranks"] = rs
        out["count"] = int(self.count_spin.value())
        loc: Dict[str, Any] = {}
        if self.location_mode.currentIndex() == 0:
            rows_txt = self.rows_list_edit.text().strip()
            rows = []
            if rows_txt:
                for part in rows_txt.split(','):
                    try:
                        rows.append(int(part.strip()))
                    except Exception:
                        pass
            if rows:
                loc["rows"] = rows
        elif self.location_mode.currentIndex() == 1:
            loc["startRow"] = int(self.start_row.value())
            loc["endRow"] = int(self.end_row.value())
        else:
            coords = []
            for r in range(self.coords_table.rowCount()):
                try:
                    rr = int(self.coords_table.item(r, 0).text())
                    cc = int(self.coords_table.item(r, 1).text())
                    coords.append({"row": rr, "col": cc})
                except Exception:
                    pass
            if coords:
                out["locations"] = coords
        if self.col_override.value() > 0:
            loc["col"] = int(self.col_override.value())
        sheet = self.sheet_override.text().strip()
        if sheet:
            loc["sheetName"] = sheet
        if loc:
            out["location"] = loc
        self.result_slot = out
        self.accept()


class SlotBlueprintsWidget(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self._build_ui()
        self._connect()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        left = QtWidgets.QVBoxLayout()
        right = QtWidgets.QVBoxLayout()

        self.bp_list = QtWidgets.QListWidget()
        self.add_bp_btn = QtWidgets.QPushButton("Add Blueprint")
        self.del_bp_btn = QtWidgets.QPushButton("Delete Blueprint")
        left.addWidget(QtWidgets.QLabel("Blueprints"))
        left.addWidget(self.bp_list, 1)
        left_btns = QtWidgets.QHBoxLayout(); left_btns.addWidget(self.add_bp_btn); left_btns.addWidget(self.del_bp_btn)
        left.addLayout(left_btns)

        self.slots_table = QtWidgets.QTableWidget(0, 4)
        self.slots_table.setHorizontalHeaderLabels(["Title", "Layout", "Rank(s)", "Location"])
        self.slots_table.horizontalHeader().setStretchLastSection(True)
        self.add_slot_btn = QtWidgets.QPushButton("Add Slot")
        self.edit_slot_btn = QtWidgets.QPushButton("Edit Slot")
        self.del_slot_btn = QtWidgets.QPushButton("Delete Slot")
        btns = QtWidgets.QHBoxLayout(); btns.addWidget(self.add_slot_btn); btns.addWidget(self.edit_slot_btn); btns.addWidget(self.del_slot_btn)
        right.addWidget(QtWidgets.QLabel("Slots"))
        right.addWidget(self.slots_table, 1)
        right.addLayout(btns)

        layout.addLayout(left, 0)
        layout.addLayout(right, 1)

    def _connect(self):
        self.add_bp_btn.clicked.connect(self._add_bp)
        self.del_bp_btn.clicked.connect(self._del_bp)
        self.bp_list.currentTextChanged.connect(self._load_slots)
        self.add_slot_btn.clicked.connect(self._add_slot)
        self.edit_slot_btn.clicked.connect(self._edit_slot)
        self.del_slot_btn.clicked.connect(self._del_slot)

    def refresh(self):
        self.bp_list.clear()
        for name in sorted(self.model.data.get("SLOT_BLUEPRINTS", {}).keys()):
            self.bp_list.addItem(name)
        if self.bp_list.count() > 0:
            self.bp_list.setCurrentRow(0)
        else:
            self.slots_table.setRowCount(0)

    def _add_bp(self):
        name, ok = QtWidgets.QInputDialog.getText(self, "New Slot Blueprint", "Name:")
        if not ok or not name:
            return
        if name in self.model.data.get("SLOT_BLUEPRINTS", {}):
            QtWidgets.QMessageBox.warning(self, "Exists", "Blueprint already exists.")
            return
        self.model.data.setdefault("SLOT_BLUEPRINTS", {})[name] = []
        self.refresh()
        items = self.bp_list.findItems(name, QtCore.Qt.MatchFlag.MatchExactly)
        if items:
            self.bp_list.setCurrentItem(items[0])

    def _del_bp(self):
        name = self.bp_list.currentItem().text() if self.bp_list.currentItem() else ""
        if not name:
            return
        if QtWidgets.QMessageBox.question(self, "Delete", f"Delete blueprint '{name}'?") != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            del self.model.data["SLOT_BLUEPRINTS"][name]
        except KeyError:
            pass
        self.refresh()

    def _load_slots(self, name: str):
        self.slots_table.setRowCount(0)
        if not name:
            return
        for slot in self.model.data.get("SLOT_BLUEPRINTS", {}).get(name, []):
            self._append_slot_row(slot)

    def _append_slot_row(self, slot: Dict[str, Any]):
        r = self.slots_table.rowCount()
        self.slots_table.insertRow(r)
        self.slots_table.setItem(r, 0, QtWidgets.QTableWidgetItem(slot.get("title", "")))
        self.slots_table.setItem(r, 1, QtWidgets.QTableWidgetItem(slot.get("layout", "")))
        rank_txt = slot.get("rank") or ", ".join(slot.get("ranks", []))
        self.slots_table.setItem(r, 2, QtWidgets.QTableWidgetItem(rank_txt))
        loc = slot.get("location", {})
        if "rows" in loc:
            loc_txt = f"rows={loc.get('rows')}"
        elif "startRow" in loc and "endRow" in loc:
            loc_txt = f"{loc.get('startRow')}..{loc.get('endRow')}"
        elif "locations" in slot:
            loc_txt = f"coords x{len(slot['locations'])}"
        else:
            loc_txt = ""
        if "col" in loc:
            loc_txt += f", col={loc['col']}"
        if loc.get("sheetName"):
            loc_txt += f", sheet={loc['sheetName']}"
        self.slots_table.setItem(r, 3, QtWidgets.QTableWidgetItem(loc_txt))

    def _add_slot(self):
        name = self.bp_list.currentItem().text() if self.bp_list.currentItem() else ""
        if not name:
            return
        ranks = [r.get("name") for r in self.model.data.get("RANK_HIERARCHY", [])]
        layouts = list(self.model.data.get("LAYOUT_BLUEPRINTS", {}).keys())
        dlg = SlotEditorDialog(self.model, ranks, layouts, self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted and dlg.result_slot:
            self.model.data["SLOT_BLUEPRINTS"][name].append(dlg.result_slot)
            self._append_slot_row(dlg.result_slot)

    def _edit_slot(self):
        name = self.bp_list.currentItem().text() if self.bp_list.currentItem() else ""
        row = self.slots_table.currentRow()
        if not name or row < 0:
            return
        slot = self.model.data["SLOT_BLUEPRINTS"][name][row]
        ranks = [r.get("name") for r in self.model.data.get("RANK_HIERARCHY", [])]
        layouts = list(self.model.data.get("LAYOUT_BLUEPRINTS", {}).keys())
        dlg = SlotEditorDialog(self.model, ranks, layouts, self)
        dlg.load_from(slot)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted and dlg.result_slot:
            self.model.data["SLOT_BLUEPRINTS"][name][row] = dlg.result_slot
            self._load_slots(name)

    def _del_slot(self):
        name = self.bp_list.currentItem().text() if self.bp_list.currentItem() else ""
        row = self.slots_table.currentRow()
        if not name or row < 0:
            return
        del self.model.data["SLOT_BLUEPRINTS"][name][row]
        self.slots_table.removeRow(row)


class OrgNodeEditor(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()

    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self.current_node: Optional[Dict[str, Any]] = None
        self._build_ui()
        self._connect()

    def _build_ui(self):
        form = QtWidgets.QFormLayout(self)
        self.name_edit = QtWidgets.QLineEdit()
        self.sheet_edit = QtWidgets.QLineEdit()
        self.layout_combo = QtWidgets.QComboBox()
        self.layout_combo.addItem("")
        self.layout_combo.addItems(self.model.list_layouts())
        self.start_col = QtWidgets.QSpinBox(); self.start_col.setRange(1, 10000)
        self.use_slots_combo = QtWidgets.QComboBox(); self.use_slots_combo.addItem(""); self.use_slots_combo.addItems(sorted(self.model.data.get("SLOT_BLUEPRINTS", {}).keys()))
        self.shortcuts_edit = QtWidgets.QLineEdit(); self.shortcuts_edit.setPlaceholderText("Comma-separated e.g. VI 1A, VI 1B")
        self.log_short_name = QtWidgets.QCheckBox("Use short section name when logging")
        self.event_log_row = QtWidgets.QSpinBox(); self.event_log_row.setRange(1, 10000)
        self.event_log_col = QtWidgets.QSpinBox(); self.event_log_col.setRange(1, 10000)
        form.addRow("Name", self.name_edit)
        form.addRow("Sheet Name", self.sheet_edit)
        form.addRow("Layout", self.layout_combo)
        form.addRow("Start Col", self.start_col)
        form.addRow("Use Slots From", self.use_slots_combo)
        form.addRow("Shortcuts", self.shortcuts_edit)
        form.addRow(self.log_short_name)
        h = QtWidgets.QHBoxLayout(); h.addWidget(self.event_log_row); h.addWidget(QtWidgets.QLabel("col")); h.addWidget(self.event_log_col)
        form.addRow("Event Log Start", h)

        # Node specific slots list
        self.slots_table = QtWidgets.QTableWidget(0, 4)
        self.slots_table.setHorizontalHeaderLabels(["Title", "Layout", "Rank(s)", "Location"])
        self.slots_table.horizontalHeader().setStretchLastSection(True)
        self.add_slot_btn = QtWidgets.QPushButton("Add Node Slot")
        self.edit_slot_btn = QtWidgets.QPushButton("Edit Node Slot")
        self.del_slot_btn = QtWidgets.QPushButton("Delete Node Slot")
        btns = QtWidgets.QHBoxLayout(); btns.addWidget(self.add_slot_btn); btns.addWidget(self.edit_slot_btn); btns.addWidget(self.del_slot_btn)
        form.addRow(QtWidgets.QLabel("Node Slots"))
        form.addRow(self.slots_table)
        form.addRow(btns)

    def _connect(self):
        self.name_edit.editingFinished.connect(self._apply)
        self.sheet_edit.editingFinished.connect(self._apply)
        self.layout_combo.currentTextChanged.connect(self._apply)
        self.start_col.valueChanged.connect(self._apply)
        self.use_slots_combo.currentTextChanged.connect(self._apply)
        self.shortcuts_edit.editingFinished.connect(self._apply)
        self.log_short_name.stateChanged.connect(self._apply)
        self.event_log_row.valueChanged.connect(self._apply)
        self.event_log_col.valueChanged.connect(self._apply)
        self.add_slot_btn.clicked.connect(self._add_slot)
        self.edit_slot_btn.clicked.connect(self._edit_slot)
        self.del_slot_btn.clicked.connect(self._del_slot)

    def load(self, node: Optional[Dict[str, Any]]):
        self.current_node = node
        if not node:
            for w in [self.name_edit, self.sheet_edit, self.layout_combo, self.start_col, self.use_slots_combo, self.shortcuts_edit, self.log_short_name]:
                w.setEnabled(False)
            self.slots_table.setRowCount(0)
            return
        for w in [self.name_edit, self.sheet_edit, self.layout_combo, self.start_col, self.use_slots_combo, self.shortcuts_edit, self.log_short_name]:
            w.setEnabled(True)
        self.name_edit.setText(node.get("name", ""))
        self.sheet_edit.setText(node.get("sheetName", ""))
        ix = max(0, self.layout_combo.findText(node.get("layout", "")))
        self.layout_combo.setCurrentIndex(ix)
        self.start_col.setValue(int(node.get("location", {}).get("startCol", 1)))
        ix2 = max(0, self.use_slots_combo.findText(node.get("useSlotsFrom", "")))
        self.use_slots_combo.setCurrentIndex(ix2)
        self.shortcuts_edit.setText(", ".join(node.get("shortcuts", [])))
        self.log_short_name.setChecked(bool(node.get("logShortSectionName", False)))
        if node.get("eventLogStart"):
            self.event_log_row.setValue(int(node["eventLogStart"].get("row", 1)))
            self.event_log_col.setValue(int(node["eventLogStart"].get("col", 1)))
        else:
            self.event_log_row.setValue(1)
            self.event_log_col.setValue(1)
        # slots
        self.slots_table.setRowCount(0)
        for slot in node.get("slots", []):
            self._append_slot_row(slot)

    def _apply(self):
        n = self.current_node
        if not n:
            return
        n["name"] = self.name_edit.text().strip()
        sn = self.sheet_edit.text().strip()
        if sn:
            n["sheetName"] = sn
        else:
            n.pop("sheetName", None)
        lay = self.layout_combo.currentText().strip()
        if lay:
            n["layout"] = lay
        else:
            n.pop("layout", None)
        sc = int(self.start_col.value())
        if sc > 0:
            n.setdefault("location", {})["startCol"] = sc
        else:
            if "location" in n:
                n["location"].pop("startCol", None)
        usf = self.use_slots_combo.currentText().strip()
        if usf:
            n["useSlotsFrom"] = usf
        else:
            n.pop("useSlotsFrom", None)
        shortcuts = [s.strip() for s in self.shortcuts_edit.text().split(',') if s.strip()]
        if shortcuts:
            n["shortcuts"] = shortcuts
        else:
            n.pop("shortcuts", None)
        n["logShortSectionName"] = self.log_short_name.isChecked()
        if self.event_log_row.value() > 0 and self.event_log_col.value() > 0:
            n["eventLogStart"] = {"row": int(self.event_log_row.value()), "col": int(self.event_log_col.value())}
        else:
            n.pop("eventLogStart", None)
        self.changed.emit()

    def _append_slot_row(self, slot: Dict[str, Any]):
        r = self.slots_table.rowCount()
        self.slots_table.insertRow(r)
        self.slots_table.setItem(r, 0, QtWidgets.QTableWidgetItem(slot.get("title", "")))
        self.slots_table.setItem(r, 1, QtWidgets.QTableWidgetItem(slot.get("layout", "")))
        rank_txt = slot.get("rank") or ", ".join(slot.get("ranks", []))
        self.slots_table.setItem(r, 2, QtWidgets.QTableWidgetItem(rank_txt))
        loc = slot.get("location", {})
        if "col" in loc and "row" in loc:
            loc_txt = f"r{loc['row']} c{loc['col']}"
        elif "col" in loc:
            loc_txt = f"col={loc['col']}"
        else:
            if "rows" in loc:
                loc_txt = f"rows={loc.get('rows')}"
            elif "startRow" in loc and "endRow" in loc:
                loc_txt = f"{loc.get('startRow')}..{loc.get('endRow')}"
            else:
                loc_txt = ""
        if loc.get("sheetName"):
            loc_txt += f", sheet={loc['sheetName']}"
        self.slots_table.setItem(r, 3, QtWidgets.QTableWidgetItem(loc_txt))

    def _add_slot(self):
        if not self.current_node:
            return
        ranks = [r.get("name") for r in self.model.data.get("RANK_HIERARCHY", [])]
        layouts = list(self.model.data.get("LAYOUT_BLUEPRINTS", {}).keys())
        dlg = SlotEditorDialog(self.model, ranks, layouts, self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted and dlg.result_slot:
            self.current_node.setdefault("slots", []).append(dlg.result_slot)
            self._append_slot_row(dlg.result_slot)
            self.changed.emit()

    def _edit_slot(self):
        if not self.current_node:
            return
        row = self.slots_table.currentRow()
        if row < 0:
            return
        slot = self.current_node.get("slots", [])[row]
        ranks = [r.get("name") for r in self.model.data.get("RANK_HIERARCHY", [])]
        layouts = list(self.model.data.get("LAYOUT_BLUEPRINTS", {}).keys())
        dlg = SlotEditorDialog(self.model, ranks, layouts, self)
        dlg.load_from(slot)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted and dlg.result_slot:
            self.current_node["slots"][row] = dlg.result_slot
            self.load(self.current_node)
            self.changed.emit()

    def _del_slot(self):
        if not self.current_node:
            return
        row = self.slots_table.currentRow()
        if row < 0:
            return
        del self.current_node["slots"][row]
        self.slots_table.removeRow(row)
        self.changed.emit()


class OrganizationEditorWidget(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self._build_ui()
        self._connect()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        left = QtWidgets.QVBoxLayout()
        right = QtWidgets.QVBoxLayout()

        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Sheet", "Layout", "Start Col", "Slots From"]) 
        self.add_root_btn = QtWidgets.QPushButton("Add Root")
        self.add_child_btn = QtWidgets.QPushButton("Add Child")
        self.del_node_btn = QtWidgets.QPushButton("Delete")
        btns = QtWidgets.QHBoxLayout(); btns.addWidget(self.add_root_btn); btns.addWidget(self.add_child_btn); btns.addWidget(self.del_node_btn)
        left.addWidget(self.tree, 1)
        left.addLayout(btns)

        self.editor = OrgNodeEditor(self.model)
        right.addWidget(self.editor)

        layout.addLayout(left, 1)
        layout.addLayout(right, 1)

    def _connect(self):
        self.add_root_btn.clicked.connect(self._add_root)
        self.add_child_btn.clicked.connect(self._add_child)
        self.del_node_btn.clicked.connect(self._del_node)
        self.tree.currentItemChanged.connect(self._sel_changed)
        self.editor.changed.connect(self._sync_tree_item)

    def refresh(self):
        self.tree.clear()
        for node in self.model.data.get("ORGANIZATION_HIERARCHY", []):
            self._add_node_to_tree(None, node)
        self.tree.expandAll()
        if self.tree.topLevelItemCount() > 0:
            self.tree.setCurrentItem(self.tree.topLevelItem(0))

    def _node_summary(self, n: Dict[str, Any]) -> List[str]:
        return [
            n.get("name", ""),
            n.get("sheetName", ""),
            n.get("layout", ""),
            str(n.get("location", {}).get("startCol", "")),
            n.get("useSlotsFrom", ""),
        ]

    def _add_node_to_tree(self, parent_item: Optional[QtWidgets.QTreeWidgetItem], node: Dict[str, Any]):
        cols = self._node_summary(node)
        item = QtWidgets.QTreeWidgetItem(cols)
        item.setData(0, QtCore.Qt.ItemDataRole.UserRole, node)
        if parent_item is None:
            self.tree.addTopLevelItem(item)
        else:
            parent_item.addChild(item)
        for child in node.get("children", []):
            self._add_node_to_tree(item, child)

    def _add_root(self):
        node = {"name": "New Node", "children": []}
        self.model.data.setdefault("ORGANIZATION_HIERARCHY", []).append(node)
        self.refresh()

    def _add_child(self):
        item = self.tree.currentItem()
        if not item:
            return
        node = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        child = {"name": "Child", "children": []}
        node.setdefault("children", []).append(child)
        self.refresh()

    def _del_node(self):
        item = self.tree.currentItem()
        if not item:
            return
        node = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        # Remove from model
        def remove_from(nodes, target):
            for i, n in enumerate(list(nodes)):
                if n is target:
                    del nodes[i]
                    return True
                if remove_from(n.get("children", []), target):
                    return True
            return False
        remove_from(self.model.data.get("ORGANIZATION_HIERARCHY", []), node)
        self.refresh()

    def _sel_changed(self, cur, prev):
        node = cur.data(0, QtCore.Qt.ItemDataRole.UserRole) if cur else None
        self.editor.load(node)

    def _sync_tree_item(self):
        item = self.tree.currentItem()
        if not item:
            return
        node = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        cols = self._node_summary(node)
        for i, txt in enumerate(cols):
            item.setText(i, txt)


class FieldsValidationWidget(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self._build_ui()
        self._connect()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget()

        # CUSTOM FIELDS
        custom_tab = QtWidgets.QWidget(); custom_layout = QtWidgets.QVBoxLayout(custom_tab)
        self.fields_table = QtWidgets.QTableWidget(0, 6)
        self.fields_table.setHorizontalHeaderLabels(["key", "label", "offsetKey", "defaultValue", "type", "validation(JSON)"])
        self.fields_table.horizontalHeader().setStretchLastSection(True)
        f_btns = QtWidgets.QHBoxLayout(); self.add_field_btn = QtWidgets.QPushButton("Add Field"); self.del_field_btn = QtWidgets.QPushButton("Delete Field"); f_btns.addWidget(self.add_field_btn); f_btns.addWidget(self.del_field_btn)
        custom_layout.addWidget(self.fields_table, 1)
        custom_layout.addLayout(f_btns)

        # VALIDATION RULES
        valid_tab = QtWidgets.QWidget(); valid_layout = QtWidgets.QVBoxLayout(valid_tab)
        self.valid_table = QtWidgets.QTableWidget(0, 2)
        self.valid_table.setHorizontalHeaderLabels(["Rule Key", "Definition (JSON)"])
        self.valid_table.horizontalHeader().setStretchLastSection(True)
        v_btns = QtWidgets.QHBoxLayout(); self.add_valid_btn = QtWidgets.QPushButton("Add Rule"); self.del_valid_btn = QtWidgets.QPushButton("Delete Rule"); v_btns.addWidget(self.add_valid_btn); v_btns.addWidget(self.del_valid_btn)
        valid_layout.addWidget(self.valid_table, 1)
        valid_layout.addLayout(v_btns)

        tabs.addTab(custom_tab, "Custom Fields")
        tabs.addTab(valid_tab, "Validation Rules")
        layout.addWidget(tabs)

        self.apply_btn = QtWidgets.QPushButton("Apply Changes")
        layout.addWidget(self.apply_btn)

    def _connect(self):
        self.add_field_btn.clicked.connect(self._add_field)
        self.del_field_btn.clicked.connect(self._del_field)
        self.add_valid_btn.clicked.connect(self._add_valid)
        self.del_valid_btn.clicked.connect(self._del_valid)
        self.apply_btn.clicked.connect(self._apply)

    def refresh(self):
        # Fields
        self.fields_table.setRowCount(0)
        for f in self.model.data.get("CUSTOM_FIELDS", []):
            r = self.fields_table.rowCount(); self.fields_table.insertRow(r)
            self.fields_table.setItem(r, 0, QtWidgets.QTableWidgetItem(f.get("key", "")))
            self.fields_table.setItem(r, 1, QtWidgets.QTableWidgetItem(f.get("label", "")))
            self.fields_table.setItem(r, 2, QtWidgets.QTableWidgetItem(f.get("offsetKey", "")))
            self.fields_table.setItem(r, 3, QtWidgets.QTableWidgetItem(json.dumps(f.get("defaultValue", ""))))
            self.fields_table.setItem(r, 4, QtWidgets.QTableWidgetItem(f.get("type", "")))
            self.fields_table.setItem(r, 5, QtWidgets.QTableWidgetItem(pretty_json(f.get("validation", {}))))
        # Validation rules
        self.valid_table.setRowCount(0)
        for k, v in self.model.data.get("VALIDATION_RULES", {}).items():
            r = self.valid_table.rowCount(); self.valid_table.insertRow(r)
            self.valid_table.setItem(r, 0, QtWidgets.QTableWidgetItem(str(k)))
            self.valid_table.setItem(r, 1, QtWidgets.QTableWidgetItem(pretty_json(v)))

    def _add_field(self):
        r = self.fields_table.rowCount(); self.fields_table.insertRow(r)
        self.fields_table.setItem(r, 0, QtWidgets.QTableWidgetItem("phase"))
        self.fields_table.setItem(r, 1, QtWidgets.QTableWidgetItem("Phase"))
        self.fields_table.setItem(r, 2, QtWidgets.QTableWidgetItem("phase"))
        self.fields_table.setItem(r, 3, QtWidgets.QTableWidgetItem("1"))
        self.fields_table.setItem(r, 4, QtWidgets.QTableWidgetItem("integer"))
        self.fields_table.setItem(r, 5, QtWidgets.QTableWidgetItem(pretty_json({"min": 1, "max": 3})))

    def _del_field(self):
        r = self.fields_table.currentRow()
        if r >= 0:
            self.fields_table.removeRow(r)

    def _add_valid(self):
        r = self.valid_table.rowCount(); self.valid_table.insertRow(r)
        self.valid_table.setItem(r, 0, QtWidgets.QTableWidgetItem("USERNAME"))
        self.valid_table.setItem(r, 1, QtWidgets.QTableWidgetItem(pretty_json({"REGEX": "^[a-zA-Z0-9_]+$"})))

    def _del_valid(self):
        r = self.valid_table.currentRow()
        if r >= 0:
            self.valid_table.removeRow(r)

    def _apply(self):
        # Fields
        fields = []
        for r in range(self.fields_table.rowCount()):
            key = self.fields_table.item(r, 0).text().strip() if self.fields_table.item(r, 0) else ""
            if not key:
                continue
            label = self.fields_table.item(r, 1).text().strip() if self.fields_table.item(r, 1) else ""
            offset_key = self.fields_table.item(r, 2).text().strip() if self.fields_table.item(r, 2) else ""
            default_val_txt = self.fields_table.item(r, 3).text().strip() if self.fields_table.item(r, 3) else "" 
            try:
                default_val = json.loads(default_val_txt) if default_val_txt else None
            except Exception:
                default_val = default_val_txt
            typ = self.fields_table.item(r, 4).text().strip() if self.fields_table.item(r, 4) else ""
            val_txt = self.fields_table.item(r, 5).text().strip() if self.fields_table.item(r, 5) else "{}"
            try:
                validation = json.loads(val_txt) if val_txt else {}
            except Exception:
                try:
                    validation = json.loads(sanitize_js_like_to_json(val_txt))
                except Exception:
                    validation = {}
            fields.append({
                "key": key,
                "label": label,
                "offsetKey": offset_key,
                "defaultValue": default_val,
                "type": typ,
                "validation": validation,
            })
        self.model.data["CUSTOM_FIELDS"] = fields

        # Validation rules
        rules = {}
        for r in range(self.valid_table.rowCount()):
            k = self.valid_table.item(r, 0).text().strip() if self.valid_table.item(r, 0) else ""
            vtxt = self.valid_table.item(r, 1).text().strip() if self.valid_table.item(r, 1) else "{}"
            if not k:
                continue
            try:
                v = json.loads(vtxt)
            except Exception:
                try:
                    v = json.loads(sanitize_js_like_to_json(vtxt))
                except Exception:
                    v = {}
            rules[k] = v
        self.model.data["VALIDATION_RULES"] = rules

        QtWidgets.QMessageBox.information(self, "Saved", "Fields and validation updated.")


@dataclass
class ResolvedInstance:
    sheet: str
    row: int
    col: int
    layout: str
    offsets: Dict[str, Any]
    node_path_names: List[str]
    node_ref: Dict[str, Any]
    slot_ref: Dict[str, Any]
    origin: str  # 'blueprint' or 'node'
    origin_name: Optional[str]
    slot_index: Optional[int]
    coord_strategy: str  # 'locations'|'rows'|'range'|'row'
    coord_index: Optional[int]
    col_source: str  # 'loc'|'slot'|'node'


class ConfigResolver:
    def __init__(self, model: ThemisConfigModel):
        self.model = model

    @staticmethod
    def _find_in_path(path: List[Dict[str, Any]], prop: str) -> Optional[Any]:
        for i in range(len(path) - 1, -1, -1):
            if prop in path[i]:
                return path[i][prop]
        return None

    def _expand_slot(self, slot: Dict[str, Any], path: List[Dict[str, Any]], current_sheet: str, node: Dict[str, Any], origin: str, origin_name: Optional[str], slot_index: int) -> List[ResolvedInstance]:
        results: List[ResolvedInstance] = []
        layout = slot.get("layout") or self._find_in_path(path, "layout") or ""
        offsets = self.model.data.get("LAYOUT_BLUEPRINTS", {}).get(layout, {}).get("offsets", {})
        loc = slot.get("location", {}) or {}
        node_loc = node.get("location", {}) or {}
        if "col" in loc:
            default_col = int(loc.get("col") or 1)
            col_source = "slot"
        elif "startCol" in node_loc:
            default_col = int(node_loc.get("startCol") or 1)
            col_source = "node"
        else:
            default_col = 1
            col_source = "node"
        sheet = loc.get("sheetName") or current_sheet or "Sheet1"

        def make_instance(r: int, c: int, coord_strategy: str, coord_index: Optional[int], colsrc: str) -> ResolvedInstance:
            return ResolvedInstance(
                sheet=sheet,
                row=int(r),
                col=int(c),
                layout=layout,
                offsets=offsets,
                node_path_names=[n.get("name", "") for n in path],
                node_ref=node,
                slot_ref=slot,
                origin=origin,
                origin_name=origin_name,
                slot_index=slot_index,
                coord_strategy=coord_strategy,
                coord_index=coord_index,
                col_source=colsrc,
            )

        if "locations" in slot:
            for i, lc in enumerate(slot["locations"]):
                rr = int(lc.get("row", 1))
                cc = int(lc.get("col", default_col))
                colsrc = "loc" if "col" in lc else ("slot" if "col" in loc else "node")
                results.append(make_instance(rr, cc, "locations", i, colsrc))
        elif "rows" in loc:
            for i, rr in enumerate(loc["rows"]):
                results.append(make_instance(int(rr), default_col, "rows", i, col_source))
        elif "row" in loc:
            results.append(make_instance(int(loc["row"]), default_col, "row", None, col_source))
        elif "startRow" in loc and "endRow" in loc:
            startR = int(loc["startRow"]) ; endR = int(loc["endRow"])
            k = 0
            for rr in range(startR, endR + 1):
                results.append(make_instance(int(rr), default_col, "range", k, col_source))
                k += 1
        return results

    def resolve_nodes(self, nodes: List[Dict[str, Any]]) -> List[ResolvedInstance]:
        res: List[ResolvedInstance] = []

        def visit(nodes_, path):
            for node in nodes_:
                path2 = path + [node]
                current_sheet = self._find_in_path(path2, "sheetName")
                # Node specific slots
                for idx, s in enumerate(node.get("slots", []) or []):
                    res.extend(self._expand_slot(s, path2, current_sheet, node, "node", None, idx))
                # Blueprint slots
                bp = node.get("useSlotsFrom")
                if bp and bp in (self.model.data.get("SLOT_BLUEPRINTS", {}) or {}):
                    for idx, s in enumerate(self.model.data["SLOT_BLUEPRINTS"][bp]):
                        res.extend(self._expand_slot(s, path2, current_sheet, node, "blueprint", bp, idx))
                # children
                if node.get("children"):
                    visit(node["children"], path2)
        visit(nodes, [])
        return res

    def resolve(self) -> List[ResolvedInstance]:
        return self.resolve_nodes(self.model.data.get("ORGANIZATION_HIERARCHY", []))

    def sheets(self) -> List[str]:
        return sorted({i.sheet for i in self.resolve()})

    def instances_by_sheet(self, sheet: str, filter_node_path: Optional[str] = None) -> List[ResolvedInstance]:
        insts = [i for i in self.resolve() if i.sheet == sheet]
        if filter_node_path:
            return [i for i in insts if ">".join(i.node_path_names) == filter_node_path]
        return insts

    def bounds_for_sheet(self, sheet: str, filter_node_path: Optional[str] = None) -> Tuple[int, int]:
        insts = self.instances_by_sheet(sheet, filter_node_path)
        max_row = 10
        max_col = 10
        for i in insts:
            max_row = max(max_row, i.row)
            max_col = max(max_col, i.col)
            for off in (i.offsets or {}).values():
                rr = i.row + int(off.get("row", 0))
                cc = i.col + int(off.get("col", 0))
                max_row = max(max_row, rr)
                max_col = max(max_col, cc)
        return max_row + 3, max_col + 3

    def apply_move(self, instance: ResolvedInstance, new_row: int, new_col: Optional[int], prefer_slot_col_override: bool = False) -> None:
        slot = instance.slot_ref
        node = instance.node_ref
        loc = slot.get("location", {}) or {}

        # Row update
        if instance.coord_strategy == "locations":
            if "locations" in slot and instance.coord_index is not None:
                slot["locations"][instance.coord_index]["row"] = int(new_row)
                if new_col is not None:
                    slot["locations"][instance.coord_index]["col"] = int(new_col)
        elif instance.coord_strategy == "rows":
            rows = loc.get("rows", [])
            if instance.coord_index is not None and 0 <= instance.coord_index < len(rows):
                rows[instance.coord_index] = int(new_row)
            if new_col is not None:
                if "col" in loc or prefer_slot_col_override or instance.col_source == "node":
                    loc["col"] = int(new_col)
                else:
                    node.setdefault("location", {})["startCol"] = int(new_col)
            slot["location"] = loc
        elif instance.coord_strategy == "row":
            loc["row"] = int(new_row)
            if new_col is not None:
                if "col" in loc or prefer_slot_col_override or instance.col_source == "node":
                    loc["col"] = int(new_col)
                else:
                    node.setdefault("location", {})["startCol"] = int(new_col)
            slot["location"] = loc
        elif instance.coord_strategy == "range":
            startR = int(loc.get("startRow", instance.row))
            endR = int(loc.get("endRow", instance.row))
            index = int(instance.coord_index or 0)
            desired_start = int(new_row) - index
            delta = desired_start - startR
            loc["startRow"] = startR + delta
            loc["endRow"] = endR + delta
            if new_col is not None:
                if "col" in loc or prefer_slot_col_override or instance.col_source == "node":
                    loc["col"] = int(new_col)
                else:
                    node.setdefault("location", {})["startCol"] = int(new_col)
            slot["location"] = loc

    def detach_blueprint_for_node(self, node: Dict[str, Any]) -> bool:
        bp_name = node.get("useSlotsFrom")
        if not bp_name:
            return False
        slots = (self.model.data.get("SLOT_BLUEPRINTS", {}) or {}).get(bp_name)
        if not slots:
            return False
        node["slots"] = [dict_deepcopy(s) for s in slots]
        node.pop("useSlotsFrom", None)
        return True


class BlueprintPreviewWidget(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self.resolver = ConfigResolver(self.model)
        self.instances: List[ResolvedInstance] = []
        self.anchor_map: Dict[Tuple[int, int], ResolvedInstance] = {}
        self.selected: Optional[ResolvedInstance] = None
        self._build_ui()
        self._connect()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        top = QtWidgets.QHBoxLayout()
        self.bp_combo = QtWidgets.QComboBox()
        self.preview_start_col = QtWidgets.QSpinBox(); self.preview_start_col.setRange(1, 10000); self.preview_start_col.setValue(4)
        self.preview_base_row = QtWidgets.QSpinBox(); self.preview_base_row.setRange(1, 10000); self.preview_base_row.setValue(5)
        self.cellsize = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.cellsize.setRange(16, 64); self.cellsize.setValue(26)
        top.addWidget(QtWidgets.QLabel("Blueprint:"))
        top.addWidget(self.bp_combo, 1)
        top.addWidget(QtWidgets.QLabel("Start Col:"))
        top.addWidget(self.preview_start_col)
        top.addWidget(QtWidgets.QLabel("Cell Size"))
        top.addWidget(self.cellsize)
        layout.addLayout(top)

        body = QtWidgets.QHBoxLayout()
        self.grid = LayoutGrid(60, 40)
        self.grid.enable_anchor_pick(True)
        body.addWidget(self.grid, 3)

        self.inspector = QtWidgets.QGroupBox("Selection")
        form = QtWidgets.QFormLayout(self.inspector)
        self.sel_info = QtWidgets.QLabel("(none)")
        self.sel_row = QtWidgets.QSpinBox(); self.sel_row.setRange(1, 100000)
        self.sel_col = QtWidgets.QSpinBox(); self.sel_col.setRange(1, 100000)
        self.apply_btn = QtWidgets.QPushButton("Apply Move")
        form.addRow("Info", self.sel_info)
        form.addRow("Row", self.sel_row)
        form.addRow("Col", self.sel_col)
        form.addRow(self.apply_btn)
        body.addWidget(self.inspector, 1)

        layout.addLayout(body, 1)

    def _connect(self):
        self.bp_combo.currentTextChanged.connect(self.render)
        self.preview_start_col.valueChanged.connect(self.render)
        self.cellsize.valueChanged.connect(self._apply_zoom)
        self.grid.anchorPicked.connect(self._on_pick)
        self.apply_btn.clicked.connect(self._apply_move)

    def refresh(self):
        self.bp_combo.blockSignals(True)
        self.bp_combo.clear()
        for name in sorted(self.model.data.get("SLOT_BLUEPRINTS", {}).keys()):
            self.bp_combo.addItem(name)
        self.bp_combo.blockSignals(False)
        if self.bp_combo.count() > 0:
            self.bp_combo.setCurrentIndex(0)
        self.render()

    def _apply_zoom(self, v: int):
        for r in range(self.grid.rowCount()):
            self.grid.setRowHeight(r, v)
        for c in range(self.grid.columnCount()):
            self.grid.setColumnWidth(c, v * 2)

    def _make_preview_node(self) -> Dict[str, Any]:
        bp = self.bp_combo.currentText()
        return {"name": "Preview", "sheetName": "Preview Sheet", "location": {"startCol": int(self.preview_start_col.value())}, "useSlotsFrom": bp}

    def render(self):
        if self.bp_combo.count() == 0:
            return
        node = self._make_preview_node()
        self.instances = self.resolver.resolve_nodes([node])
        # Build grid bounds from preview instances only
        max_row, max_col = 10, 10
        for inst in self.instances:
            if inst.sheet != "Preview Sheet":
                continue
            max_row = max(max_row, inst.row)
            max_col = max(max_col, inst.col)
            for off in (inst.offsets or {}).values():
                rr = inst.row + int(off.get("row", 0))
                cc = inst.col + int(off.get("col", 0))
                max_row = max(max_row, rr)
                max_col = max(max_col, cc)
        self.grid.setRowCount(max(max_row, 30))
        self.grid.setColumnCount(max(max_col, 20))
        self._apply_zoom(self.cellsize.value())
        self.grid.clearContents()
        self.anchor_map.clear()
        # Place markers
        for inst in self.instances:
            if inst.sheet != "Preview Sheet":
                continue
            # Anchor
            item = QtWidgets.QTableWidgetItem("A")
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            item.setBackground(QtGui.QBrush(QtGui.QColor("#ffd966")))
            self.grid.setItem(inst.row - 1, inst.col - 1, item)
            self.anchor_map[(inst.row, inst.col)] = inst
            # Fields
            for key, off in (inst.offsets or {}).items():
                rr = inst.row + int(off.get("row", 0))
                cc = inst.col + int(off.get("col", 0))
                if rr <= 0 or cc <= 0:
                    continue
                it = self.grid.item(rr - 1, cc - 1)
                txt = key if it is None else f"{it.text()}\n{key}"
                it2 = QtWidgets.QTableWidgetItem(txt)
                it2.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                it2.setForeground(QtGui.QBrush(QtGui.QColor("#003366")))
                it2.setBackground(QtGui.QBrush(QtGui.QColor("#cce5ff")))
                self.grid.setItem(rr - 1, cc - 1, it2)

    def _on_pick(self, row: int, col: int):
        key = (row + 1, col + 1)
        inst = self.anchor_map.get(key)
        self.selected = inst
        if inst:
            self.sel_info.setText(f"{'>'.join(inst.node_path_names)} | {inst.origin} {inst.origin_name or ''}")
            self.sel_row.setValue(inst.row)
            self.sel_col.setValue(inst.col)
        else:
            self.sel_info.setText("(none)")

    def _apply_move(self):
        if not self.selected:
            return
        self.resolver.apply_move(self.selected, int(self.sel_row.value()), int(self.sel_col.value()), prefer_slot_col_override=True)
        self.render()


class SheetPreviewEditorWidget(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self.resolver = ConfigResolver(self.model)
        self.instances: List[ResolvedInstance] = []
        self.anchor_map: Dict[Tuple[int, int], ResolvedInstance] = {}
        self.selected: Optional[ResolvedInstance] = None
        self._build_ui()
        self._connect()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        top = QtWidgets.QHBoxLayout()
        self.sheet_combo = QtWidgets.QComboBox()
        self.node_filter = QtWidgets.QComboBox()
        self.node_filter.addItem("(All)")
        self.cellsize = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.cellsize.setRange(16, 64); self.cellsize.setValue(24)
        self.show_fields = QtWidgets.QCheckBox("Show field cells")
        self.show_fields.setChecked(True)
        self.pick_new_anchor = QtWidgets.QPushButton("Pick New Anchor")
        self.pick_new_anchor.setCheckable(True)
        self.prefer_slot_col = QtWidgets.QCheckBox("Prefer slot col override on edits")
        top.addWidget(QtWidgets.QLabel("Sheet:"))
        top.addWidget(self.sheet_combo)
        top.addWidget(QtWidgets.QLabel("Section:"))
        top.addWidget(self.node_filter)
        top.addWidget(self.show_fields)
        top.addWidget(QtWidgets.QLabel("Cell Size"))
        top.addWidget(self.cellsize)
        top.addWidget(self.pick_new_anchor)
        top.addWidget(self.prefer_slot_col)
        layout.addLayout(top)

        body = QtWidgets.QHBoxLayout()
        self.grid = LayoutGrid(120, 60)
        body.addWidget(self.grid, 3)

        self.inspector = QtWidgets.QGroupBox("Selection")
        form = QtWidgets.QFormLayout(self.inspector)
        self.sel_info = QtWidgets.QLabel("(none)")
        self.sel_row = QtWidgets.QSpinBox(); self.sel_row.setRange(1, 99999)
        self.sel_col = QtWidgets.QSpinBox(); self.sel_col.setRange(1, 99999)
        self.apply_move_btn = QtWidgets.QPushButton("Apply Move")
        self.detach_btn = QtWidgets.QPushButton("Detach blueprint for this node")
        form.addRow("Info", self.sel_info)
        form.addRow("Row", self.sel_row)
        form.addRow("Col", self.sel_col)
        form.addRow(self.apply_move_btn)
        form.addRow(self.detach_btn)
        body.addWidget(self.inspector, 1)

        layout.addLayout(body, 1)

    def _connect(self):
        self.sheet_combo.currentTextChanged.connect(self._render)
        self.node_filter.currentTextChanged.connect(self._render)
        self.cellsize.valueChanged.connect(self._apply_zoom)
        self.show_fields.toggled.connect(self._render)
        self.pick_new_anchor.toggled.connect(self.grid.enable_anchor_pick)
        self.grid.anchorPicked.connect(self._on_pick)
        self.apply_move_btn.clicked.connect(self._apply_move)
        self.detach_btn.clicked.connect(self._detach_blueprint)

    def refresh(self):
        # Refresh sheets and render
        self.instances = self.resolver.resolve()
        sheets = sorted({i.sheet for i in self.instances})
        self.sheet_combo.blockSignals(True)
        self.sheet_combo.clear()
        for s in sheets:
            self.sheet_combo.addItem(s)
        self.sheet_combo.blockSignals(False)
        if self.sheet_combo.count() > 0:
            self.sheet_combo.setCurrentIndex(0)
        self._render()

    def _apply_zoom(self, v: int):
        for r in range(self.grid.rowCount()):
            self.grid.setRowHeight(r, v)
        for c in range(self.grid.columnCount()):
            self.grid.setColumnWidth(c, v * 2)

    def _current_instances(self) -> List[ResolvedInstance]:
        sheet = self.sheet_combo.currentText()
        if not sheet:
            return []
        filter_path = None if self.node_filter.currentIndex() == 0 else self.node_filter.currentText()
        return self.resolver.instances_by_sheet(sheet, filter_path)

    def _render(self):
        self.grid.clearContents()
        self.anchor_map.clear()
        sheet = self.sheet_combo.currentText()
        if not sheet:
            return
        # Populate node filter
        insts_all = [i for i in self.resolver.instances_by_sheet(sheet)]
        paths = sorted({">".join(i.node_path_names) for i in insts_all})
        self.node_filter.blockSignals(True)
        self.node_filter.clear(); self.node_filter.addItem("(All)")
        for p in paths:
            self.node_filter.addItem(p)
        self.node_filter.blockSignals(False)

        # Bounds
        max_row, max_col = self.resolver.bounds_for_sheet(sheet, None if self.node_filter.currentIndex() == 0 else self.node_filter.currentText())
        self.grid.setRowCount(max(max_row, 40))
        self.grid.setColumnCount(max(max_col, 20))
        self._apply_zoom(self.cellsize.value())

        # Draw
        for inst in self._current_instances():
            # Anchor
            item = QtWidgets.QTableWidgetItem("A")
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            item.setBackground(QtGui.QBrush(QtGui.QColor("#ffd966")))
            self.grid.setItem(inst.row - 1, inst.col - 1, item)
            self.anchor_map[(inst.row, inst.col)] = inst
            # Fields
            if self.show_fields.isChecked():
                for key, off in (inst.offsets or {}).items():
                    rr = inst.row + int(off.get("row", 0))
                    cc = inst.col + int(off.get("col", 0))
                    if rr <= 0 or cc <= 0:
                        continue
                    it = self.grid.item(rr - 1, cc - 1)
                    txt = key if it is None else f"{it.text()}\n{key}"
                    it2 = QtWidgets.QTableWidgetItem(txt)
                    it2.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                    it2.setForeground(QtGui.QBrush(QtGui.QColor("#003366")))
                    it2.setBackground(QtGui.QBrush(QtGui.QColor("#cce5ff")))
                    self.grid.setItem(rr - 1, cc - 1, it2)

    def _on_pick(self, row: int, col: int):
        if self.pick_new_anchor.isChecked() and self.selected is not None:
            # Move selected instance to this row/col
            self.resolver.apply_move(self.selected, row + 1, col + 1, prefer_slot_col_override=self.prefer_slot_col.isChecked())
            self.pick_new_anchor.setChecked(False)
            self.refresh()
            return
        inst = self.anchor_map.get((row + 1, col + 1))
        self.selected = inst
        if inst:
            self.sel_info.setText(f"{'>'.join(inst.node_path_names)} | {inst.origin} {inst.origin_name or ''}")
            self.sel_row.setValue(inst.row)
            self.sel_col.setValue(inst.col)
        else:
            self.sel_info.setText("(none)")

    def _apply_move(self):
        if not self.selected:
            return
        self.resolver.apply_move(self.selected, int(self.sel_row.value()), int(self.sel_col.value()), prefer_slot_col_override=self.prefer_slot_col.isChecked())
        self.refresh()

    def _detach_blueprint(self):
        if not self.selected or self.selected.origin != "blueprint":
            return
        node = self.selected.node_ref
        if self.resolver.detach_blueprint_for_node(node):
            QtWidgets.QMessageBox.information(self, "Detached", "Blueprint was copied into this node's slots and detached.")
            self.refresh()
        else:
            QtWidgets.QMessageBox.warning(self, "Unavailable", "Unable to detach blueprint for this node.")


class PreviewExportWidget(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.validation_label = QtWidgets.QLabel()
        self.validation_label.setWordWrap(True)
        self.tabs = QtWidgets.QTabWidget()
        self.json_view = QtWidgets.QPlainTextEdit(); self.json_view.setReadOnly(True)
        self.js_view = QtWidgets.QPlainTextEdit(); self.js_view.setReadOnly(True)
        self.tabs.addTab(self.json_view, "JSON Preview")
        self.tabs.addTab(self.js_view, "JS Preview")

        btns = QtWidgets.QHBoxLayout()
        self.copy_json_btn = QtWidgets.QPushButton("Copy JSON")
        self.copy_js_btn = QtWidgets.QPushButton("Copy JS")
        self.save_json_btn = QtWidgets.QPushButton("Save JSON...")
        self.save_js_btn = QtWidgets.QPushButton("Save JS...")
        btns.addWidget(self.copy_json_btn)
        btns.addWidget(self.copy_js_btn)
        btns.addStretch(1)
        btns.addWidget(self.save_json_btn)
        btns.addWidget(self.save_js_btn)

        layout.addWidget(self.validation_label)
        layout.addWidget(self.tabs, 1)
        layout.addLayout(btns)

        self.copy_json_btn.clicked.connect(self._copy_json)
        self.copy_js_btn.clicked.connect(self._copy_js)
        self.save_json_btn.clicked.connect(self._save_json)
        self.save_js_btn.clicked.connect(self._save_js)

    def refresh(self):
        errs, warns = self.model.validate()
        if errs:
            txt = "Errors: \n- " + "\n- ".join(errs)
            if warns:
                txt += "\n\nWarnings:\n- " + "\n- ".join(warns)
            self.validation_label.setText(f"<font color='red'>{QtWidgets.QApplication.translate('','')}{txt}</font>")
        elif warns:
            txt = "Warnings:\n- " + "\n- ".join(warns)
            self.validation_label.setText(f"<font color='orange'>{txt}</font>")
        else:
            self.validation_label.setText("<font color='green'>No issues detected.</font>")
        self.json_view.setPlainText(self.model.to_json())
        self.js_view.setPlainText(self.model.to_js())

    def _copy_json(self):
        QtWidgets.QApplication.clipboard().setText(self.model.to_json())
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "JSON copied")

    def _copy_js(self):
        QtWidgets.QApplication.clipboard().setText(self.model.to_js())
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "JS copied")

    def _save_json(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save JSON", "themis_config.json", "JSON (*.json)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.model.to_json())

    def _save_js(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save JS", "themis_config.js", "JavaScript (*.js)")
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.model.to_js())


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("THEMIS Configuration Studio")
        self.resize(1280, 820)
        self.model = ThemisConfigModel.default()
        self._build_ui()
        self._connect()
        self._refresh_all()

    def _build_ui(self):
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)

        self.layout_designer = LayoutDesignerWidget(self.model)
        self.slot_blueprints = SlotBlueprintsWidget(self.model)
        self.blueprint_preview = BlueprintPreviewWidget(self.model)
        self.org_editor = OrganizationEditorWidget(self.model)
        self.sheet_preview = SheetPreviewEditorWidget(self.model)
        self.ranks_settings = RanksSettingsWidget(self.model)
        self.fields_validation = FieldsValidationWidget(self.model)
        self.preview_export = PreviewExportWidget(self.model)

        self.tabs.addTab(self.layout_designer, "Layout Designer")
        self.tabs.addTab(self.slot_blueprints, "Slot Blueprints")
        self.tabs.addTab(self.blueprint_preview, "Blueprint Preview")
        self.tabs.addTab(self.org_editor, "Organization")
        self.tabs.addTab(self.sheet_preview, "Sheet Preview & Editor")
        self.tabs.addTab(self.ranks_settings, "Ranks & Settings")
        self.tabs.addTab(self.fields_validation, "Fields & Validation")
        self.tabs.addTab(self.preview_export, "Preview & Export")

        # Menu
        self._build_menu()
        self.statusBar().showMessage("Ready")

    def _build_menu(self):
        bar = self.menuBar()
        filem = bar.addMenu("File")
        self.new_action = filem.addAction("New")
        self.open_json_action = filem.addAction("Open JSON...")
        self.open_js_action = filem.addAction("Open JS...")
        filem.addSeparator()
        self.save_json_action = filem.addAction("Save JSON...")
        self.save_js_action = filem.addAction("Save JS...")
        filem.addSeparator()
        self.exit_action = filem.addAction("Exit")

        helpm = bar.addMenu("Help")
        self.about_action = helpm.addAction("About")

    def _connect(self):
        self.new_action.triggered.connect(self._new_project)
        self.open_json_action.triggered.connect(self._open_json)
        self.open_js_action.triggered.connect(self._open_js)
        self.save_json_action.triggered.connect(self.preview_export._save_json)
        self.save_js_action.triggered.connect(self.preview_export._save_js)
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self._about)

        # Keep previews up-to-date
        for tab in [
            self.layout_designer,
            self.slot_blueprints,
            self.blueprint_preview,
            self.org_editor,
            self.sheet_preview,
            self.ranks_settings,
            self.fields_validation,
        ]:
            if hasattr(tab, "refresh"):
                # We'll refresh preview on tab change or menu events
                pass
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _refresh_all(self):
        self.layout_designer.refresh()
        self.slot_blueprints.refresh()
        self.blueprint_preview.refresh()
        self.org_editor.refresh()
        self.sheet_preview.refresh()
        self.ranks_settings.refresh()
        self.fields_validation.refresh()
        self.preview_export.refresh()

    def _on_tab_changed(self, idx: int):
        # Update palette for potential new custom fields
        if self.tabs.widget(idx) is self.layout_designer:
            self.layout_designer.palette.refresh()
        # Always refresh the export preview because model may have changed
        self.preview_export.refresh()

    def _new_project(self):
        if QtWidgets.QMessageBox.question(self, "New Project", "Discard current changes and start a new configuration?") != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self.model = ThemisConfigModel.default()
        self._rebind_model()

    def _rebind_model(self):
        # Recreate tabs bound to model to propagate references cleanly
        self.tabs.clear()
        self.layout_designer = LayoutDesignerWidget(self.model)
        self.slot_blueprints = SlotBlueprintsWidget(self.model)
        self.blueprint_preview = BlueprintPreviewWidget(self.model)
        self.org_editor = OrganizationEditorWidget(self.model)
        self.sheet_preview = SheetPreviewEditorWidget(self.model)
        self.ranks_settings = RanksSettingsWidget(self.model)
        self.fields_validation = FieldsValidationWidget(self.model)
        self.preview_export = PreviewExportWidget(self.model)
        self.tabs.addTab(self.layout_designer, "Layout Designer")
        self.tabs.addTab(self.slot_blueprints, "Slot Blueprints")
        self.tabs.addTab(self.blueprint_preview, "Blueprint Preview")
        self.tabs.addTab(self.org_editor, "Organization")
        self.tabs.addTab(self.sheet_preview, "Sheet Preview & Editor")
        self.tabs.addTab(self.ranks_settings, "Ranks & Settings")
        self.tabs.addTab(self.fields_validation, "Fields & Validation")
        self.tabs.addTab(self.preview_export, "Preview & Export")

    def _about(self):
        QtWidgets.QMessageBox.information(
            self,
            "About",
            "THEMIS Configuration Studio\n\n"
            "A visual editor for THEMIS configuration (Layouts, Slots, Organization, Ranks, Fields).\n"
            "Exports JSON and JS compatible with Code.js expectations.\n\n"
            "Drag fields onto the grid in Layout Designer to set offsets relative to an anchor.\n"
            "Use Slot Blueprints to define ranks and locations, and Organization to assemble your hierarchy.",
        )

    def _open_json(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open JSON", "", "JSON (*.json)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Invalid JSON root; expected an object")
            self.model.set_data(data)
            self._rebind_model()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open: {e}")

    def _open_js(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open JS", "", "JavaScript (*.js)")
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            body = sanitize_js_like_to_json(text)
            data = json.loads(body)
            if not isinstance(data, dict):
                raise ValueError("Invalid JS config; not a top-level object")
            self.model.set_data(data)
            self._rebind_model()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open JS: {e}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("THEMIS Configuration Studio")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
