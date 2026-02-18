"""AI Employee Vault CLI entry point."""

import sys
import subprocess
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.ai_employee.services.vault import VaultService
from src.ai_employee.services.logger import DashboardLogger, LogEntry, LogOutcome
from src.ai_employee.models.vault import VaultState, Source

app = typer.Typer(
    name="ai-employee",
    help="AI Employee Vault - Autonomous AI for Obsidian vault automation",
    add_completion=False,
)
console = Console()


def validate_qwen_cli() -> bool:
    """T031: Validate that Qwen CLI is working via `qwen --version` check."""
    try:
        result = subprocess.run(
            ["qwen", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            console.print(f"[green]✓[/green] Qwen CLI detected: {result.stdout.strip()}")
            return True
        else:
            console.print(f"[red]✗[/red] Qwen CLI returned error: {result.stderr}")
            return False
    except FileNotFoundError:
        console.print("[red]✗[/red] Qwen CLI not found. Please install Qwen CLI first.")
        return False
    except subprocess.TimeoutExpired:
        console.print("[red]✗[/red] Qwen CLI check timed out.")
        return False
    except Exception as e:
        console.print(f"[red]✗[/red] Error checking Qwen CLI: {e}")
        return False


def get_vault_path(vault_path: Optional[str]) -> Path:
    """Get vault path from argument or use default."""
    if vault_path:
        return Path(vault_path)
    
    # Default: AI_Employee_Vault in current directory
    default_path = Path.cwd() / "AI_Employee_Vault"
    return default_path


@app.command()
def start(
    vault_path: Optional[str] = typer.Argument(
        None,
        help="Path to AI_Employee_Vault directory (default: ./AI_Employee_Vault)"
    ),
    skip_qwen_check: bool = typer.Option(
        False,
        "--skip-qwen-check",
        help="Skip Qwen CLI validation"
    ),
):
    """
    T026/T030: Start the AI Employee system.
    
    Initializes the vault structure and prepares the system for operation.
    """
    console.print(Panel.fit(
        "[bold blue]AI Employee Vault[/bold blue]\n"
        "Starting autonomous AI employee system...",
        title="Welcome"
    ))
    
    # Validate Qwen CLI unless skipped
    if not skip_qwen_check:
        if not validate_qwen_cli():
            console.print("\n[yellow]Warning:[/yellow] Qwen CLI not available. Some features may not work.")
            console.print("Continuing with limited functionality...\n")
    
    # Get vault path
    vault_path = get_vault_path(vault_path)
    console.print(f"[dim]Vault path: {vault_path}[/dim]\n")
    
    # Initialize vault service
    try:
        vault_service = VaultService(str(vault_path))
        created = vault_service.create_vault_structure()
        
        if created:
            console.print("[green]✓[/green] Vault structure initialized successfully!")
            console.print(f"  - Inbox/: {vault_service.inbox_path}")
            console.print(f"  - Needs_Action/: {vault_service.needs_action_path}")
            console.print(f"  - Done/: {vault_service.done_path}")
            console.print(f"  - Dashboard.md: {vault_path / 'Dashboard.md'}")
            console.print(f"  - Company_Handbook.md: {vault_path / 'Company_Handbook.md'}")
            console.print(f"  - Agent_Skills.md: {vault_path / 'Agent_Skills.md'}")
        
        # Log the startup
        dashboard_logger = DashboardLogger(str(vault_path / "Dashboard.md"))
        log_entry = LogEntry.from_success(
            trigger_event="System Start",
            skill_executed=None,
            file_moved=None,
            duration_ms=0
        )
        dashboard_logger.log_entry(log_entry)
        
        console.print("\n[green]✓[/green] AI Employee system is ready!")
        console.print("\nNext steps:")
        console.print("  1. Run [bold]ai-employee status[/bold] to check system state")
        console.print("  2. Run [bold]ai-employee process <path>[/bold] to process inputs")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error initializing vault: {e}")
        raise typer.Exit(code=1)


@app.command()
def status(
    vault_path: Optional[str] = typer.Argument(
        None,
        help="Path to AI_Employee_Vault directory (default: ./AI_Employee_Vault)"
    ),
):
    """
    T028: Show the current status of the AI Employee system.
    
    Displays vault structure, item counts, and recent activity.
    """
    vault_path = get_vault_path(vault_path)
    
    # Check if vault exists
    if not vault_path.exists():
        console.print(f"[red]✗[/red] Vault not found at: {vault_path}")
        console.print("Run [bold]ai-employee start[/bold] first to initialize the vault.")
        raise typer.Exit(code=1)
    
    console.print(Panel.fit(
        f"[bold blue]AI Employee Status[/bold blue]\n"
        f"Vault: {vault_path}",
        title="System Status"
    ))
    
    try:
        vault_service = VaultService(str(vault_path))
        
        # Count items in each state
        inbox_count = len(vault_service.list_items(VaultState.INBOX))
        needs_action_count = len(vault_service.list_items(VaultState.NEEDS_ACTION))
        done_count = len(vault_service.list_items(VaultState.DONE))
        total_count = inbox_count + needs_action_count + done_count
        
        # Display summary table
        table = Table(title="Vault Statistics")
        table.add_column("State", style="cyan")
        table.add_column("Count", justify="right", style="green")
        
        table.add_row("Inbox", str(inbox_count))
        table.add_row("Needs_Action", str(needs_action_count))
        table.add_row("Done", str(done_count))
        table.add_row("Total", str(total_count), style="bold")
        
        console.print(table)
        
        # Show recent activity
        dashboard_path = vault_path / "Dashboard.md"
        if dashboard_path.exists():
            logger = DashboardLogger(str(dashboard_path))
            recent_logs = logger.get_recent_logs(limit=5)
            
            if recent_logs:
                console.print("\n[bold]Recent Activity:[/bold]")
                for log in recent_logs:
                    timestamp = log.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    outcome_icon = "✓" if log.outcome == LogOutcome.SUCCESS else "✗"
                    console.print(
                        f"  [dim]{timestamp}[/dim] "
                        f"{outcome_icon} {log.trigger_event}"
                    )
            else:
                console.print("\n[yellow]No recent activity logged.[/yellow]")
        
        # Validate vault structure
        console.print("\n[bold]Vault Structure:[/bold]")
        structure_valid = True
        
        for folder_name in ["Inbox", "Needs_Action", "Done"]:
            folder_path = vault_path / folder_name
            if folder_path.exists() and folder_path.is_dir():
                console.print(f"  [green]✓[/green] {folder_name}/")
            else:
                console.print(f"  [red]✗[/red] {folder_name}/ (missing)")
                structure_valid = False
        
        for file_name in ["Dashboard.md", "Company_Handbook.md", "Agent_Skills.md"]:
            file_path = vault_path / file_name
            if file_path.exists():
                console.print(f"  [green]✓[/green] {file_name}")
            else:
                console.print(f"  [red]✗[/red] {file_name} (missing)")
                structure_valid = False
        
        if structure_valid:
            console.print("\n[green]✓[/green] Vault structure is valid!")
        else:
            console.print("\n[yellow]⚠[/yellow] Vault structure is incomplete.")
            console.print("Run [bold]ai-employee start[/bold] to repair.")
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error checking status: {e}")
        raise typer.Exit(code=1)


@app.command()
def process(
    path: str = typer.Argument(
        ...,
        help="Path to input file or directory to process"
    ),
    vault_path: Optional[str] = typer.Option(
        None,
        "--vault", "-v",
        help="Path to AI_Employee_Vault directory (default: ./AI_Employee_Vault)"
    ),
    skill: Optional[str] = typer.Option(
        None,
        "--skill", "-s",
        help="Specific skill to apply (default: auto-detect)"
    ),
):
    """
    T029: Process an input file or directory.
    
    Reads the input, applies appropriate skill, and places in vault.
    """
    vault_path = get_vault_path(vault_path)
    input_path = Path(path)
    
    # Validate input exists
    if not input_path.exists():
        console.print(f"[red]✗[/red] Input not found: {input_path}")
        raise typer.Exit(code=1)
    
    console.print(Panel.fit(
        f"[bold blue]Processing Input[/bold blue]\n"
        f"Path: {input_path}",
        title="AI Employee"
    ))
    
    try:
        vault_service = VaultService(str(vault_path))
        
        # Ensure vault exists
        if not vault_path.exists():
            console.print("[yellow]⚠[/yellow] Vault not found. Initializing...")
            vault_service.create_vault_structure()
        
        dashboard_logger = DashboardLogger(str(vault_path / "Dashboard.md"))
        
        # Process file(s)
        if input_path.is_file():
            # Single file processing
            console.print(f"[dim]Processing file: {input_path.name}[/dim]")
            
            # Read content
            content = input_path.read_text()
            
            # Create vault item
            import hashlib
            item_id = hashlib.sha256(content.encode()).hexdigest()
            
            # Check for duplicates
            if vault_service.item_exists(item_id):
                console.print("[yellow]⚠[/yellow] Duplicate detected. Skipping.")
                log_entry = LogEntry.from_skipped(
                    trigger_event=f"File: {input_path.name}",
                    reason="Duplicate content"
                )
                dashboard_logger.log_entry(log_entry)
            else:
                from src.ai_employee.models.vault import VaultItem
                
                item = VaultItem(
                    id=item_id,
                    title=input_path.stem,
                    source=Source.FILESYSTEM,
                    source_path=str(input_path.absolute()),
                    current_state=VaultState.INBOX,
                    content=content,
                    assigned_skill=skill
                )
                
                # Write to vault
                file_path = vault_service.write_item(item, VaultState.INBOX)
                console.print(f"[green]✓[/green] Processed: {input_path.name}")
                console.print(f"  → {file_path}")
                
                # Log success
                log_entry = LogEntry.from_success(
                    trigger_event=f"File: {input_path.name}",
                    skill_executed=skill or "ProcessFile",
                    file_moved="→ Inbox",
                    duration_ms=0
                )
                dashboard_logger.log_entry(log_entry)
        
        elif input_path.is_dir():
            # Directory processing
            console.print(f"[dim]Processing directory: {input_path}[/dim]")
            
            markdown_files = list(input_path.glob("*.md"))
            if not markdown_files:
                console.print("[yellow]⚠[/yellow] No markdown files found in directory.")
                return
            
            console.print(f"Found {len(markdown_files)} markdown file(s)")
            
            processed_count = 0
            skipped_count = 0
            
            for md_file in markdown_files:
                content = md_file.read_text()
                item_id = hashlib.sha256(content.encode()).hexdigest()
                
                if vault_service.item_exists(item_id):
                    skipped_count += 1
                    continue
                
                item = VaultItem(
                    id=item_id,
                    title=md_file.stem,
                    source=Source.FILESYSTEM,
                    source_path=str(md_file.absolute()),
                    current_state=VaultState.INBOX,
                    content=content,
                    assigned_skill=skill
                )
                
                vault_service.write_item(item, VaultState.INBOX)
                processed_count += 1
            
            console.print(f"\n[green]✓[/green] Processing complete!")
            console.print(f"  Processed: {processed_count} files")
            console.print(f"  Skipped (duplicates): {skipped_count} files")
            
            # Log batch processing
            log_entry = LogEntry.from_success(
                trigger_event=f"Directory: {input_path.name}",
                skill_executed="ProcessFile",
                file_moved=f"→ Inbox ({processed_count} files)",
                duration_ms=0
            )
            dashboard_logger.log_entry(log_entry)
        
    except Exception as e:
        console.print(f"[red]✗[/red] Error processing input: {e}")
        
        # Log error
        try:
            dashboard_logger = DashboardLogger(str(vault_path / "Dashboard.md"))
            log_entry = LogEntry.from_failure(
                trigger_event=f"Process: {path}",
                error_message=str(e)
            )
            dashboard_logger.log_entry(log_entry)
        except Exception:
            pass
        
        raise typer.Exit(code=1)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
