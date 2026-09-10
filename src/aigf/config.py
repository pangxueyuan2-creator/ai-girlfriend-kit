"""Load / save project config."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Config
from .paths import aigf_dir, config_path


def load_config(root: Path | None = None) -> Config:
    path = config_path(root)
    if not path.is_file():
        return Config()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return Config()
        return Config.from_dict(data)
    except (json.JSONDecodeError, OSError, TypeError, ValueError, OverflowError):
        return Config()


def save_config(cfg: Config, root: Path | None = None) -> None:
    d = aigf_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    path = config_path(root)
    path.write_text(
        json.dumps(cfg.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
