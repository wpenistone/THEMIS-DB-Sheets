from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class OrgNode:
    name: str
    sheet_name: str
    children: List["OrgNode"] = field(default_factory=list)

    def add_child(self, node: "OrgNode") -> None:
        self.children.append(node)

    def remove_child(self, node: "OrgNode") -> None:
        self.children = [c for c in self.children if c is not node]

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "sheetName": self.sheet_name, "children": [c.to_dict() for c in self.children]}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "OrgNode":
        return OrgNode(name=d.get("name", ""), sheet_name=d.get("sheetName", ""), children=[OrgNode.from_dict(c) for c in d.get("children", [])])

    def find(self, name: str) -> Optional["OrgNode"]:
        if self.name == name:
            return self
        for c in self.children:
            f = c.find(name)
            if f is not None:
                return f
        return None

    def all_nodes(self) -> List["OrgNode"]:
        out = [self]
        for c in self.children:
            out.extend(c.all_nodes())
        return out

    def path(self) -> List[str]:
        return [self.name]
