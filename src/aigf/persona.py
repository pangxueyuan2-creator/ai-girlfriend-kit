"""Persona loading and management. Personas remain human-editable markdown."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .paths import personas_dir


@dataclass
class Persona:
    name: str
    path: Path
    body: str
    language_sections: dict[str, str]

    @property
    def display_name(self) -> str:
        return self.name.replace("-", " ").title()


def list_personas(root: Path | None = None) -> list[Persona]:
    d = personas_dir(root)
    if not d.is_dir():
        return []
    result = []
    for p in sorted(d.glob("*.md")):
        if p.name.startswith("."):
            continue
        persona = load_persona(p.stem, root)
        if persona:
            result.append(persona)
    return result


def load_persona(name: str, root: Path | None = None) -> Persona | None:
    d = personas_dir(root)
    path = d / f"{name}.md"
    if not path.is_file():
        for p in d.glob("*.md"):
            if p.stem.lower() == name.lower():
                path = p
                break
        else:
            return None
    text = path.read_text(encoding="utf-8")
    sections = _split_language_sections(text)
    return Persona(name=path.stem, path=path, body=text, language_sections=sections)


def get_persona_prompt(name: str, lang: str = "zh", root: Path | None = None) -> str:
    persona = load_persona(name, root)
    if not persona:
        raise FileNotFoundError(f"Persona not found: {name}")
    if lang in persona.language_sections and persona.language_sections[lang].strip():
        return persona.language_sections[lang].strip()
    for key in ("zh", "en"):
        if key in persona.language_sections and persona.language_sections[key].strip():
            return persona.language_sections[key].strip()
    return persona.body.strip()


def _split_language_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {"zh": "", "en": ""}
    zh_patterns = [
        r"##\s*中文版[^\n]*\n(.*?)(?=##\s*English|\Z)",
        r"##\s*中文[^\n]*\n(.*?)(?=##\s*English|\Z)",
    ]
    en_patterns = [
        r"##\s*English Version[^\n]*\n(.*?)(?=##\s*中文|\Z)",
        r"##\s*English[^\n]*\n(.*?)(?=##\s*中文|\Z)",
    ]
    for pat in zh_patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            sections["zh"] = m.group(1).strip()
            break
    for pat in en_patterns:
        m = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        if m:
            sections["en"] = m.group(1).strip()
            break
    if not sections["zh"] and not sections["en"]:
        sections["zh"] = text.strip()
        sections["en"] = text.strip()
    return sections
