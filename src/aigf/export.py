"""Export helpers for plain prompt, SillyTavern, OpenWebUI."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .context import build_context
from .persona import get_persona_prompt, load_persona


def _write_private_text(dest: Path, text: str) -> None:
    """Atomically write an export while keeping private context owner-readable only."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=dest.parent,
            prefix=f".{dest.name}.",
            suffix=".tmp",
            delete=False,
        ) as f:
            tmp_path = Path(f.name)
            if os.name == "posix":
                os.fchmod(f.fileno(), 0o600)
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, dest)
        tmp_path = None
        if os.name == "posix":
            dest.chmod(0o600)
    finally:
        if tmp_path is not None and tmp_path.exists():
            tmp_path.unlink()


def export_plain(
    dest: Path | None = None,
    persona: str | None = None,
    lang: str = "zh",
    max_memories: int | None = None,
) -> str:
    """Plain system prompt text (same as context build)."""
    text = build_context(persona=persona, lang=lang, max_memories=max_memories)
    if dest is not None:
        _write_private_text(dest, text)
    return text


def export_sillytavern(
    dest: Path,
    persona: str | None = None,
    lang: str = "zh",
    max_memories: int | None = None,
) -> Path:
    """Minimal SillyTavern character card JSON."""
    from .config import load_config

    cfg = load_config()
    name = persona or cfg.active_persona
    p = load_persona(name)
    display = p.display_name if p else name
    system = build_context(persona=name, lang=lang, max_memories=max_memories)
    persona_only = get_persona_prompt(name, lang=lang)

    card = {
        "name": display,
        "description": persona_only[:500],
        "personality": persona_only,
        "scenario": "",
        "first_mes": "",
        "mes_example": "",
        "system_prompt": system,
        "post_history_instructions": "",
        "tags": ["aigf", "local-first"],
        "creator": "aigf",
        "character_version": "0.1.0",
        "extensions": {"aigf": {"source": "ai-girlfriend-kit", "persona": name}},
    }
    _write_private_text(dest, json.dumps(card, ensure_ascii=False, indent=2) + "\n")
    return dest


def export_openwebui(
    dest: Path,
    persona: str | None = None,
    lang: str = "zh",
    max_memories: int | None = None,
) -> Path:
    """OpenWebUI-style system prompt JSON."""
    from .config import load_config

    cfg = load_config()
    name = persona or cfg.active_persona
    p = load_persona(name)
    display = p.display_name if p else name
    system = build_context(persona=name, lang=lang, max_memories=max_memories)

    payload = {
        "name": display,
        "description": f"Imported from aigf persona `{name}`",
        "system": system,
        "meta": {
            "source": "ai-girlfriend-kit",
            "persona": name,
            "lang": lang,
        },
    }
    _write_private_text(dest, json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    return dest
