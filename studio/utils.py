from __future__ import annotations

import json
import math
import os
import random
import string
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, TypeVar

T = TypeVar("T")


def clamp(value: float, min_value: float, max_value: float) -> float:
    if value < min_value:
        return min_value
    if value > max_value:
        return max_value
    return value


def snap(value: float, grid: float) -> float:
    if grid <= 0:
        return value
    return round(value / grid) * grid


def gen_id(prefix: str = "id") -> str:
    return f"{prefix}_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def deep_update(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = deep_update(base[k], v)
        else:
            base[k] = v
    return base


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Dict[str, Any]) -> None:
    ensure_dir(os.path.dirname(path) or ".")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def human_readable_bytes(num: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num < 1024.0:
            return f"{num:3.1f}{unit}"
        num /= 1024.0
    return f"{num:.1f}PB"


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def rect_from_points(p1: Tuple[float, float], p2: Tuple[float, float]) -> Tuple[float, float, float, float]:
    x1, y1 = p1
    x2, y2 = p2
    return (min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def midpoint(a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float]:
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def approx_equal(a: float, b: float, eps: float = 1e-6) -> bool:
    return abs(a - b) <= eps


def normalize_angle(degrees: float) -> float:
    d = degrees % 360.0
    if d < 0:
        d += 360.0
    return d


def chunked(seq: Sequence[T], size: int) -> Iterable[Sequence[T]]:
    for i in range(0, len(seq), size):
        yield seq[i : i + size]


def try_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return fallback


def try_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return fallback


def is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


def to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        v = value.strip().lower()
        return v in {"true", "t", "yes", "y", "1", "on"}
    return bool(value)


@dataclass
class FieldDef:
    key: str
    label: str
    row: int = 0
    col: int = 0
    width: int = 1
    height: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "label": self.label,
            "row": self.row,
            "col": self.col,
            "width": self.width,
            "height": self.height,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "FieldDef":
        return FieldDef(
            key=d.get("key", ""),
            label=d.get("label", ""),
            row=int(d.get("row", 0)),
            col=int(d.get("col", 0)),
            width=int(d.get("width", 1)),
            height=int(d.get("height", 1)),
        )


@dataclass
class OrgNode:
    name: str
    sheet_name: str
    children: List["OrgNode"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "sheetName": self.sheet_name,
            "children": [c.to_dict() for c in self.children],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "OrgNode":
        return OrgNode(
            name=d.get("name", ""),
            sheet_name=d.get("sheetName", ""),
            children=[OrgNode.from_dict(x) for x in d.get("children", [])],
        )


def flatten_org(root: OrgNode) -> List[OrgNode]:
    result: List[OrgNode] = []
    def walk(n: OrgNode) -> None:
        result.append(n)
        for c in n.children:
            walk(c)
    walk(root)
    return result


def find_in_org(root: OrgNode, name: str) -> Optional[OrgNode]:
    for n in flatten_org(root):
        if n.name == name:
            return n
    return None


def unique_name(base: str, existing: Iterable[str]) -> str:
    i = 1
    s = set(existing)
    candidate = base
    while candidate in s:
        i += 1
        candidate = f"{base} {i}"
    return candidate


def rect_to_tuple(rect: Any) -> Tuple[float, float, float, float]:
    # Avoid importing Qt here
    x = getattr(rect, "x", lambda: rect[0])()
    y = getattr(rect, "y", lambda: rect[1])()
    w = getattr(rect, "width", lambda: rect[2])()
    h = getattr(rect, "height", lambda: rect[3])()
    return float(x), float(y), float(w), float(h)


def version() -> str:
    return "1.0"
