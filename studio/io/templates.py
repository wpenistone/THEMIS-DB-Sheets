from __future__ import annotations

from typing import Any, Dict, List


def default_fields() -> List[Dict[str, Any]]:
    return [
        {"key": "username", "label": "Username", "row": 0, "col": 0},
        {"key": "rank", "label": "Rank", "row": 0, "col": 1},
        {"key": "discordId", "label": "Discord ID", "row": 1, "col": 1},
        {"key": "region", "label": "Region", "row": 1, "col": 0},
        {"key": "joinDate", "label": "Join Date", "row": 1, "col": 2},
        {"key": "LOAcheckbox", "label": "LOA", "row": 1, "col": 3},
    ]


def default_org() -> Dict[str, Any]:
    return {
        "name": "Legio VI",
        "sheetName": "Legio VI",
        "children": [
            {
                "name": "First Cohort",
                "sheetName": "VI 1C",
                "children": [
                    {
                        "name": "First Aquilia Contubernium",
                        "sheetName": "VI 1A",
                        "children": [],
                    }
                ],
            }
        ],
    }


def default_config() -> Dict[str, Any]:
    return {
        "ORGANIZATION_HIERARCHY": [default_org()],
        "RANK_HIERARCHY": [
            {"abbr": "AUX", "name": "Auxilia"},
            {"abbr": "TIR", "name": "Tirones"},
            {"abbr": "MIL", "name": "Milites"},
            {"abbr": "CON", "name": "Consul"},
        ],
        "LAYOUT_BLUEPRINTS": {
            "BILLET_OFFSETS": {
                "offsets": {f["key"]: {"row": f["row"], "col": f["col"]} for f in default_fields()}
            }
        },
        "CUSTOM_FIELDS": [],
        "EVENT_TYPE_DEFINITIONS": [
            {"name": "Combat Training", "aliases": ["CT", "Combat Practice"]},
            {"name": "Crate Run", "aliases": ["Crates", "Supply Run"]},
        ],
        "VALIDATION_RULES": {
            "USERNAME": {"REGEX": "^[a-zA-Z0-9_]+$", "MIN_LENGTH": 3, "MAX_LENGTH": 20}
        },
    }
