"""Context builder must be deterministic and offline."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigf.context import build_context
from aigf.memory import MemoryStore


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
        '{"active_persona": "teasing-sister", "language": "zh", "max_memories": 5, "max_chars": 2000}',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_context_includes_persona_and_memories(project: Path) -> None:
    store = MemoryStore(path=project / ".aigf" / "memories.jsonl")
    store.add("我不喜欢被冷暴力", category="preference", importance="high")
    store.add("喜欢被主动关心", category="relationship", importance="high")

    text1 = build_context(lang="zh")
    text2 = build_context(lang="zh")
    assert text1 == text2
    assert "会调戏人的姐姐" in text1
    assert "冷暴力" in text1
    assert "主动关心" in text1
    assert "【长期记忆】" in text1


def test_context_en(project: Path) -> None:
    text = build_context(lang="en")
    assert "[System Role]" in text
