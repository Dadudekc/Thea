#!/usr/bin/env python3
"""
Dream.OS Toolbelt
=================

A compact Typer-powered CLI that wraps common Dream.OS workflows.
This tool consolidates repetitive GUI, DB, memory and Discord operations
into script-friendly commands so you can iterate without opening the GUI.

Only a subset of the proposed commands are fully implemented right now
(theme switch, GUI inspect, DB utilities).  The remaining groups are
stubbed with clear TODOs that call into the existing architecture.

Usage examples:
  dreamos theme switch dark
  dreamos gui inspect --out widgets.json
  dreamos db ls tables
  dreamos db query "SELECT COUNT(*) FROM conversations"

Note: Entry-point is set to `dreamos` for convenience (see setup.py).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
from rich import print as rprint
from rich.table import Table
from rich.console import Console

# Re-use existing settings and processing modules
from core.settings_manager import settings_manager

# Tools DB helpers
from tools_db import connect as tools_connect, list_tools as tools_list, fetch_tool as tools_fetch, load_tool_code
from rich.syntax import Syntax

# Constants
APP_NAME = "Dream.OS Toolbelt"
DB_PATH = Path.cwd() / "dreamos_memory.db"
console = Console()

app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]},
    add_completion=False,
)

# ---------------------------------------------------------------------------
# ROOT CALLBACK (handles --help-tools)
# ---------------------------------------------------------------------------

@app.callback(invoke_without_command=True)
def _root_callback(
    ctx: typer.Context,
    help_tools: bool = typer.Option(
        False,
        "--help-tools",
        help="Show Tools Database catalog in addition to normal help and exit",
        is_flag=True,
    ),
):
    """Intercept --help-tools to append tools catalog then exit."""
    if help_tools:
        # Show default help first
        typer.echo(ctx.get_help())

        # Display tools table (auto-ingest if empty)
        from tools_db.ingest_tools import run as ingest_run  # local import to avoid overhead

        conn = tools_connect()
        names = tools_list(conn)
        if not names:
            typer.echo("(Tools DB empty — running initial ingestion…)")
            ingest_run()
            names = tools_list(conn)

        table = Table(title="Available CLI Tools")
        table.add_column("#", justify="right")
        table.add_column("Name")
        for idx, name in enumerate(names, 1):
            table.add_row(str(idx), name)
        console.print(table)
        raise typer.Exit()

# ---------------------------------------------------------------------------
# THEME COMMANDS
# ---------------------------------------------------------------------------

theme_app = typer.Typer(help="Theme utilities (switch, inspect)")

@theme_app.command("switch")
def theme_switch(
    theme: str = typer.Argument(..., help="dark | light | system", metavar="[dark|light|system]"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show the diff without changing anything"),
):
    """Switch the current application theme without opening the GUI."""
    valid = {"dark": "Dark", "light": "Light", "system": "System"}
    if theme.lower() not in valid:
        typer.echo("[bold red]Invalid theme.[/bold red] Choose from dark|light|system")
        raise typer.Exit(1)

    desired = valid[theme.lower()]
    current = settings_manager.get_theme()

    if dry_run:
        typer.echo(f"Would switch theme from '{current}' -> '{desired}'")
        raise typer.Exit()

    if current == desired:
        typer.echo(f"Theme already set to '{desired}'. Nothing to do.")
        raise typer.Exit()

    settings_manager.set_theme(desired)
    typer.echo(f"✅ Theme switched to '{desired}'.")

app.add_typer(theme_app, name="theme")

# ---------------------------------------------------------------------------
# GUI COMMANDS
# ---------------------------------------------------------------------------

gui_app = typer.Typer(help="GUI-related helpers (state inspection, theme overrides)")

@gui_app.command("inspect")
def gui_inspect(
    out: Optional[Path] = typer.Option(None, "--out", help="Write widget tree to JSON file"),
):
    """Dump the current PyQt widget tree (names, classes, palette) to JSON or stdout."""
    try:
        from PyQt6.QtWidgets import QApplication
    except ImportError as e:
        typer.echo("[bold red]PyQt6 not available — cannot inspect GUI.[/bold red]")
        raise typer.Exit(1) from e

    app_instance = QApplication.instance()
    if app_instance is None:
        typer.echo("[bold red]No running QApplication instance found.[/bold red]  Launch the GUI first.")
        raise typer.Exit(1)

    def walk_widget(widget) -> Dict[str, Any]:
        palette = widget.palette()
        return {
            "object_name": widget.objectName(),
            "class": widget.__class__.__name__,
            "geometry": [widget.x(), widget.y(), widget.width(), widget.height()],
            "palette": {
                "window": palette.window().color().name(),
                "base": palette.base().color().name(),
                "text": palette.text().color().name(),
            },
            "children": [walk_widget(child) for child in widget.findChildren(type(widget))],
        }

    trees: List[Dict[str, Any]] = [walk_widget(w) for w in app_instance.topLevelWidgets()]

    if out:
        out.write_text(json.dumps(trees, indent=2))
        typer.echo(f"✅ Widget tree exported to {out}")
    else:
        rprint(trees)

app.add_typer(gui_app, name="gui")

# ---------------------------------------------------------------------------
# DATABASE COMMANDS
# ---------------------------------------------------------------------------

db_app = typer.Typer(help="Memory / database utilities")

@db_app.command("ls")
def db_ls(which: str = typer.Argument("tables", help="tables | schema")):
    """List tables or full schema."""
    if not DB_PATH.exists():
        typer.echo(f"[bold red]DB not found at {DB_PATH}[/bold red]")
        raise typer.Exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if which == "tables":
        rows = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        table = Table(title="Database Tables")
        table.add_column("#")
        table.add_column("Name")
        for idx, (name,) in enumerate(rows, 1):
            table.add_row(str(idx), name)
        console.print(table)
    elif which == "schema":
        rows = cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';").fetchall()
        for sql, in rows:
            rprint(sql)
            rprint("\n")
    else:
        typer.echo("[bold red]Unknown option. Use 'tables' or 'schema'.[/bold red]")
        raise typer.Exit(1)

    conn.close()

@db_app.command("query")
def db_query(sql: str = typer.Argument(..., help="SQL statement to execute")):
    """Run a read-only SQL query and pretty-print the result."""
    if not DB_PATH.exists():
        typer.echo(f"[bold red]DB not found at {DB_PATH}[/bold red]")
        raise typer.Exit(1)

    conn = sqlite3.connect(DB_PATH, uri=True, check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
    except sqlite3.Error as e:
        typer.echo(f"[bold red]SQL error:[/bold red] {e}")
        raise typer.Exit(1)
    finally:
        conn.close()

    if not rows:
        typer.echo("(no rows)")
        raise typer.Exit()

    # Render with Rich table
    table = Table(show_header=True, header_style="bold magenta")
    for col in range(len(rows[0])):
        table.add_column(f"col{col}")
    for row in rows:
        table.add_row(*[str(item) for item in row])
    console.print(table)

@db_app.command("stats")
def db_stats():
    """Show quick stats (row counts) for all tables."""
    if not DB_PATH.exists():
        typer.echo(f"[bold red]DB not found at {DB_PATH}[/bold red]")
        raise typer.Exit(1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
    table = Table(title="Row counts")
    table.add_column("Table")
    table.add_column("Rows", justify="right")

    for (tname,) in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {tname};").fetchone()[0]
        table.add_row(tname, str(count))
    console.print(table)
    conn.close()

@db_app.command("migrate")
def db_migrate(sql_file: Optional[Path] = typer.Argument(None, help="Path to .sql file; omit for stdin")):
    """Apply small schema tweaks with auto-backup."""
    if not DB_PATH.exists():
        typer.echo(f"[bold red]DB not found at {DB_PATH}[/bold red]")
        raise typer.Exit(1)

    sql_text = ""
    if sql_file:
        sql_text = sql_file.read_text()
    else:
        sql_text = sys.stdin.read()

    if not sql_text.strip():
        typer.echo("[bold red]No SQL provided.[/bold red]")
        raise typer.Exit(1)

    backup_path = DB_PATH.with_suffix(".bak")
    DB_PATH.replace(backup_path)
    typer.echo(f"🗄️  Backup created at {backup_path}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.executescript(sql_text)
        conn.commit()
        typer.echo("✅ Migration applied successfully.")
    except sqlite3.Error as e:
        typer.echo(f"[bold red]Migration failed:[/bold red] {e}\nRestoring backup…")
        conn.close()
        backup_path.replace(DB_PATH)
        raise typer.Exit(1)
    conn.close()

app.add_typer(db_app, name="db")

# ---------------------------------------------------------------------------
# TOOLS DATABASE COMMANDS (Phase-1)
# ---------------------------------------------------------------------------

tools_app = typer.Typer(help="Tools Database utilities (list, show, run)")

@tools_app.command("list")
def tools_list_cmd():
    """List all tools stored in the Tools Database."""
    conn = tools_connect()
    names = tools_list(conn)
    if not names:
        typer.echo("(no tools found — run ingest_tools first)")
        raise typer.Exit()

    table = Table(title="Available CLI Tools")
    table.add_column("#", justify="right")
    table.add_column("Name")
    for idx, name in enumerate(names, 1):
        table.add_row(str(idx), name)
    console.print(table)

@tools_app.command("show")
def tools_show(name: str = typer.Argument(..., help="Tool name")):
    """Display the source code of a tool with syntax highlighting."""
    conn = tools_connect()
    row = tools_fetch(conn, name)
    if row is None:
        typer.echo(f"[bold red]Tool '{name}' not found.[/bold red]")
        raise typer.Exit(1)

    syntax = Syntax(row["code"], "python", theme="monokai", line_numbers=True)
    console.print(syntax)

@tools_app.command("run")
def tools_run(name: str = typer.Argument(..., help="Tool name"), args: List[str] = typer.Argument(None, help="Args after --")):
    """Dynamically execute a stored tool (experimental)."""
    import importlib.util
    import types

    conn = tools_connect()
    code = load_tool_code(conn, name)
    if code is None:
        typer.echo(f"[bold red]Tool '{name}' not found.[/bold red]")
        raise typer.Exit(1)

    module_name = f"_db_tool_{name}"
    spec = importlib.util.spec_from_loader(module_name, loader=None)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    exec(code, module.__dict__)

    if hasattr(module, "main") and callable(module.main):
        module.main(*(args or []))
    else:
        typer.echo("[yellow]Tool loaded but no callable 'main' found — nothing executed.[/yellow]")

@tools_app.command("ingest")
def tools_ingest(force: bool = typer.Option(False, "--force", help="Re-ingest even if DB already populated")):
    """Import on-disk tools into the Tools Database.
    This wraps `tools_db.ingest_tools.run()` so users can execute:
        dreamos tools ingest
    without knowing the underlying module path.
    """
    from tools_db.ingest_tools import run as ingest_run

    if not force:
        conn = tools_connect()
        if tools_list(conn):
            typer.echo("(Tools DB already populated – use --force to re-ingest)")
            raise typer.Exit()

    ingest_run()
    typer.echo("✅ Ingestion complete.")

app.add_typer(tools_app, name="tools")

# ---------------------------------------------------------------------------
# STUBS FOR REMAINING GROUPS (convo, chat, tpl, dev, discord)
# ---------------------------------------------------------------------------

convo_app = typer.Typer(help="Conversation workflows")
chat_app = typer.Typer(help="ChatGPT / API diagnostics")
tpl_app = typer.Typer(help="Template rendering helpers")
dev_app = typer.Typer(help="Dev-quality automation")
discord_app = typer.Typer(help="Discord bot helpers")

# Placeholder commands -------------------------------------------------------

@convo_app.command("export")
def convo_export():
    """[TODO] Export conversations."""
    typer.echo("TODO: convo export not yet implemented")

@chat_app.command("test-key")
def chat_test_key(key: str):
    """[TODO] Test OpenAI key latency."""
    typer.echo("TODO: chat test-key not yet implemented")

@tpl_app.command("render")
def tpl_render():
    """[TODO] Render Jinja template."""
    typer.echo("TODO: tpl render not yet implemented")

@dev_app.command("lint")
def dev_lint():
    """[TODO] Run linting suite."""
    typer.echo("TODO: dev lint not yet implemented")

@discord_app.command("send")
def discord_send():
    """[TODO] Send a message via Discord bot."""
    typer.echo("TODO: discord send not yet implemented")

@discord_app.command("ids")
def discord_ids(token: Optional[str] = typer.Option(None, "--token", help="Override bot token (else uses DISCORD_BOT_TOKEN)"),
                 guild_filter: Optional[int] = typer.Option(None, "--guild", help="Filter output to a specific guild ID")):
    """List all guilds and text channels the bot can access.

    Example:
        dreamos discord ids --guild 123456789012345678
    """
    try:
        import asyncio
        import os
        import discord  # type: ignore
    except ImportError:
        typer.echo("[bold red]discord.py not installed.[/bold red]  Install with `pip install discord.py`.")
        raise typer.Exit(1)

    tok = token or os.getenv("DISCORD_BOT_TOKEN")
    if not tok:
        typer.echo("[bold red]Bot token not set.  Provide via --token or DISCORD_BOT_TOKEN env var.[/bold red]")
        raise typer.Exit(1)

    intents = discord.Intents.none()
    intents.guilds = True  # We only need guild / channel metadata

    table = Table(title="Accessible Guilds / Channels")
    table.add_column("Guild ID", style="cyan")
    table.add_column("Guild Name")
    table.add_column("Channel ID", style="magenta")
    table.add_column("Channel Name")

    client = discord.Client(intents=intents)

    @client.event  # type: ignore[misc]
    async def on_ready():  # noqa: D401
        for g in client.guilds:
            if guild_filter and g.id != guild_filter:
                continue
            for ch in sorted(g.text_channels, key=lambda c: c.position):
                table.add_row(str(g.id), g.name, str(ch.id), ch.name)
        console.print(table)
        await client.close()

    asyncio.run(client.start(tok))

@discord_app.command("set")
def discord_set(
    token: Optional[str] = typer.Option(None, "--token", help="Bot token"),
    app_id: Optional[str] = typer.Option(None, "--app", help="Application ID"),
    guild_id: Optional[str] = typer.Option(None, "--guild", help="Guild (server) ID"),
    channel: Optional[str] = typer.Option(None, "--channel", help="Default channel ID"),
    devlog: Optional[str] = typer.Option(None, "--devlog", help="Devlog channel ID"),
    mmrpg: Optional[str] = typer.Option(None, "--mmrpg", help="MMORPG channel ID"),
    agent_memory: Optional[str] = typer.Option(None, "--agent-memory", help="Agent Memory channel ID"),
    agent_prompt: Optional[str] = typer.Option(None, "--agent-prompt", help="Agent Prompt channel ID"),
    agent_scraper: Optional[str] = typer.Option(None, "--agent-scraper", help="Agent Scraper channel ID"),
    agent_core: Optional[str] = typer.Option(None, "--agent-core", help="Agent Core channel ID"),
    interactive: bool = typer.Option(False, "--interactive", help="Prompt for missing values interactively"),
):
    """Quickly write Discord IDs/tokens into your .env.

    Any option not provided via flag (and not already present) will be prompted if
    --interactive is supplied; otherwise it's left unchanged.
    """
    from tools.dreamos_cli import DreamOSCLI

    cli = DreamOSCLI()
    current = cli._load_env_config()

    updates = {}
    def maybe_set(key: str, value: Optional[str]):
        if value:
            updates[key] = value.strip()
        elif interactive and not current.get(key):
            prompt_val = typer.prompt(f"Enter value for {key}")
            if prompt_val:
                updates[key] = prompt_val.strip()

    maybe_set("DISCORD_BOT_TOKEN", token)
    maybe_set("DISCORD_APPLICATION_ID", app_id)
    maybe_set("DISCORD_GUILD_ID", guild_id)
    maybe_set("DISCORD_CHANNEL_ID", channel)
    maybe_set("DISCORD_CHANNEL_DEVLOG_ID", devlog)
    maybe_set("DISCORD_CHANNEL_MMRPG_ID", mmrpg)
    maybe_set("DISCORD_CHANNEL_AGENT_MEMORY_ID", agent_memory)
    maybe_set("DISCORD_CHANNEL_AGENT_PROMPT_ID", agent_prompt)
    maybe_set("DISCORD_CHANNEL_AGENT_SCRAPER_ID", agent_scraper)
    maybe_set("DISCORD_CHANNEL_AGENT_CORE_ID", agent_core)

    if not updates:
        typer.echo("[yellow]Nothing to update.[/yellow]")
        raise typer.Exit()

    cli._save_env_config(updates)
    typer.echo("✅ .env updated.")

# Register stubs so `dreamos help` shows placeholders
app.add_typer(convo_app, name="convo")
app.add_typer(chat_app, name="chat")
app.add_typer(tpl_app, name="tpl")
app.add_typer(dev_app, name="dev")
app.add_typer(discord_app, name="discord")

# ---------------------------------------------------------------------------
# MAIN ENTRY
# ---------------------------------------------------------------------------

def main():  # pragma: no cover
    """Entry-point for `python -m tools.dreamos_toolbelt` and console-script."""
    app()

if __name__ == "__main__":
    main() 