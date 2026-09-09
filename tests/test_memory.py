"""Tests for memory store — deterministic, no network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import aigf.memory as memory_module
from aigf.memory import MemoryStore


@pytest.fixture()
def store(tmp_path: Path) -> MemoryStore:
    return MemoryStore(path=tmp_path / "memories.jsonl")


def test_add_and_list(store: MemoryStore) -> None:
    e = store.add("我不喜欢被冷暴力", category="preference", importance="high")
    assert e.content == "我不喜欢被冷暴力"
    assert e.category == "preference"
    assert e.importance == "high"
    assert len(e.id) > 8

    items = store.list()
    assert len(items) == 1
    assert items[0].content == "我不喜欢被冷暴力"


def test_duplicate_compact(store: MemoryStore) -> None:
    store.add("喜欢被哄", category="preference")
    store.add("喜欢被哄", category="preference")
    store.add("另一件事", category="event")
    stats = store.compact()
    assert stats["before"] == 3
    assert stats["after"] == 2
    assert stats["removed"] == 1
    contents = {e.content for e in store.list()}
    assert contents == {"喜欢被哄", "另一件事"}


def test_search_chinese(store: MemoryStore) -> None:
    store.add("我喜欢别人主动哄我", category="relationship")
    store.add("讨厌加班", category="preference")
    hits = store.search("哄")
    assert len(hits) == 1
    assert "哄" in hits[0].content


def test_remove_by_prefix(store: MemoryStore) -> None:
    e = store.add("临时记忆")
    assert store.remove(e.id[:8]) is True
    assert store.list() == []


def test_ambiguous_prefix_does_not_remove_multiple_memories(store: MemoryStore) -> None:
    store.add("第一条")
    store.add("第二条")
    entries = store._load_all()
    entries[0].id = "abcdef1111111111"
    entries[1].id = "abcdef2222222222"
    store._save_all(entries)

    assert store.get("abcdef") is None
    assert store.remove("abcdef") is False
    assert {entry.id for entry in store.list()} == {
        "abcdef1111111111",
        "abcdef2222222222",
    }
    assert store.remove("abcdef1111111111") is True
    assert [entry.id for entry in store.list()] == ["abcdef2222222222"]


def test_select_prefers_high_importance(store: MemoryStore) -> None:
    store.add("低优先级", importance="low")
    store.add("高优先级", importance="high")
    store.add("中优先级", importance="medium")
    selected = store.select(max_count=2)
    assert selected[0].importance == "high"
    assert len(selected) == 2


def test_empty_content_rejected(store: MemoryStore) -> None:
    with pytest.raises(ValueError):
        store.add("   ")


def test_empty_edit_rejected_without_losing_memory(store: MemoryStore) -> None:
    entry = store.add("保留这条记忆", category="preference")

    with pytest.raises(ValueError):
        store.edit(entry.id, content="   ")

    saved = store.get(entry.id)
    assert saved is not None
    assert saved.content == "保留这条记忆"


def test_rewrite_failure_preserves_original_file(
    store: MemoryStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    store.add("第一条")
    store.add("第二条")
    original = store.path.read_text(encoding="utf-8")
    entries = store._load_all()
    real_dumps = memory_module.json.dumps
    calls = 0

    def flaky_dumps(*args: object, **kwargs: object) -> str:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("simulated serialization failure")
        return real_dumps(*args, **kwargs)

    monkeypatch.setattr(memory_module.json, "dumps", flaky_dumps)

    with pytest.raises(RuntimeError, match="simulated serialization failure"):
        store._save_all(entries)

    assert store.path.read_text(encoding="utf-8") == original
    assert list(store.path.parent.glob(f".{store.path.name}.*.tmp")) == []


def test_malformed_lines_ignored(tmp_path: Path) -> None:
    path = tmp_path / "memories.jsonl"
    path.write_text(
        '{"content": "good", "category": "other", "importance": "medium", '
        '"id": "abc", "created_at": "2026-01-01T00:00:00+00:00", '
        '"updated_at": "2026-01-01T00:00:00+00:00", "tags": [], "source": "manual", "archived": false}\n'
        "this is not json\n"
        "{bad\n",
        encoding="utf-8",
    )
    store = MemoryStore(path=path)
    items = store.list()
    assert len(items) == 1
    assert items[0].content == "good"


def test_export_jsonl(store: MemoryStore, tmp_path: Path) -> None:
    store.add("一条记忆")
    dest = tmp_path / "out.jsonl"
    n = store.export_jsonl(dest)
    assert n == 1
    lines = dest.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    data = json.loads(lines[0])
    assert data["content"] == "一条记忆"
