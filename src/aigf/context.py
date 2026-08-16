"""Deterministic context builder. No LLM calls."""

from __future__ import annotations

from .config import load_config
from .memory import MemoryStore
from .persona import get_fallback_persona, get_persona_prompt


def build_context(
    persona: str | None = None,
    lang: str | None = None,
    max_memories: int | None = None,
    max_chars: int | None = None,
    extra_notes: str = "",
) -> str:
    cfg = load_config()
    persona_name = persona or cfg.active_persona
    language = lang or cfg.language
    max_mem = max_memories if max_memories is not None else cfg.max_memories
    max_c = max_chars if max_chars is not None else cfg.max_chars

    if persona_name:
        try:
            persona_text = get_persona_prompt(persona_name, lang=language)
        except FileNotFoundError:
            persona_text = get_fallback_persona(language)
    else:
        persona_text = get_fallback_persona(language)

    store = MemoryStore()
    selected = store.select(max_count=max_mem)

    parts: list[str] = []

    if language == "zh":
        parts.append("【系统角色】")
        parts.append(persona_text)
        parts.append("")
        if selected:
            parts.append("【长期记忆】")
            parts.append("以下是你需要长期记住的关于对方的信息。请自然地运用它们，不要生硬复述：")
            for i, m in enumerate(selected, 1):
                tag = f"[{m.category}/{m.importance}]"
                parts.append(f"{i}. {tag} {m.content}")
            parts.append("")
        if extra_notes.strip():
            parts.append("【额外说明】")
            parts.append(extra_notes.strip())
            parts.append("")
        parts.append("【要求】")
        parts.append("- 始终保持角色一致")
        parts.append("- 结合长期记忆自然回应，不要每次都主动把记忆念出来")
        parts.append("- 如果对方说了新的重要信息，可以在心里记住，但本工具不会自动写入")
    else:
        parts.append("[System Role]")
        parts.append(persona_text)
        parts.append("")
        if selected:
            parts.append("[Long-term Memory]")
            parts.append(
                "The following are important facts you should remember about the user. "
                "Use them naturally; do not recite them robotically:"
            )
            for i, m in enumerate(selected, 1):
                tag = f"[{m.category}/{m.importance}]"
                parts.append(f"{i}. {tag} {m.content}")
            parts.append("")
        if extra_notes.strip():
            parts.append("[Additional Notes]")
            parts.append(extra_notes.strip())
            parts.append("")
        parts.append("[Requirements]")
        parts.append("- Stay in character at all times")
        parts.append("- Use long-term memory naturally; do not dump it every turn")
        parts.append("- New important facts are not auto-saved by this tool")

    text = "\n".join(parts).strip() + "\n"

    if len(text) > max_c:
        text = text[: max_c - 20].rstrip() + "\n…(truncated)\n"
    return text
