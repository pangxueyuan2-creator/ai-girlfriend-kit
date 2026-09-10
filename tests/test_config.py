from __future__ import annotations

import json
from pathlib import Path

import pytest

from aigf.config import load_config
from aigf.models import Config


def _write_config(root: Path, payload: object) -> None:
    directory = root / ".aigf"
    directory.mkdir(parents=True)
    (directory / "config.json").write_text(json.dumps(payload), encoding="utf-8")


def test_load_config_falls_back_for_non_object_json(tmp_path: Path) -> None:
    _write_config(tmp_path, ["not", "an", "object"])

    assert load_config(tmp_path) == Config()


@pytest.mark.parametrize("value", ["not-a-number", {}, []])
def test_load_config_falls_back_for_invalid_numeric_values(
    tmp_path: Path, value: object
) -> None:
    _write_config(tmp_path, {"max_memories": value})

    assert load_config(tmp_path) == Config()


def test_load_config_preserves_valid_values(tmp_path: Path) -> None:
    _write_config(
        tmp_path,
        {
            "active_persona": "warm-companion",
            "language": "en",
            "max_memories": 24,
            "max_chars": 6400,
        },
    )

    assert load_config(tmp_path) == Config(
        active_persona="warm-companion",
        language="en",
        max_memories=24,
        max_chars=6400,
    )
