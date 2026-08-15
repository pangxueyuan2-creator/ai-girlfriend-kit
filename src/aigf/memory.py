"""JSONL-backed memory store with simple deterministic selection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .models import MemoryEntry, VALID_CATEGORIES, VALID_IMPORTANCE, _now_iso
from .paths import memories_path


class MemoryStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or memories_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.touch()

    def _load_all(self) -> list[MemoryEntry]:
        entries: list[MemoryEntry] = []
        if not self.path.exists():
            return entries
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entry = MemoryEntry.from_dict(data)
                    if entry.content:
                        entries.append(entry)
                except (json.JSONDecodeError, TypeError, ValueError):
                    continue
        return entries

    def _save_all(self, entries: Iterable[MemoryEntry]) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e.to_dict(), ensure_ascii=False) + "\n")

    def add(
        self,
        content: str,
        category: str = "other",
        importance: str = "medium",
        tags: list[str] | None = None,
        source: str = "manual",
    ) -> MemoryEntry:
        content = content.strip()
        if not content:
            raise ValueError("Memory content cannot be empty")
        entry = MemoryEntry(
            content=content,
            category=category if category in VALID_CATEGORIES else "other",
            importance=importance if importance in VALID_IMPORTANCE else "medium",
            tags=tags or [],
            source=source,
        )
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
        return entry

    def list(
        self,
        category: str | None = None,
        include_archived: bool = False,
    ) -> list[MemoryEntry]:
        entries = self._load_all()
        if not include_archived:
            entries = [e for e in entries if not e.archived]
        if category:
            entries = [e for e in entries if e.category == category]
        entries.sort(key=lambda e: e.updated_at, reverse=True)
        return entries

    def get(self, memory_id: str) -> MemoryEntry | None:
        for e in self._load_all():
            if e.id == memory_id or e.id.startswith(memory_id):
                return e
        return None

    def remove(self, memory_id: str) -> bool:
        entries = self._load_all()
        new_entries = []
        removed = False
        for e in entries:
            if e.id == memory_id or e.id.startswith(memory_id):
                removed = True
                continue
            new_entries.append(e)
        if removed:
            self._save_all(new_entries)
        return removed

    def edit(
        self,
        memory_id: str,
        content: str | None = None,
        category: str | None = None,
        importance: str | None = None,
        tags: list[str] | None = None,
    ) -> MemoryEntry | None:
        entries = self._load_all()
        target = None
        for e in entries:
            if e.id == memory_id or e.id.startswith(memory_id):
                target = e
                break
        if target is None:
            return None
        if content is not None:
            target.content = content.strip()
        if category is not None and category in VALID_CATEGORIES:
            target.category = category
        if importance is not None and importance in VALID_IMPORTANCE:
            target.importance = importance
        if tags is not None:
            target.tags = tags
        target.updated_at = _now_iso()
        self._save_all(entries)
        return target

    def search(self, query: str, include_archived: bool = False) -> list[MemoryEntry]:
        q = query.lower().strip()
        if not q:
            return []
        results = []
        for e in self.list(include_archived=include_archived):
            hay = f"{e.content} {' '.join(e.tags)} {e.category}".lower()
            if q in hay:
                results.append(e)
        return results

    def select(
        self,
        max_count: int = 12,
        categories: list[str] | None = None,
        prefer_high: bool = True,
    ) -> list[MemoryEntry]:
        entries = self.list(include_archived=False)
        if categories:
            entries = [e for e in entries if e.category in categories]
        weight = {"high": 0, "medium": 1, "low": 2}

        def sort_key(e: MemoryEntry) -> tuple:
            return (
                weight.get(e.importance, 1) if prefer_high else 0,
                -_ts(e.updated_at),
            )

        entries.sort(key=sort_key)
        return entries[: max(0, max_count)]

    def compact(self) -> dict[str, int]:
        entries = self._load_all()
        seen: dict[str, MemoryEntry] = {}
        removed = 0
        for e in entries:
            key = e.content.strip().lower()
            if not key:
                removed += 1
                continue
            if key in seen:
                if e.updated_at > seen[key].updated_at:
                    seen[key] = e
                removed += 1
            else:
                seen[key] = e
        unique = list(seen.values())
        unique.sort(key=lambda e: e.updated_at, reverse=True)
        self._save_all(unique)
        return {"before": len(entries), "after": len(unique), "removed": removed}

    def export_jsonl(self, dest: Path) -> int:
        entries = self.list(include_archived=True)
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("w", encoding="utf-8") as f:
            for e in entries:
                f.write(json.dumps(e.to_dict(), ensure_ascii=False) + "\n")
        return len(entries)


def _ts(iso: str) -> float:
    try:
        from datetime import datetime

        return datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0
