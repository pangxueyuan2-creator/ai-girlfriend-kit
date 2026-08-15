"""Simple data models for memory entries and configuration."""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


VALID_CATEGORIES = {
    "user_profile",
    "preference",
    "relationship",
    "event",
    "boundary",
    "ongoing_topic",
    "favorite",
    "other",
}

VALID_IMPORTANCE = {"high", "medium", "low"}


@dataclass
class MemoryEntry:
    content: str
    category: str = "other"
    importance: str = "medium"
    tags: list[str] = field(default_factory=list)
    source: str = "manual"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    archived: bool = False

    def __post_init__(self) -> None:
        if self.category not in VALID_CATEGORIES:
            self.category = "other"
        if self.importance not in VALID_IMPORTANCE:
            self.importance = "medium"
        if not isinstance(self.tags, list):
            self.tags = []

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MemoryEntry:
        return cls(
            id=str(data.get("id") or uuid.uuid4()),
            content=str(data.get("content") or "").strip(),
            category=str(data.get("category") or "other"),
            importance=str(data.get("importance") or "medium"),
            tags=list(data.get("tags") or []),
            source=str(data.get("source") or "manual"),
            created_at=str(data.get("created_at") or _now_iso()),
            updated_at=str(data.get("updated_at") or _now_iso()),
            archived=bool(data.get("archived", False)),
        )


@dataclass
class Config:
    """Project-level configuration stored in .aigf/config.json."""

    active_persona: str = "teasing-sister"
    language: str = "zh"  # zh | en
    max_memories: int = 12
    max_chars: int = 3500

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Config:
        return cls(
            active_persona=str(data.get("active_persona") or "teasing-sister"),
            language=str(data.get("language") or "zh"),
            max_memories=int(data.get("max_memories") or 12),
            max_chars=int(data.get("max_chars") or 3500),
        )
