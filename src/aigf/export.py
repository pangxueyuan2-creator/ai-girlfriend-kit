"""Export helpers for plain prompt, SillyTavern, OpenWebUI."""

from __future__ import annotations

import json
from pathlib import Path

from .context import build_context
from .persona import get_persona_prompt, load_persona


def export_plain(
    dest: Path | None = None,
    persona: str | None = None,
    lang: str = "zh",
    max_memories: int | None = None,
) -> str:
    """Plain system prompt text (same as context build)."""
    text = build_context(persona=persona, lang=lang, max_memories=max_memories)
    if dest is not None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
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
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(card, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return dest
