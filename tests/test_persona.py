"""Persona loading tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigf.persona import get_persona_prompt, list_personas


@pytest.fixture()
def personas(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "personalities"
    d.mkdir()
    (d / "teasing-sister.md").write_text(
        "# 会调戏人的姐姐\n\n## 中文版（推荐）\n你是姐姐。\n\n## English Version\nYou are sister.\n",
        encoding="utf-8",
    )
    (d / "soft-clingy.md").write_text(
        "## 中文版\n软萌。\n\n## English Version\nSoft.\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return d


def test_list_personas(personas: Path) -> None:
    items = list_personas()
    names = {p.name for p in items}
    assert "teasing-sister" in names
    assert "soft-clingy" in names


def test_get_prompt_zh_en(personas: Path) -> None:
    zh = get_persona_prompt("teasing-sister", lang="zh")
    en = get_persona_prompt("teasing-sister", lang="en")
    assert "姐姐" in zh
    assert "sister" in en.lower()
