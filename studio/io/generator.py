from __future__ import annotations

from typing import Any, Dict, List


def generate_layout_blueprint(fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    offsets = {}
    for f in fields:
        key = f.get("key")
        if not key:
            continue
        offsets[key] = {"row": int(f.get("row", 0)), "col": int(f.get("col", 0))}
    return {"BILLET_OFFSETS": {"offsets": offsets}}


def generate_config(org_tree: Dict[str, Any], fields: List[Dict[str, Any]], ranks: List[Dict[str, Any]], custom_fields: List[Dict[str, Any]], event_types: List[Dict[str, Any]], rules: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ORGANIZATION_HIERARCHY": [org_tree],
        "RANK_HIERARCHY": ranks,
        "LAYOUT_BLUEPRINTS": generate_layout_blueprint(fields),
        "CUSTOM_FIELDS": custom_fields,
        "EVENT_TYPE_DEFINITIONS": event_types,
        "VALIDATION_RULES": rules,
    }
