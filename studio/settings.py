from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from .utils import ensure_dir


class Settings:
    def __init__(self, org: Optional[str] = None) -> None:
        base = os.environ.get("THEMIS_STUDIO_HOME") or os.path.join(os.path.expanduser("~"), ".themis_studio")
        ensure_dir(base)
        self.base = base
        self.org = org or "default"
        self.path = os.path.join(self.base, f"{self.org}.json")
        self._data: Dict[str, Any] = {}
        self.load()

    def load(self) -> None:
        if os.path.isfile(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def save(self) -> None:
        ensure_dir(self.base)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self.path)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def last_opened_path(self) -> Optional[str]:
        return self.get("last_opened_path")

    def set_last_opened_path(self, path: str) -> None:
        self.set("last_opened_path", path)

    def window_geometry(self) -> Optional[bytes]:
        val = self.get("window_geometry")
        if isinstance(val, str):
            return bytes.fromhex(val)
        return None

    def set_window_geometry(self, data: bytes) -> None:
        self.set("window_geometry", data.hex())

    def window_state(self) -> Optional[bytes]:
        val = self.get("window_state")
        if isinstance(val, str):
            return bytes.fromhex(val)
        return None

    def set_window_state(self, data: bytes) -> None:
        self.set("window_state", data.hex())
