"""Command-line interface for 1inch MCP Server using Typer."""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from inch_mcp_server.database.migrations import (
    run_migrations_sync,
    get_current_revision,
    check_migrations_needed,
    get_alembic_config,
)
from inch_mcp_server.config import settings
from inch_mcp_server.utils.logger_setup import setup_logger

# Initialize CLI app and console
app = typer.Typer(
    name="1inch-mcp",
    help="1inch MCP Server CLI - Database and migration management",
    no_args_is_help=True,
)
console = Console()
logger = setup_logger("cli")

# Database command group
db_app = typer.Typer(name="db", help="Database management commands")
app.add_typer(db_app, name="db")


@db_app.command("migrate")
def migrate(
    revision: Optional[str] = typer.Argument(
        "head",
        help="Target revision (default: head for latest)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose", "-v",
        help="Enable verbose output"
    )
):
    """Run database migrations to the specified revision."""
    try:
        if verbose:
            console.print(f"[blue]Running migrations to revision: {revision}[/blue]")
            console.print(f"[blue]Database URL: {settings.database_url}[/blue]")
        
        run_migrations_sync(revision)
        
        console.print(f"[green]✅ Migrations completed successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Migration failed: {e}[/red]")
        raise typer.Exit(1)


@db_app.command("status")
def status():
    """Check the current migration status."""
    try:
        current_rev = get_current_revision()
        migrations_needed = check_migrations_needed()
        
        # Create a status table
        table = Table(title="Database Migration Status")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Database URL", settings.database_url)
        table.add_row("Current Revision", current_rev or "None")
        table.add_row("Auto-migrate", "Enabled" if settings.auto_migrate else "Disabled")
        table.add_row("Migrations Needed", "Yes" if migrations_needed else "No")
        
        console.print(table)
        
        if migrations_needed:
            console.print("\n[yellow]⚠️  Database migrations are needed. Run 'db migrate' to update.[/yellow]")
        else:
            console.print("\n[green]✅ Database is up to date![/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Failed to check status: {e}[/red]")
        raise typer.Exit(1)


@db_app.command("create-migration")
def create_migration(
    message: str = typer.Argument(..., help="Migration message/description"),
    autogenerate: bool = typer.Option(
        True,
        "--autogenerate/--no-autogenerate",
        help="Enable autogenerate (compare models with database)"
    )
):
    """Create a new migration file."""
    try:
        from alembic import command
        
        config = get_alembic_config()
        
        if autogenerate:
            console.print(f"[blue]Creating migration with autogenerate: {message}[/blue]")
            command.revision(config, message=message, autogenerate=True)
        else:
            console.print(f"[blue]Creating empty migration: {message}[/blue]")
            command.revision(config, message=message)
        
        console.print(f"[green]✅ Migration created successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to create migration: {e}[/red]")
        raise typer.Exit(1)


@db_app.command("init")
def init_db():
    """Initialize Alembic in the project (only needed if alembic/ doesn't exist)."""
    try:
        from alembic import command
        
        project_root = Path.cwd()
        alembic_dir = project_root / "alembic"
        
        if alembic_dir.exists():
            console.print("[yellow]⚠️  Alembic directory already exists![/yellow]")
            return
        
        console.print("[blue]Initializing Alembic...[/blue]")
        config = get_alembic_config()
        command.init(config, str(alembic_dir))
        
        console.print("[green]✅ Alembic initialized successfully![/green]")
        console.print("[yellow]Note: You may need to update the alembic/env.py file for your specific setup.[/yellow]")
        
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize Alembic: {e}[/red]")
        raise typer.Exit(1)


@app.command("version")
def version():
    """Show version information."""
    console.print("[blue]1inch MCP Server CLI[/blue]")
    console.print("Version: 1.0.0")


if __name__ == "__main__":
    app() 