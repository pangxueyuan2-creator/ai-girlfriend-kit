"""Resolve project and data paths."""

from __future__ import annotations

from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Walk upward looking for .aigf/ or personalities/."""
    cur = (start or Path.cwd()).resolve()
    for p in [cur, *cur.parents]:
        if (p / ".aigf").is_dir() or (p / "personalities").is_dir():
            return p
    return cur


def aigf_dir(root: Path | None = None) -> Path:
    root = root or find_project_root()
    return root / ".aigf"


def config_path(root: Path | None = None) -> Path:
    return aigf_dir(root) / "config.json"


def memories_path(root: Path | None = None) -> Path:
    return aigf_dir(root) / "memories.jsonl"


def personas_dir(root: Path | None = None) -> Path:
    """Project-local personalities/ wins; bundled package templates are the fallback."""
    root = root or find_project_root()
    local = root / "personalities"
    if local.is_dir():
        return local
    bundled = bundled_personas_dir()
    return bundled if bundled.is_dir() else local


def bundled_personas_dir() -> Path:
    """Templates shipped inside the installed package."""
    return Path(__file__).resolve().parent / "personalities"
