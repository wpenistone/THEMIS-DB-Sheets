from __future__ import annotations

import re
from typing import Any, Dict, List, Set, Tuple


class ValidationIssue:
    def __init__(self, level: str, message: str, path: str) -> None:
        self.level = level
        self.message = message
        self.path = path

    def to_dict(self) -> Dict[str, str]:
        return {"level": self.level, "message": self.message, "path": self.path}


def _walk_org(node: Dict[str, Any], parent_names: Set[str], path: str, issues: List[ValidationIssue]) -> None:
    name = node.get("name", "")
    sheet = node.get("sheetName", "")
    if not name:
        issues.append(ValidationIssue("error", "Organization node missing name", path + ".name"))
    if not sheet:
        issues.append(ValidationIssue("warning", "Organization node missing sheetName", path + ".sheetName"))
    if name in parent_names:
        issues.append(ValidationIssue("error", "Circular reference detected in organization tree", path))
    new_set = set(parent_names)
    new_set.add(name)
    for i, child in enumerate(node.get("children", [])):
        _walk_org(child, new_set, f"{path}.children[{i}]", issues)


def validate_org_hierarchy(org: Dict[str, Any]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    _walk_org(org, set(), "ORGANIZATION_HIERARCHY[0]", issues)
    # Check duplicate sheet names
    def collect_sheets(n: Dict[str, Any], sheets: List[str]) -> None:
        sheets.append(str(n.get("sheetName", "")))
        for c in n.get("children", []):
            collect_sheets(c, sheets)
    sheets: List[str] = []
    collect_sheets(org, sheets)
    seen: Set[str] = set()
    for i, s in enumerate(sheets):
        if not s:
            continue
        if s in seen:
            issues.append(ValidationIssue("warning", f"Duplicate sheetName: {s}", f"ORGANIZATION_HIERARCHY[...].sheetName"))
        seen.add(s)
    return issues


def validate_layout_fields(fields: List[Dict[str, Any]]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    seen_keys: Set[str] = set()
    grid: Set[Tuple[int, int]] = set()
    for i, f in enumerate(fields):
        key = f.get("key", "")
        label = f.get("label", "")
        row = int(f.get("row", 0))
        col = int(f.get("col", 0))
        if not key:
            issues.append(ValidationIssue("error", "Field missing key", f"fields[{i}].key"))
        if not label:
            issues.append(ValidationIssue("warning", "Field missing label", f"fields[{i}].label"))
        if key in seen_keys:
            issues.append(ValidationIssue("error", f"Duplicate field key: {key}", f"fields[{i}].key"))
        else:
            seen_keys.add(key)
        if row < 0 or col < 0:
            issues.append(ValidationIssue("error", "Row/Col cannot be negative", f"fields[{i}]"))
        cell = (row, col)
        if cell in grid:
            issues.append(ValidationIssue("warning", f"Multiple fields share cell {cell}", f"fields[{i}]"))
        else:
            grid.add(cell)
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
            issues.append(ValidationIssue("warning", "Field key should be alphanumeric with underscores", f"fields[{i}].key"))
    # Recommend common fields
    required = {"username", "rank"}
    keys = {f.get("key", "") for f in fields}
    for req in required - keys:
        issues.append(ValidationIssue("info", f"Missing common field: {req}", "LAYOUT_BLUEPRINTS.BILLET_OFFSETS.offsets"))
    return issues


def validate_ranks(ranks: List[Dict[str, Any]]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    abbrs: Set[str] = set()
    names: Set[str] = set()
    for i, r in enumerate(ranks):
        ab = r.get("abbr", "")
        name = r.get("name", "")
        if not ab or not name:
            issues.append(ValidationIssue("warning", "Rank missing abbr or name", f"RANK_HIERARCHY[{i}]"))
        if ab in abbrs:
            issues.append(ValidationIssue("error", f"Duplicate rank abbr: {ab}", f"RANK_HIERARCHY[{i}].abbr"))
        else:
            abbrs.add(ab)
        if name in names:
            issues.append(ValidationIssue("warning", f"Duplicate rank name: {name}", f"RANK_HIERARCHY[{i}].name"))
        else:
            names.add(name)
        if not re.match(r"^[A-Z]{2,4}$", ab):
            issues.append(ValidationIssue("info", "Rank abbr should be 2-4 uppercase letters", f"RANK_HIERARCHY[{i}].abbr"))
    if ranks:
        top = ranks[-1]
        if top.get("abbr") not in {"CON", "GEN", "ADM"}:
            issues.append(ValidationIssue("info", "Highest rank abbr is unusual; ensure this is intentional", "RANK_HIERARCHY[-1]"))
    return issues


def validate_custom_fields(custom_fields: List[Dict[str, Any]]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    seen: Set[str] = set()
    allowed_types = {"string", "integer", "float", "boolean", "date"}
    for i, f in enumerate(custom_fields):
        key = f.get("key", "")
        if not key:
            issues.append(ValidationIssue("error", "Custom field missing key", f"CUSTOM_FIELDS[{i}].key"))
        if key in seen:
            issues.append(ValidationIssue("error", f"Duplicate custom field key: {key}", f"CUSTOM_FIELDS[{i}].key"))
        else:
            seen.add(key)
        typ = (f.get("type") or "string").lower()
        if typ not in allowed_types:
            issues.append(ValidationIssue("warning", f"Unknown custom field type: {typ}", f"CUSTOM_FIELDS[{i}].type"))
        if f.get("required") and f.get("defaultValue") in (None, ""):
            issues.append(ValidationIssue("info", "Required field missing defaultValue", f"CUSTOM_FIELDS[{i}].defaultValue"))
    return issues


def validate_event_types(events: List[Dict[str, Any]]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    names: Set[str] = set()
    for i, ev in enumerate(events):
        name = ev.get("name", "")
        if not name:
            issues.append(ValidationIssue("error", "Event type missing name", f"EVENT_TYPE_DEFINITIONS[{i}].name"))
        if name in names:
            issues.append(ValidationIssue("warning", f"Duplicate event type name: {name}", f"EVENT_TYPE_DEFINITIONS[{i}].name"))
        else:
            names.add(name)
        aliases = ev.get("aliases", [])
        for j, a in enumerate(aliases):
            if a == name:
                issues.append(ValidationIssue("info", "Alias repeats name", f"EVENT_TYPE_DEFINITIONS[{i}].aliases[{j}]"))
    return issues


def validate_config(config: Dict[str, Any]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    orgs = config.get("ORGANIZATION_HIERARCHY", [])
    if not orgs:
        issues.append(ValidationIssue("error", "Missing ORGANIZATION_HIERARCHY", "ORGANIZATION_HIERARCHY"))
    else:
        issues.extend(validate_org_hierarchy(orgs[0]))
    lb = config.get("LAYOUT_BLUEPRINTS", {}).get("BILLET_OFFSETS", {}).get("offsets", {})
    fields = []
    for k, v in lb.items():
        fields.append({"key": k, "label": k, "row": int(v.get("row", 0)), "col": int(v.get("col", 0))})
    issues.extend(validate_layout_fields(fields))
    ranks = config.get("RANK_HIERARCHY", [])
    issues.extend(validate_ranks(ranks))
    custom_fields = config.get("CUSTOM_FIELDS", [])
    issues.extend(validate_custom_fields(custom_fields))
    events = config.get("EVENT_TYPE_DEFINITIONS", [])
    issues.extend(validate_event_types(events))
    # Sanity check: username and rank offsets within reasonable bounds
    for k in ("username", "rank"):
        off = lb.get(k)
        if isinstance(off, dict):
            r = int(off.get("row", 0))
            c = int(off.get("col", 0))
            if r > 100 or c > 100:
                issues.append(ValidationIssue("warning", f"Offset for {k} seems very large (row={r}, col={c})", f"LAYOUT_BLUEPRINTS.BILLET_OFFSETS.offsets.{k}"))
    return issues
