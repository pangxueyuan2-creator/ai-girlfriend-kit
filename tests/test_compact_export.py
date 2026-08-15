"""Compaction + export tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigf.export import export_openwebui, export_plain, export_sillytavern
from aigf.memory import MemoryStore


@pytest.fixture()
def store(tmp_path: Path) -> MemoryStore:
    return MemoryStore(path=tmp_path / "memories.jsonl")


def test_normalized_duplicate_removal(store: MemoryStore) -> None:
    store.add("我喜欢被哄")
    store.add("我喜欢被哄。")
    store.add("我  喜欢被哄")
    store.add("完全不同的事")
    stats = store.compact()
    assert stats["after"] == 2
    contents = {e.content for e in store.list()}
    assert "完全不同的事" in contents
    assert any("喜欢被哄" in c for c in contents)


def test_archive_excludes_from_select(store: MemoryStore) -> None:
    e = store.add("将被归档", importance="high")
    store.add("仍然活跃", importance="high")
    store.archive(e.id)
    selected = store.select(max_count=10)
    assert all(x.content != "将被归档" for x in selected)
    assert any(x.content == "仍然活跃" for x in selected)
    all_items = store.list(include_archived=True)
    assert any(x.archived and x.content == "将被归档" for x in all_items)


def test_drop_archived_on_compact(store: MemoryStore) -> None:
    e = store.add("旧的")
    store.archive(e.id)
    store.add("新的")
    stats = store.compact(drop_archived=True)
    assert stats["after"] == 1
    assert store.list(include_archived=True)[0].content == "新的"


@pytest.fixture()
def project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "personalities").mkdir()
    (tmp_path / "personalities" / "teasing-sister.md").write_text(
        "## 中文版\n你是会调戏人的姐姐。\n\n## English Version\nYou are a teasing sister.\n",
        encoding="utf-8",
    )
    aigf = tmp_path / ".aigf"
    aigf.mkdir()
    (aigf / "config.json").write_text(
        '{"active_persona": "teasing-sister", "language": "zh", '
        '"max_memories": 5, "max_chars": 4000}',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_export_plain_and_frontends(project: Path, tmp_path: Path) -> None:
    store = MemoryStore(path=project / ".aigf" / "memories.jsonl")
    store.add("测试记忆一条", category="preference", importance="high")

    plain = export_plain(lang="zh")
    assert "会调戏人的姐姐" in plain
    assert "测试记忆" in plain

    st = export_sillytavern(tmp_path / "st.json", lang="zh")
    data = json.loads(st.read_text(encoding="utf-8"))
    assert "system_prompt" in data
    assert "测试记忆" in data["system_prompt"]

    ow = export_openwebui(tmp_path / "ow.json", lang="en")
    data2 = json.loads(ow.read_text(encoding="utf-8"))
    assert "system" in data2
    assert data2["meta"]["lang"] == "en"


def test_compact_keeps_similar_but_different_memories(store: MemoryStore) -> None:
    """Near-dup detection must not merge legitimately different facts."""
    store.add("我喜欢被哄")
    store.add("我喜欢被抱")
    store.add("我不喜欢被冷暴力")
    stats = store.compact()
    assert stats["after"] == 3
    contents = {e.content for e in store.list()}
    assert contents == {"我喜欢被哄", "我喜欢被抱", "我不喜欢被冷暴力"}


def test_export_json_is_valid(project: Path, tmp_path: Path) -> None:
    store = MemoryStore(path=project / ".aigf" / "memories.jsonl")
    store.add("valid-json-check", importance="high")
    st = export_sillytavern(tmp_path / "st2.json")
    ow = export_openwebui(tmp_path / "ow2.json")
    data_st = json.loads(st.read_text(encoding="utf-8"))
    data_ow = json.loads(ow.read_text(encoding="utf-8"))
    assert isinstance(data_st, dict) and "system_prompt" in data_st
    assert isinstance(data_ow, dict) and "system" in data_ow
