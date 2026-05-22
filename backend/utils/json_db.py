"""JSON file database helper with auto-create and atomic writes."""

import json
import os
import shutil
from pathlib import Path
from typing import Any


class JsonDatabase:
    def __init__(self, path: Path, default: Any = None):
        self.path = Path(path)
        self.default = default if default is not None else []
        self._ensure_file()

    def _ensure_file(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.write(self.default)

    def read(self) -> Any:
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            backup = self.path.with_suffix(".json.bak")
            if backup.exists():
                try:
                    with open(backup, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    self.write(data)
                    return data
                except (json.JSONDecodeError, OSError):
                    pass
            self.write(self.default)
            return self.default if not callable(self.default) else self.default()

    def write(self, data: Any) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_suffix(".json.tmp")
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp_path, self.path)
            try:
                shutil.copy2(self.path, self.path.with_suffix(".json.bak"))
            except OSError:
                pass
        finally:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
