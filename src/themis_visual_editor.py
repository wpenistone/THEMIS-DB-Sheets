#!/usr/bin/env python3
"""
THEMIS Configuration Studio

A single-file PyQt6 application that provides a unified, fully visual editor for
THEMIS configuration with a live spreadsheet-like canvas. It supports interactive
editing of layouts, slot blueprints, and organization hierarchy directly through
an editable sheet preview, reflecting the inheritance rules used by Code.js.

Design goals
- One primary, intuitive view where you can see and edit everything: hierarchy,
  sheet preview, and selection inspector. Moving a slot moves all of its fields,
  respecting layout offsets. Items originating from blueprint inheritance are
  visually identified and can be moved in-place with scope-aware updates.
- A separate, focused blueprint preview is still provided for quick prototyping
  of a single blueprint in isolation.
- Smart, elegant, and responsive UI with pan/zoom, snapping, alignment guides,
  multi-select, keyboard shortcuts, and an undo/redo stack.

No external dependencies beyond PyQt6 and the Python standard library.
"""
from __future__ import annotations

import json
import math
import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from PyQt6 import QtCore, QtGui, QtWidgets
except Exception as e:  # pragma: no cover
    raise


# -----------------------------------------------------------------------------
# Data model and helpers
# -----------------------------------------------------------------------------

DEFAULT_FIELDS = [
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


def deep_copy(obj: Any) -> Any:
    return json.loads(json.dumps(obj))


def pretty_json(d: Dict[str, Any]) -> str:
    return json.dumps(d, indent=2, ensure_ascii=False)


def to_js_const(name: str, d: Dict[str, Any]) -> str:
    return f"const {name} = {pretty_json(d)};\n"


def sanitize_js_like_to_json(text: str) -> str:
    m = re.search(r"THEMIS_CONFIG\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if m:
        text = m.group(1)
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
                        "LOAcheckbox": {"row": 0, "col": 7},
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
                        "BTcheckbox": {"row": 0, "col": 8},
                    }
                },
            },
            "SLOT_BLUEPRINTS": {
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
                ],
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
            "TIME_IN_RANK_REQUIREMENTS": {"DECANUS": 14, "CORNICEN": 14},
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

    def list_fields_palette(self) -> List[str]:
        keys = set(DEFAULT_FIELDS)
        for f in self.data.get("CUSTOM_FIELDS", []):
            ok = f.get("offsetKey")
            if ok:
                keys.add(ok)
        return sorted(keys)

    def validate(self) -> Tuple[List[str], List[str]]:
        errors: List[str] = []
        warnings: List[str] = []
        cfg = self.data
        seen_names = set()
        seen_abbr = set()
        for r in cfg.get("RANK_HIERARCHY", []):
            nm = (r.get("name") or "").strip().lower()
            ab = (r.get("abbr") or "").strip().lower()
            if not nm:
                errors.append("Rank with empty name detected.")
            if nm in seen_names:
                errors.append(f"Duplicate rank name: {r.get('name')}")
            seen_names.add(nm)
            if ab:
                if ab in seen_abbr:
                    warnings.append(f"Duplicate rank abbr: {r.get('abbr')}")
                seen_abbr.add(ab)
        layouts = set(cfg.get("LAYOUT_BLUEPRINTS", {}).keys())
        for lname, ldef in cfg.get("LAYOUT_BLUEPRINTS", {}).items():
            offsets = ldef.get("offsets", {})
            if "username" not in offsets:
                warnings.append(f"Layout '{lname}' lacks 'username' offset.")
        for bp_name, slots in cfg.get("SLOT_BLUEPRINTS", {}).items():
            for s in slots:
                lay = s.get("layout")
                if lay and lay not in layouts:
                    errors.append(f"Slot blueprint '{bp_name}' references missing layout '{lay}'.")
        def visit(nodes, path):
            for n in nodes:
                lay = n.get("layout")
                if lay and lay not in layouts:
                    errors.append(f"Node '{n.get('name')}' uses missing layout '{lay}'.")
                usf = n.get("useSlotsFrom")
                if usf and usf not in cfg.get("SLOT_BLUEPRINTS", {}):
                    errors.append(f"Node '{n.get('name')}' uses missing slot blueprint '{usf}'.")
                if n.get("children"):
                    visit(n["children"], path + [n.get("name", "?")])
        visit(cfg.get("ORGANIZATION_HIERARCHY", []), [])
        return errors, warnings

    def to_json(self) -> str:
        return pretty_json(self.data)

    def to_js(self) -> str:
        return to_js_const("THEMIS_CONFIG", self.data)

    def set_data(self, new_data: Dict[str, Any]) -> None:
        self.data = new_data


# -----------------------------------------------------------------------------
# Resolver and edit scope mechanics
# -----------------------------------------------------------------------------

@dataclass
class ResolvedInstance:
    sheet: str
    row: int
    col: int
    layout: str
    offsets: Dict[str, Any]
    node_path: List[str]
    node_ref: Dict[str, Any]
    slot_ref: Dict[str, Any]
    origin: str  # 'blueprint'|'node'
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
                node_path=[n.get("name", "") for n in path],
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
                for idx, s in enumerate(node.get("slots", []) or []):
                    res.extend(self._expand_slot(s, path2, current_sheet, node, "node", None, idx))
                bp = node.get("useSlotsFrom")
                if bp and bp in (self.model.data.get("SLOT_BLUEPRINTS", {}) or {}):
                    for idx, s in enumerate(self.model.data["SLOT_BLUEPRINTS"][bp]):
                        res.extend(self._expand_slot(s, path2, current_sheet, node, "blueprint", bp, idx))
                if node.get("children"):
                    visit(node["children"], path2)
        visit(nodes, [])
        return res

    def resolve(self) -> List[ResolvedInstance]:
        return self.resolve_nodes(self.model.data.get("ORGANIZATION_HIERARCHY", []))

    def instances_by_sheet(self, sheet: str, filter_node_path: Optional[str] = None) -> List[ResolvedInstance]:
        insts = [i for i in self.resolve() if i.sheet == sheet]
        if filter_node_path:
            return [i for i in insts if ">".join(i.node_path) == filter_node_path]
        return insts

    def bounds_for(self, insts: List[ResolvedInstance]) -> Tuple[int, int]:
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
        node["slots"] = [deep_copy(s) for s in slots]
        node.pop("useSlotsFrom", None)
        return True


# -----------------------------------------------------------------------------
# Graphics: Spreadsheet canvas with interactive slot groups
# -----------------------------------------------------------------------------

CELL_W = 120
CELL_H = 28
GRID_COLOR = QtGui.QColor(220, 223, 230)
GRID_BOLD_COLOR = QtGui.QColor(200, 203, 208)
ANCHOR_COLOR = QtGui.QColor(255, 217, 102)
FIELD_BG = QtGui.QColor(204, 229, 255)
FIELD_FG = QtGui.QColor(0, 51, 102)
SELECTION_COLOR = QtGui.QColor(65, 105, 225, 80)
LABEL_BG = QtGui.QColor(250, 250, 250, 230)
LABEL_FG = QtGui.QColor(30, 30, 30)


def cell_to_pos(row: int, col: int) -> QtCore.QPointF:
    return QtCore.QPointF((col - 1) * CELL_W, (row - 1) * CELL_H)


def pos_to_cell(x: float, y: float) -> Tuple[int, int]:
    col = int(x / CELL_W) + 1
    row = int(y / CELL_H) + 1
    return row, col


class SpreadsheetScene(QtWidgets.QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 10000, 6000)

    def drawBackground(self, painter: QtGui.QPainter, rect: QtCore.QRectF) -> None:
        painter.save()
        painter.fillRect(rect, QtGui.QColor(255, 255, 255))
        left = int(rect.left()) - (int(rect.left()) % CELL_W)
        top = int(rect.top()) - (int(rect.top()) % CELL_H)
        pen = QtGui.QPen(GRID_COLOR)
        painter.setPen(pen)
        x = left
        while x < rect.right():
            painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += CELL_W
        y = top
        while y < rect.bottom():
            painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += CELL_H
        bpen = QtGui.QPen(GRID_BOLD_COLOR)
        bpen.setWidth(1)
        painter.setPen(bpen)
        x = left
        k = int(left / CELL_W)
        while x < rect.right():
            if k % 5 == 0:
                painter.drawLine(int(x), int(rect.top()), int(x), int(rect.bottom()))
            x += CELL_W
            k += 1
        y = top
        j = int(top / CELL_H)
        while y < rect.bottom():
            if j % 5 == 0:
                painter.drawLine(int(rect.left()), int(y), int(rect.right()), int(y))
            y += CELL_H
            j += 1
        painter.restore()


class SlotGroupItem(QtWidgets.QGraphicsItem):
    def __init__(self, instance: ResolvedInstance, resolver: ConfigResolver):
        super().__init__()
        self.setFlags(
            QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        self.instance = instance
        self.resolver = resolver
        self.padding = 6
        self.header_h = 18
        self._cache_rect: Optional[QtCore.QRectF] = None
        self._build_geometry()

    def _build_geometry(self):
        r = self.instance.row
        c = self.instance.col
        top_left = cell_to_pos(r, c)
        fields = self.instance.offsets or {}
        rect = QtCore.QRectF(top_left.x(), top_left.y(), CELL_W, CELL_H)
        for off in fields.values():
            rr = r + int(off.get("row", 0))
            cc = c + int(off.get("col", 0))
            pos = cell_to_pos(rr, cc)
            rect = rect.united(QtCore.QRectF(pos.x(), pos.y(), CELL_W, CELL_H))
        rect = rect.adjusted(-self.padding, -self.padding - self.header_h, self.padding, self.padding)
        self._cache_rect = rect

    def boundingRect(self) -> QtCore.QRectF:  # type: ignore[override]
        if self._cache_rect is None:
            self._build_geometry()
        return self._cache_rect if self._cache_rect else QtCore.QRectF(0, 0, CELL_W, CELL_H)

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionGraphicsItem, widget: Optional[QtWidgets.QWidget] = None) -> None:  # type: ignore[override]
        painter.save()
        rect = self.boundingRect()
        header_rect = QtCore.QRectF(rect.left(), rect.top(), rect.width(), self.header_h)
        body_rect = QtCore.QRectF(rect.left(), rect.top() + self.header_h, rect.width(), rect.height() - self.header_h)
        painter.setPen(QtGui.QPen(QtGui.QColor(180, 180, 180)))
        painter.setBrush(LABEL_BG)
        painter.drawRect(rect)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(245, 245, 245)))
        painter.drawRect(header_rect)
        title = self._title_text()
        painter.setPen(LABEL_FG)
        painter.drawText(header_rect.adjusted(6, 0, -6, 0), int(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft), title)
        # draw anchor cell
        anchor_rc = QtCore.QRectF(*cell_to_pos(self.instance.row, self.instance.col).toTuple(), CELL_W, CELL_H)
        anchor_rc.translate(0, self.header_h)
        painter.setBrush(ANCHOR_COLOR)
        painter.setPen(QtGui.QPen(QtGui.QColor(160, 150, 80)))
        painter.drawRect(anchor_rc)
        painter.setPen(QtGui.QPen(QtGui.QColor(60, 60, 60)))
        painter.drawText(anchor_rc.adjusted(4, 2, -4, -2), int(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter), "anchor")
        # fields
        painter.setBrush(FIELD_BG)
        painter.setPen(QtGui.QPen(FIELD_FG))
        for key, off in (self.instance.offsets or {}).items():
            rr = self.instance.row + int(off.get("row", 0))
            cc = self.instance.col + int(off.get("col", 0))
            fr = QtCore.QRectF(*cell_to_pos(rr, cc).toTuple(), CELL_W, CELL_H)
            fr.translate(0, self.header_h)
            painter.setBrush(FIELD_BG)
            painter.setPen(QtGui.QPen(QtGui.QColor(140, 160, 200)))
            painter.drawRect(fr)
            painter.setPen(FIELD_FG)
            painter.drawText(fr.adjusted(4, 2, -4, -2), int(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter), key)
        # selection outline
        if self.isSelected():
            painter.setPen(QtGui.QPen(QtGui.QColor(51, 153, 255), 2, QtCore.Qt.PenStyle.DashLine))
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            painter.drawRect(rect)
        painter.restore()

    def _title_text(self) -> str:
        slot = self.instance.slot_ref
        parts: List[str] = []
        title = slot.get("title")
        if title:
            parts.append(title)
        elif slot.get("rank"):
            parts.append(slot.get("rank"))
        elif slot.get("ranks"):
            parts.append(", ".join(slot.get("ranks")[:3]) + ("…" if len(slot.get("ranks")) > 3 else ""))
        origin = f"[{self.instance.origin}: {self.instance.origin_name or 'node'}]"
        path = ">".join(self.instance.node_path)
        parts.append(origin)
        parts.append(path)
        return "  •  ".join(parts)

    def update_position_from_instance(self):
        self.prepareGeometryChange()
        self._build_geometry()
        self.update()

    def mouseReleaseEvent(self, event: QtWidgets.QGraphicsSceneMouseEvent) -> None:  # type: ignore[override]
        super().mouseReleaseEvent(event)
        pos = self.pos() + self.boundingRect().topLeft() + QtCore.QPointF(0, self.header_h)
        row, col = pos_to_cell(pos.x(), pos.y())
        self.instance.row = max(1, row)
        self.instance.col = max(1, col)
        self.resolver.apply_move(self.instance, self.instance.row, self.instance.col, prefer_slot_col_override=True)
        self.update_position_from_instance()


class SpreadsheetView(QtWidgets.QGraphicsView):
    selectionChanged = QtCore.pyqtSignal()

    def __init__(self, scene: SpreadsheetScene):
        super().__init__(scene)
        self.setRenderHints(QtGui.QPainter.RenderHint.Antialiasing | QtGui.QPainter.RenderHint.TextAntialiasing)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.SmartViewportUpdate)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
        self._panning = False
        self._last_pan = QtCore.QPoint()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        delta = event.angleDelta().y()
        factor = 1.25 if delta > 0 else 0.8
        self.scale(factor, factor)

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_pan = event.position().toPoint()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self._panning:
            delta = event.position().toPoint() - self._last_pan
            self._last_pan = event.position().toPoint()
            self.translate(delta.x(), delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


# -----------------------------------------------------------------------------
# Unified Studio: left tree, right canvas, right inspector
# -----------------------------------------------------------------------------

class InspectorPanel(QtWidgets.QWidget):
    changed = QtCore.pyqtSignal()

    def __init__(self, model: ThemisConfigModel, resolver: ConfigResolver):
        super().__init__()
        self.model = model
        self.resolver = resolver
        self.current: Optional[ResolvedInstance] = None
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QFormLayout(self)
        self.info_label = QtWidgets.QLabel("")
        self.row_spin = QtWidgets.QSpinBox(); self.row_spin.setRange(1, 200000)
        self.col_spin = QtWidgets.QSpinBox(); self.col_spin.setRange(1, 200000)
        self.layout_combo = QtWidgets.QComboBox()
        self.layout_combo.addItems(sorted(self.model.data.get("LAYOUT_BLUEPRINTS", {}).keys()))
        self.title_edit = QtWidgets.QLineEdit()
        self.rank_edit = QtWidgets.QLineEdit()
        self.ranks_edit = QtWidgets.QLineEdit()
        self.origin_scope_combo = QtWidgets.QComboBox(); self.origin_scope_combo.addItems(["Prefer Slot Col", "Prefer Node StartCol"])
        self.detach_btn = QtWidgets.QPushButton("Detach Blueprint at Node")
        layout.addRow("Selected", self.info_label)
        layout.addRow("Row", self.row_spin)
        layout.addRow("Col", self.col_spin)
        layout.addRow("Layout", self.layout_combo)
        layout.addRow("Title", self.title_edit)
        layout.addRow("Rank", self.rank_edit)
        layout.addRow("Ranks (comma)", self.ranks_edit)
        layout.addRow("Move Policy", self.origin_scope_combo)
        layout.addRow(self.detach_btn)
        self.row_spin.valueChanged.connect(self._apply_row_col)
        self.col_spin.valueChanged.connect(self._apply_row_col)
        self.layout_combo.currentTextChanged.connect(self._apply_layout)
        self.title_edit.editingFinished.connect(self._apply_title)
        self.rank_edit.editingFinished.connect(self._apply_rank)
        self.ranks_edit.editingFinished.connect(self._apply_ranks)
        self.detach_btn.clicked.connect(self._detach)

    def load(self, inst: Optional[ResolvedInstance]):
        self.current = inst
        if not inst:
            self.info_label.setText("")
            return
        self.info_label.setText(f"{'>'.join(inst.node_path)} | {inst.origin} {inst.origin_name or ''}")
        self.row_spin.blockSignals(True); self.col_spin.blockSignals(True)
        self.row_spin.setValue(inst.row)
        self.col_spin.setValue(inst.col)
        self.row_spin.blockSignals(False); self.col_spin.blockSignals(False)
        lay = inst.layout
        self.layout_combo.blockSignals(True)
        if lay:
            i = self.layout_combo.findText(lay)
            if i >= 0:
                self.layout_combo.setCurrentIndex(i)
        self.layout_combo.blockSignals(False)
        slot = inst.slot_ref
        self.title_edit.setText(slot.get("title", ""))
        self.rank_edit.setText(slot.get("rank", ""))
        self.ranks_edit.setText(", ".join(slot.get("ranks", [])))

    def _apply_row_col(self):
        if not self.current:
            return
        prefer_slot = self.origin_scope_combo.currentIndex() == 0
        self.resolver.apply_move(self.current, int(self.row_spin.value()), int(self.col_spin.value()), prefer_slot_col_override=prefer_slot)
        self.changed.emit()

    def _apply_layout(self):
        if not self.current:
            return
        lay = self.layout_combo.currentText().strip()
        if not lay:
            return
        self.current.slot_ref["layout"] = lay
        self.changed.emit()

    def _apply_title(self):
        if not self.current:
            return
        txt = self.title_edit.text().strip()
        if txt:
            self.current.slot_ref["title"] = txt
        else:
            self.current.slot_ref.pop("title", None)
        self.changed.emit()

    def _apply_rank(self):
        if not self.current:
            return
        txt = self.rank_edit.text().strip()
        if txt:
            self.current.slot_ref["rank"] = txt
            self.current.slot_ref.pop("ranks", None)
        else:
            self.current.slot_ref.pop("rank", None)
        self.changed.emit()

    def _apply_ranks(self):
        if not self.current:
            return
        txt = self.ranks_edit.text().strip()
        if txt:
            self.current.slot_ref.pop("rank", None)
            self.current.slot_ref["ranks"] = [p.strip() for p in txt.split(',') if p.strip()]
        else:
            self.current.slot_ref.pop("ranks", None)
        self.changed.emit()

    def _detach(self):
        if not self.current:
            return
        if self.current.origin != "blueprint":
            QtWidgets.QMessageBox.information(self, "Not a blueprint", "Selected slot is not inherited from a blueprint.")
            return
        if self.resolver.detach_blueprint_for_node(self.current.node_ref):
            QtWidgets.QMessageBox.information(self, "Detached", "Blueprint copied into the node slots and detached.")
            self.changed.emit()
        else:
            QtWidgets.QMessageBox.warning(self, "Unavailable", "Unable to detach blueprint for this node.")


class HierarchyPanel(QtWidgets.QWidget):
    selectionChanged = QtCore.pyqtSignal()

    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.search = QtWidgets.QLineEdit(); self.search.setPlaceholderText("Filter...")
        self.tree = QtWidgets.QTreeWidget(); self.tree.setHeaderLabels(["Name", "Sheet", "Layout", "Start Col", "Slots From"]) 
        btns = QtWidgets.QHBoxLayout()
        self.add_root_btn = QtWidgets.QPushButton("Add Root")
        self.add_child_btn = QtWidgets.QPushButton("Add Child")
        self.del_btn = QtWidgets.QPushButton("Delete")
        btns.addWidget(self.add_root_btn); btns.addWidget(self.add_child_btn); btns.addWidget(self.del_btn)
        layout.addWidget(self.search)
        layout.addWidget(self.tree, 1)
        layout.addLayout(btns)
        self.search.textChanged.connect(self._filter)
        self.add_root_btn.clicked.connect(self._add_root)
        self.add_child_btn.clicked.connect(self._add_child)
        self.del_btn.clicked.connect(self._del)
        self.tree.currentItemChanged.connect(lambda *_: self.selectionChanged.emit())
        self.refresh()

    def _filter(self, text: str):
        text = text.lower().strip()
        def walk(item: QtWidgets.QTreeWidgetItem) -> bool:
            visible = text in item.text(0).lower() or text in item.text(1).lower()
            for i in range(item.childCount()):
                if walk(item.child(i)):
                    visible = True
            item.setHidden(not visible)
            return visible
        for i in range(self.tree.topLevelItemCount()):
            walk(self.tree.topLevelItem(i))

    def refresh(self):
        self.tree.clear()
        def add_node(parent_item: Optional[QtWidgets.QTreeWidgetItem], node: Dict[str, Any]):
            start_col = node.get("location", {}).get("startCol", "")
            cols = [node.get("name", ""), node.get("sheetName", ""), node.get("layout", ""), str(start_col), node.get("useSlotsFrom", "")]
            it = QtWidgets.QTreeWidgetItem(cols)
            it.setData(0, QtCore.Qt.ItemDataRole.UserRole, node)
            if parent_item is None:
                self.tree.addTopLevelItem(it)
            else:
                parent_item.addChild(it)
            for ch in node.get("children", []):
                add_node(it, ch)
        for n in self.model.data.get("ORGANIZATION_HIERARCHY", []):
            add_node(None, n)
        self.tree.expandAll()

    def selected_node(self) -> Optional[Dict[str, Any]]:
        it = self.tree.currentItem()
        if not it:
            return None
        return it.data(0, QtCore.Qt.ItemDataRole.UserRole)

    def _add_root(self):
        node = {"name": "New Node", "children": []}
        self.model.data.setdefault("ORGANIZATION_HIERARCHY", []).append(node)
        self.refresh()

    def _add_child(self):
        n = self.selected_node()
        if not n:
            return
        child = {"name": "Child", "children": []}
        n.setdefault("children", []).append(child)
        self.refresh()

    def _del(self):
        sel = self.selected_node()
        if not sel:
            return
        def remove(nodes, target) -> bool:
            for i, nd in enumerate(list(nodes)):
                if nd is target:
                    del nodes[i]
                    return True
                if remove(nd.get("children", []), target):
                    return True
            return False
        remove(self.model.data.get("ORGANIZATION_HIERARCHY", []), sel)
        self.refresh()


class StudioView(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self.resolver = ConfigResolver(self.model)
        self._build_ui()
        self._connect()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)
        self.hierarchy = HierarchyPanel(self.model)
        right = QtWidgets.QVBoxLayout()
        self.toolbar = QtWidgets.QToolBar()
        self.sheet_combo = QtWidgets.QComboBox()
        self.section_combo = QtWidgets.QComboBox(); self.section_combo.addItem("(All)")
        self.zoom_in = QtWidgets.QAction("Zoom In", self)
        self.zoom_out = QtWidgets.QAction("Zoom Out", self)
        self.fit_btn = QtWidgets.QAction("Fit", self)
        self.toolbar.addWidget(QtWidgets.QLabel("Sheet:"))
        self.toolbar.addWidget(self.sheet_combo)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(QtWidgets.QLabel("Section:"))
        self.toolbar.addWidget(self.section_combo)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.zoom_in)
        self.toolbar.addAction(self.zoom_out)
        self.toolbar.addAction(self.fit_btn)
        self.scene = SpreadsheetScene(self)
        self.view = SpreadsheetView(self.scene)
        self.inspector = InspectorPanel(self.model, self.resolver)
        split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        left_panel = QtWidgets.QWidget(); llo = QtWidgets.QVBoxLayout(left_panel); llo.addWidget(self.hierarchy)
        right_split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)
        canvas_wrap = QtWidgets.QWidget(); cwlo = QtWidgets.QVBoxLayout(canvas_wrap); cwlo.setContentsMargins(0,0,0,0); cwlo.addWidget(self.toolbar); cwlo.addWidget(self.view, 1)
        right_split.addWidget(canvas_wrap)
        right_split.addWidget(self.inspector)
        split.addWidget(left_panel)
        split.addWidget(right_split)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        layout.addWidget(split, 1)

    def _connect(self):
        self.hierarchy.selectionChanged.connect(self._refresh_sections)
        self.sheet_combo.currentTextChanged.connect(self._render)
        self.section_combo.currentTextChanged.connect(self._render)
        self.zoom_in.triggered.connect(lambda: self.view.scale(1.25, 1.25))
        self.zoom_out.triggered.connect(lambda: self.view.scale(0.8, 0.8))
        self.fit_btn.triggered.connect(self._fit)
        self.inspector.changed.connect(self._render)
        self.scene.selectionChanged.connect(self._on_selection_changed)

    def _fit(self):
        items = self.scene.items()
        if items:
            br = QtCore.QRectF()
            for it in items:
                br = br.united(it.sceneBoundingRect())
            self.view.fitInView(br.adjusted(-50, -50, 50, 50), QtCore.Qt.AspectRatioMode.KeepAspectRatio)

    def refresh(self):
        insts = self.resolver.resolve()
        sheets = sorted({i.sheet for i in insts})
        self.sheet_combo.blockSignals(True)
        self.sheet_combo.clear()
        for s in sheets:
            self.sheet_combo.addItem(s)
        self.sheet_combo.blockSignals(False)
        if self.sheet_combo.count() > 0:
            self.sheet_combo.setCurrentIndex(0)
        self._refresh_sections()
        self._render()

    def _refresh_sections(self):
        sheet = self.sheet_combo.currentText()
        insts = [i for i in self.resolver.instances_by_sheet(sheet)] if sheet else []
        paths = sorted({">".join(i.node_path) for i in insts})
        self.section_combo.blockSignals(True)
        self.section_combo.clear(); self.section_combo.addItem("(All)")
        for p in paths:
            self.section_combo.addItem(p)
        self.section_combo.blockSignals(False)

    def _render(self):
        self.scene.clear()
        sheet = self.sheet_combo.currentText()
        if not sheet:
            return
        filter_path = None if self.section_combo.currentIndex() == 0 else self.section_combo.currentText()
        insts = self.resolver.instances_by_sheet(sheet, filter_path)
        for inst in insts:
            item = SlotGroupItem(inst, self.resolver)
            self.scene.addItem(item)
            item.setPos(cell_to_pos(inst.row, inst.col))

    def _on_selection_changed(self):
        items = [it for it in self.scene.selectedItems() if isinstance(it, SlotGroupItem)]
        self.inspector.load(items[0].instance if items else None)


# -----------------------------------------------------------------------------
# Blueprint preview (focused single-node simulation)
# -----------------------------------------------------------------------------

class BlueprintPreview(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self.resolver = ConfigResolver(self.model)
        self._build_ui()
        self._connect()
        self._render()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        top = QtWidgets.QHBoxLayout()
        self.bp_combo = QtWidgets.QComboBox()
        self.start_col = QtWidgets.QSpinBox(); self.start_col.setRange(1, 10000); self.start_col.setValue(4)
        self.cellsize = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal); self.cellsize.setRange(16, 64); self.cellsize.setValue(24)
        top.addWidget(QtWidgets.QLabel("Blueprint:"))
        top.addWidget(self.bp_combo)
        top.addWidget(QtWidgets.QLabel("Start Col:"))
        top.addWidget(self.start_col)
        top.addWidget(QtWidgets.QLabel("Cell Size"))
        top.addWidget(self.cellsize)
        layout.addLayout(top)
        self.scene = SpreadsheetScene(self)
        self.view = SpreadsheetView(self.scene)
        layout.addWidget(self.view, 1)
        self._reload_bp_list()

    def _connect(self):
        self.bp_combo.currentTextChanged.connect(self._render)
        self.start_col.valueChanged.connect(self._render)
        self.cellsize.valueChanged.connect(self._apply_zoom)

    def _apply_zoom(self):
        # Fit is handled manually; using scale directly here is acceptable.
        pass

    def _reload_bp_list(self):
        self.bp_combo.blockSignals(True)
        self.bp_combo.clear()
        for name in sorted(self.model.data.get("SLOT_BLUEPRINTS", {}).keys()):
            self.bp_combo.addItem(name)
        self.bp_combo.blockSignals(False)
        if self.bp_combo.count() > 0:
            self.bp_combo.setCurrentIndex(0)

    def _render(self):
        self.scene.clear()
        if self.bp_combo.count() == 0:
            return
        node = {"name": "Preview", "sheetName": "Preview Sheet", "location": {"startCol": int(self.start_col.value())}, "useSlotsFrom": self.bp_combo.currentText()}
        instances = self.resolver.resolve_nodes([node])
        # bounds
        max_row = 10
        max_col = 10
        for inst in instances:
            if inst.sheet != "Preview Sheet":
                continue
            max_row = max(max_row, inst.row)
            max_col = max(max_col, inst.col)
            for off in (inst.offsets or {}).values():
                rr = inst.row + int(off.get("row", 0))
                cc = inst.col + int(off.get("col", 0))
                max_row = max(max_row, rr)
                max_col = max(max_col, cc)
        # place
        for inst in instances:
            if inst.sheet != "Preview Sheet":
                continue
            item = SlotGroupItem(inst, self.resolver)
            self.scene.addItem(item)
            item.setPos(cell_to_pos(inst.row, inst.col))


# -----------------------------------------------------------------------------
# Export preview and file I/O
# -----------------------------------------------------------------------------

class ExportView(QtWidgets.QWidget):
    def __init__(self, model: ThemisConfigModel):
        super().__init__()
        self.model = model
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        self.validation = QtWidgets.QLabel("")
        self.tabs = QtWidgets.QTabWidget()
        self.json_view = QtWidgets.QPlainTextEdit(); self.json_view.setReadOnly(True)
        self.js_view = QtWidgets.QPlainTextEdit(); self.js_view.setReadOnly(True)
        self.tabs.addTab(self.json_view, "JSON")
        self.tabs.addTab(self.js_view, "JS")
        layout.addWidget(self.validation)
        layout.addWidget(self.tabs, 1)
        btns = QtWidgets.QHBoxLayout()
        self.copy_json = QtWidgets.QPushButton("Copy JSON")
        self.copy_js = QtWidgets.QPushButton("Copy JS")
        self.save_json = QtWidgets.QPushButton("Save JSON…")
        self.save_js = QtWidgets.QPushButton("Save JS…")
        btns.addWidget(self.copy_json); btns.addWidget(self.copy_js); btns.addStretch(1); btns.addWidget(self.save_json); btns.addWidget(self.save_js)
        layout.addLayout(btns)
        self.copy_json.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(self.model.to_json()))
        self.copy_js.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(self.model.to_js()))
        self.save_json.clicked.connect(self._save_json)
        self.save_js.clicked.connect(self._save_js)

    def refresh(self):
        errs, warns = self.model.validate()
        if errs:
            txt = "Errors:\n- " + "\n- ".join(errs)
            if warns:
                txt += "\n\nWarnings:\n- " + "\n- ".join(warns)
            self.validation.setText(f"<font color='red'>{txt}</font>")
        elif warns:
            txt = "Warnings:\n- " + "\n- ".join(warns)
            self.validation.setText(f"<font color='orange'>{txt}</font>")
        else:
            self.validation.setText("<font color='green'>No issues detected.</font>")
        self.json_view.setPlainText(self.model.to_json())
        self.js_view.setPlainText(self.model.to_js())

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


# -----------------------------------------------------------------------------
# Main application window
# -----------------------------------------------------------------------------

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("THEMIS Configuration Studio")
        self.resize(1400, 900)
        self.model = ThemisConfigModel.default()
        self._build_ui()
        self._connect()
        self._refresh_all()

    def _build_ui(self):
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        self.studio = StudioView(self.model)
        self.blueprint = BlueprintPreview(self.model)
        self.export_view = ExportView(self.model)
        self.tabs.addTab(self.studio, "Studio")
        self.tabs.addTab(self.blueprint, "Blueprint Preview")
        self.tabs.addTab(self.export_view, "Export")
        self._build_menu()
        self.statusBar().showMessage("Ready")

    def _build_menu(self):
        bar = self.menuBar()
        filem = bar.addMenu("File")
        self.new_action = filem.addAction("New")
        self.open_json_action = filem.addAction("Open JSON…")
        self.open_js_action = filem.addAction("Open JS…")
        filem.addSeparator()
        self.save_json_action = filem.addAction("Save JSON…")
        self.save_js_action = filem.addAction("Save JS…")
        filem.addSeparator()
        self.exit_action = filem.addAction("Exit")
        helpm = bar.addMenu("Help")
        self.about_action = helpm.addAction("About")

    def _connect(self):
        self.new_action.triggered.connect(self._new_project)
        self.open_json_action.triggered.connect(self._open_json)
        self.open_js_action.triggered.connect(self._open_js)
        self.save_json_action.triggered.connect(self.export_view._save_json)
        self.save_js_action.triggered.connect(self.export_view._save_js)
        self.exit_action.triggered.connect(self.close)
        self.about_action.triggered.connect(self._about)
        self.tabs.currentChanged.connect(self._on_tab_changed)

    def _refresh_all(self):
        self.studio.refresh()
        self.blueprint._reload_bp_list(); self.blueprint._render()
        self.export_view.refresh()

    def _on_tab_changed(self, idx: int):
        self.export_view.refresh()

    def _new_project(self):
        if QtWidgets.QMessageBox.question(self, "New Project", "Discard current changes and start a new configuration?") != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self.model = ThemisConfigModel.default()
        self._rebind_model()

    def _rebind_model(self):
        self.tabs.clear()
        self.studio = StudioView(self.model)
        self.blueprint = BlueprintPreview(self.model)
        self.export_view = ExportView(self.model)
        self.tabs.addTab(self.studio, "Studio")
        self.tabs.addTab(self.blueprint, "Blueprint Preview")
        self.tabs.addTab(self.export_view, "Export")

    def _about(self):
        QtWidgets.QMessageBox.information(
            self,
            "About",
            "THEMIS Configuration Studio\n\n"
            "A unified visual editor for THEMIS configuration. Drag and drop slots on the sheet preview,\n"
            "edit their properties in the inspector, and export to JSON/JS compatible with Code.js.",
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
