"""Fresh-install quickstart regressions: the README's 60-second path must work."""

from __future__ import annotations

from pathlib import Path

import pytest

from aigf.context import build_context
from aigf.persona import get_persona_prompt, list_personas


@pytest.fixture()
def fresh(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """An empty directory with no .aigf/ and no local personalities/."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_bundled_personas_available_without_local_dir(fresh: Path) -> None:
    names = {p.name for p in list_personas()}
    assert "teasing-sister" in names
    assert "soft-clingy" in names
    assert "mature-gentle" in names
    assert "cold-beauty" in names
    prompt = get_persona_prompt("teasing-sister", lang="zh")
    assert prompt.strip()


def test_context_build_without_persona_does_not_crash(fresh: Path) -> None:
    text = build_context()
    assert isinstance(text, str)
    assert "【系统角色】" in text
    assert len(text) > 50


def test_init_seeds_editable_personalities(fresh: Path) -> None:
    from aigf.cli import init

    init()
    local = fresh / "personalities"
    assert local.is_dir()
    assert (local / "teasing-sister.md").is_file()
    assert (local / "soft-clingy.md").is_file()
    assert (local / "mature-gentle.md").is_file()
    assert (local / "cold-beauty.md").is_file()
    assert (fresh / ".aigf" / "config.json").is_file()
