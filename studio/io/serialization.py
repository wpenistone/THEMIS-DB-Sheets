from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from .templates import default_config


def to_js_object(data: Any, indent: int = 2) -> str:
    def serialize(obj: Any, level: int = 0) -> str:
        sp = " " * (indent * level)
        if isinstance(obj, dict):
            items = []
            for k, v in obj.items():
                items.append(f"{sp}{' ' * indent}{json.dumps(k)}: {serialize(v, level + 1)}")
            return "{\n" + ",\n".join(items) + f"\n{sp}}"
        if isinstance(obj, list):
            items = [serialize(v, level + 1) for v in obj]
            return "[\n" + ",\n".join([" " * (indent * (level + 1)) + i for i in items]) + f"\n{sp}]"
        return json.dumps(obj)

    return serialize(data, 0)


def export_config_json(config: Dict[str, Any]) -> str:
    return json.dumps(config, indent=2, ensure_ascii=False)


def export_config_js(config: Dict[str, Any]) -> str:
    return "const THEMIS_CONFIG = " + to_js_object(config) + ";\n"


def import_config_json(text: str) -> Dict[str, Any]:
    return json.loads(text)


def import_config_js(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("const THEMIS_CONFIG = ") and cleaned.endswith(";"):
        cleaned = cleaned[len("const THEMIS_CONFIG = ") : -1]
    return json.loads(cleaned)


def merge_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    base = default_config()
    base.update(config)
    return base
