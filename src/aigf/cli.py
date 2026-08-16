"""CLI entry point for aigf."""

from __future__ import annotations

from pathlib import Path

import typer

from . import __version__
from .config import load_config, save_config
from .context import build_context
from .doctor import run_doctor
from .memory import MemoryStore
from .paths import aigf_dir, bundled_personas_dir, find_project_root, memories_path, personas_dir
from .persona import get_persona_prompt, list_personas, load_persona

app = typer.Typer(
    name="aigf",
    help="Local-first AI companion personality & memory toolkit.",
    no_args_is_help=True,
    add_completion=False,
)

memory_app = typer.Typer(help="Manage long-term memories.")
persona_app = typer.Typer(help="Manage personas.")
context_app = typer.Typer(help="Build ready-to-paste context for your model.")
export_app = typer.Typer(help="Export prompts for frontends.")
app.add_typer(memory_app, name="memory")
app.add_typer(persona_app, name="persona")
app.add_typer(context_app, name="context")
app.add_typer(export_app, name="export")


@app.callback()
def main_callback() -> None:
    """aigf — local AI companion toolkit."""


@app.command()
def version() -> None:
    """Show version."""
    typer.echo(__version__)


@app.command()
def init(
    force: bool = typer.Option(False, "--force", help="Re-create config if exists"),
) -> None:
    """Initialize .aigf/ in the current project."""
    root = find_project_root()
    d = aigf_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    cfg_path = d / "config.json"
    if cfg_path.exists() and not force:
        typer.echo(f"Already initialized: {d}")
        typer.echo("Use --force to overwrite config.")
        raise typer.Exit(0)

    from .models import Config

    save_config(Config(), root)
    mem = memories_path(root)
    if not mem.exists():
        mem.touch()

    # Seed the bundled persona templates so `persona set` works right away and
    # users can edit them as plain markdown in their own project.
    local_personas = root / "personalities"
    bundled = bundled_personas_dir()
    seeded = 0
    if bundled.is_dir():
        local_personas.mkdir(parents=True, exist_ok=True)
        for template in sorted(bundled.glob("*.md")):
            destination = local_personas / template.name
            if not destination.exists():
                destination.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
                seeded += 1
    typer.echo(f"Initialized: {d}")
    typer.echo(f"Memories   : {mem}")
    typer.echo(f"Personas   : {local_personas} (seeded {seeded} template(s))")
    typer.echo("Next: aigf persona list  →  aigf persona set <name>  →  aigf memory add ...")


@app.command()
def doctor() -> None:
    """Check local setup and look for obvious problems."""
    for line in run_doctor():
        typer.echo(line)


@context_app.callback(invoke_without_command=True)
def context_root(
    ctx: typer.Context,
    persona: str | None = typer.Option(None, "--persona", "-p", help="Persona name"),
    lang: str | None = typer.Option(None, "--lang", "-l", help="zh or en"),
    max_memories: int | None = typer.Option(None, "--max-memories"),
    max_chars: int | None = typer.Option(None, "--max-chars"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    """Build a ready-to-paste context (same as `aigf context build`)."""
    if ctx.invoked_subcommand is not None:
        return
    text = build_context(
        persona=persona,
        lang=lang,
        max_memories=max_memories,
        max_chars=max_chars,
        extra_notes=notes,
    )
    typer.echo(text)


@context_app.command("build")
def context_build(
    persona: str | None = typer.Option(None, "--persona", "-p"),
    lang: str | None = typer.Option(None, "--lang", "-l"),
    max_memories: int | None = typer.Option(None, "--max-memories"),
    max_chars: int | None = typer.Option(None, "--max-chars"),
    notes: str = typer.Option("", "--notes"),
) -> None:
    """Build a ready-to-paste context for your model / frontend."""
    text = build_context(
        persona=persona,
        lang=lang,
        max_memories=max_memories,
        max_chars=max_chars,
        extra_notes=notes,
    )
    typer.echo(text)


@memory_app.command("add")
def memory_add(
    content: str = typer.Argument(...),
    category: str = typer.Option("other", "--category", "-c"),
    importance: str = typer.Option("medium", "--importance", "-i"),
    tag: list[str] = typer.Option([], "--tag", "-t"),
) -> None:
    """Add a long-term memory."""
    store = MemoryStore()
    entry = store.add(content=content, category=category, importance=importance, tags=tag)
    typer.echo(f"Added [{entry.id[:8]}] ({entry.category}/{entry.importance})")
    typer.echo(entry.content)


@memory_app.command("list")
def memory_list(
    category: str | None = typer.Option(None, "--category", "-c"),
    all_: bool = typer.Option(False, "--all", help="Include archived"),
) -> None:
    """List memories (newest first)."""
    store = MemoryStore()
    entries = store.list(category=category, include_archived=all_)
    if not entries:
        typer.echo("(no memories)")
        raise typer.Exit(0)
    for e in entries:
        archived = " [archived]" if e.archived else ""
        typer.echo(f"{e.id[:8]}  {e.category}/{e.importance}{archived}  {e.content}")


@memory_app.command("search")
def memory_search(query: str = typer.Argument(...)) -> None:
    """Search memories by keyword."""
    store = MemoryStore()
    results = store.search(query)
    if not results:
        typer.echo("(no matches)")
        raise typer.Exit(0)
    for e in results:
        typer.echo(f"{e.id[:8]}  {e.category}/{e.importance}  {e.content}")


@memory_app.command("remove")
def memory_remove(memory_id: str = typer.Argument(...)) -> None:
    """Remove a memory by id (prefix ok)."""
    store = MemoryStore()
    ok = store.remove(memory_id)
    if ok:
        typer.echo(f"Removed {memory_id}")
    else:
        typer.echo(f"Not found: {memory_id}", err=True)
        raise typer.Exit(1)


@memory_app.command("archive")
def memory_archive(memory_id: str = typer.Argument(...)) -> None:
    """Soft-delete: mark memory as archived."""
    store = MemoryStore()
    entry = store.archive(memory_id)
    if entry is None:
        typer.echo(f"Not found: {memory_id}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Archived [{entry.id[:8]}]")


@memory_app.command("unarchive")
def memory_unarchive(memory_id: str = typer.Argument(...)) -> None:
    """Restore an archived memory."""
    store = MemoryStore()
    entry = store.unarchive(memory_id)
    if entry is None:
        typer.echo(f"Not found: {memory_id}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Unarchived [{entry.id[:8]}]")


@memory_app.command("edit")
def memory_edit(
    memory_id: str = typer.Argument(...),
    content: str | None = typer.Option(None, "--content"),
    category: str | None = typer.Option(None, "--category", "-c"),
    importance: str | None = typer.Option(None, "--importance", "-i"),
) -> None:
    """Edit an existing memory."""
    store = MemoryStore()
    entry = store.edit(memory_id, content=content, category=category, importance=importance)
    if entry is None:
        typer.echo(f"Not found: {memory_id}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Updated [{entry.id[:8]}] {entry.category}/{entry.importance}")
    typer.echo(entry.content)


@memory_app.command("compact")
def memory_compact(
    drop_archived: bool = typer.Option(False, "--drop-archived"),
) -> None:
    """Remove exact/near duplicates; optionally drop archived."""
    store = MemoryStore()
    stats = store.compact(drop_archived=drop_archived)
    typer.echo(f"Before: {stats['before']}  After: {stats['after']}  Removed: {stats['removed']}")


@memory_app.command("export")
def memory_export(dest: Path = typer.Argument(...)) -> None:
    """Export all memories to a JSONL file."""
    store = MemoryStore()
    n = store.export_jsonl(dest)
    typer.echo(f"Exported {n} entries → {dest}")


@persona_app.command("list")
def persona_list() -> None:
    """List available personas."""
    personas = list_personas()
    if not personas:
        typer.echo(f"(no personas found in {personas_dir()})")
        raise typer.Exit(0)
    cfg = load_config()
    for p in personas:
        mark = " *" if p.name == cfg.active_persona else ""
        typer.echo(f"{p.name}{mark}")


@persona_app.command("show")
def persona_show(
    name: str = typer.Argument(...),
    lang: str = typer.Option("zh", "--lang", "-l"),
) -> None:
    """Show persona prompt text."""
    try:
        text = get_persona_prompt(name, lang=lang)
    except FileNotFoundError as e:
        typer.echo(str(e), err=True)
        raise typer.Exit(1) from None
    typer.echo(text)


@persona_app.command("set")
def persona_set(name: str = typer.Argument(...)) -> None:
    """Set the active persona."""
    p = load_persona(name)
    if p is None:
        typer.echo(f"Persona not found: {name}", err=True)
        raise typer.Exit(1)
    cfg = load_config()
    cfg.active_persona = p.name
    save_config(cfg)
    typer.echo(f"Active persona → {p.name}")


@persona_app.command("export")
def persona_export(
    name: str = typer.Argument(...),
    lang: str = typer.Option("zh", "--lang", "-l"),
) -> None:
    """Export persona prompt to stdout."""
    persona_show(name, lang=lang)


@export_app.command("prompt")
def export_prompt(
    dest: Path | None = typer.Option(None, "--out", "-o"),
    persona: str | None = typer.Option(None, "--persona", "-p"),
    lang: str = typer.Option("zh", "--lang", "-l"),
    max_memories: int | None = typer.Option(None, "--max-memories"),
) -> None:
    """Export plain system prompt (same as context build)."""
    from .export import export_plain

    text_out = export_plain(dest=dest, persona=persona, lang=lang, max_memories=max_memories)
    if dest is None:
        typer.echo(text_out)
    else:
        typer.echo(f"Wrote {dest}")


@export_app.command("sillytavern")
def export_st(
    dest: Path = typer.Argument(...),
    persona: str | None = typer.Option(None, "--persona", "-p"),
    lang: str = typer.Option("zh", "--lang", "-l"),
) -> None:
    """Export a minimal SillyTavern character card JSON."""
    from .export import export_sillytavern

    path = export_sillytavern(dest, persona=persona, lang=lang)
    typer.echo(f"Wrote {path}")


@export_app.command("openwebui")
def export_owui(
    dest: Path = typer.Argument(...),
    persona: str | None = typer.Option(None, "--persona", "-p"),
    lang: str = typer.Option("zh", "--lang", "-l"),
) -> None:
    """Export an OpenWebUI-style system prompt JSON."""
    from .export import export_openwebui

    path = export_openwebui(dest, persona=persona, lang=lang)
    typer.echo(f"Wrote {path}")


@app.command()
def migrate(
    legacy: Path = typer.Argument(..., help="Path to old memory-template.md or similar"),
) -> None:
    """Import plain text / markdown legacy memory into structured store."""
    if not legacy.is_file():
        typer.echo(f"File not found: {legacy}", err=True)
        raise typer.Exit(1)
    text = legacy.read_text(encoding="utf-8")
    store = MemoryStore()
    added = 0
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(("：", ":")):
            continue
        store.add(content=line, category="other", importance="medium", source="migrate")
        added += 1
    typer.echo(f"Imported {added} lines from {legacy}")


if __name__ == "__main__":
    app()
