"""Simple local health checks. No network, no exaggerated claims."""

from __future__ import annotations

import re

from .paths import aigf_dir, config_path, memories_path, personas_dir

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xai-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]


def run_doctor() -> list[str]:
    lines: list[str] = []
    root_aigf = aigf_dir()
    lines.append(
        f"Project .aigf dir : {root_aigf} ({'exists' if root_aigf.is_dir() else 'missing'})"
    )
    lines.append(
        f"Config            : {config_path()} ({'ok' if config_path().is_file() else 'missing'})"
    )
    lines.append(
        f"Memories file     : {memories_path()} ({'ok' if memories_path().is_file() else 'missing'})"
    )
    pdir = personas_dir()
    count = len(list(pdir.glob("*.md"))) if pdir.is_dir() else 0
    lines.append(f"Personas dir      : {pdir} ({count} personas)")

    mem = memories_path()
    if mem.is_file():
        text = mem.read_text(encoding="utf-8", errors="ignore")
        found = []
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                found.append(pat.pattern[:20] + "…")
        if found:
            lines.append("WARNING: possible secrets detected in memories file:")
            for f in found:
                lines.append(f"  - pattern {f}")
            lines.append("  Consider removing them. Memory files can contain private data.")
        else:
            lines.append("Secret scan      : no obvious API-key patterns found in memories")
    else:
        lines.append("Secret scan      : skipped (no memories file yet)")

    lines.append("")
    lines.append("Privacy reminder: memory files may contain highly personal information.")
    lines.append("This tool never uploads data. Keep .aigf/ out of public repos if needed.")
    return lines
