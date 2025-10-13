"""Main CLI entry point for the AI Coding Agent."""

import typer
from rich.console import Console
from pathlib import Path
import sys
import tempfile
import shutil
import uuid

from .orchestrator import ClaudeOrchestrator
from .tools.registry import ToolRegistry

app = typer.Typer(
    help="AI Coding Agent - Demo of Claude API with tool use, parallel execution, and MCP integration"
)
console = Console()


def _ephemeral_repo(src: str) -> str:
    """
    Create an ephemeral copy of a repository in a temporary directory.

    This ensures the demo starts from a clean state every time without
    modifying the original repository.

    Args:
        src: Source repository path

    Returns:
        Path to the temporary copy
    """
    tmp = Path(tempfile.gettempdir()) / f"agent-demo-{uuid.uuid4().hex}"
    shutil.copytree(src, tmp, dirs_exist_ok=False)
    return str(tmp)


@app.command()
def chat(
    repo: str = typer.Option(
        "demo/sample_repo",
        "--repo",
        "-r",
        help="Path to the repository to work with"
    ),
    model: str = typer.Option(
        "claude-sonnet-4-5",
        "--model",
        "-m",
        help="Claude model to use"
    ),
    ephemeral: bool = typer.Option(
        True,
        "--ephemeral/--no-ephemeral",
        help="Create a temporary copy of the repo (keeps original clean)"
    ),
    allow_write: bool = typer.Option(
        True,
        "--allow-write/--read-only",
        help="Allow the agent to write/modify files"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed tool execution logs"
    )
):
    """
    Start an interactive chat session with the AI Coding Agent.

    The agent can search files, read code, write files, and ask clarifying questions.
    Type 'exit' or 'quit' to end the session.
    """
    # Validate repository path
    repo_path = Path(repo)
    if not repo_path.exists():
        console.print(f"[red]Error: Repository path does not exist: {repo}[/red]")
        console.print(f"[yellow]Creating directory: {repo}[/yellow]")
        repo_path.mkdir(parents=True, exist_ok=True)

    # Create ephemeral copy if requested
    if ephemeral:
        repo = _ephemeral_repo(str(repo_path))
        repo_path = Path(repo)
        console.print(f"[dim]Ephemeral repo: {repo_path}[/dim]")

    # Initialize the agent
    try:
        tool_registry = ToolRegistry(repo_root=str(repo_path.absolute()), allow_write=allow_write)

        # Log callback for verbose mode
        def log_callback(msg: str):
            console.print(f"[dim]{msg}[/dim]")

        orchestrator = ClaudeOrchestrator(
            model=model,
            verbose=verbose,
            log_callback=log_callback if verbose else None
        )
    except Exception as e:
        console.print(f"[red]Error initializing agent: {e}[/red]")
        sys.exit(1)

    # Welcome message
    console.print("[bold cyan]AI Coding Agent Demo[/bold cyan]")
    console.print(f"Model: [green]{model}[/green]")
    console.print(f"Repository: [green]{repo_path.absolute()}[/green]")
    console.print(f"Mode: [green]{'Ephemeral' if ephemeral else 'Direct'} / {'Read-Write' if allow_write else 'Read-Only'}[/green]")
    if verbose:
        console.print(f"Verbose: [green]Enabled[/green]")
    console.print("\nAvailable tools:")
    console.print("  - [yellow]ask_user[/yellow]: Ask clarifying questions")
    console.print("  - [yellow]search_files[/yellow]: Find files by pattern")
    console.print("  - [yellow]search_in_files[/yellow]: Search for text in files")
    console.print("  - [yellow]read_file[/yellow]: Read file contents")
    console.print("  - [yellow]write_file[/yellow]: Create or modify files")
    console.print("  - [yellow]web_search[/yellow]: Search the web (server tool)")
    console.print("\nType 'exit' or 'quit' to end the session.\n")

    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = console.input("[bold blue]You:[/bold blue] ")

            # Check for exit commands
            if user_input.strip().lower() in {"exit", "quit", "q"}:
                console.print("[yellow]Goodbye![/yellow]")
                break

            # Skip empty input
            if not user_input.strip():
                continue

            # Process the message
            if verbose:
                # In verbose mode, show logs directly without spinner
                console.print("[bold green]Agent:[/bold green]")
                response = orchestrator.run_once(user_input, tool_registry)
            else:
                # In normal mode, show spinner
                with console.status("[bold green]Agent:[/bold green] [dim]Thinking...[/dim]", spinner="dots"):
                    response = orchestrator.run_once(user_input, tool_registry)
                console.print("[bold green]Agent:[/bold green]")

            console.print(response)
            console.print()  # Empty line for readability

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted. Type 'exit' to quit.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def oneshot(
    prompt: str = typer.Argument(..., help="The prompt to send to the agent"),
    repo: str = typer.Option(
        "demo/sample_repo",
        "--repo",
        "-r",
        help="Path to the repository to work with"
    ),
    model: str = typer.Option(
        "claude-sonnet-4-5",
        "--model",
        "-m",
        help="Claude model to use"
    ),
    ephemeral: bool = typer.Option(
        True,
        "--ephemeral/--no-ephemeral",
        help="Create a temporary copy of the repo (keeps original clean)"
    ),
    allow_write: bool = typer.Option(
        True,
        "--allow-write/--read-only",
        help="Allow the agent to write/modify files"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed tool execution logs"
    )
):
    """
    Send a single prompt to the AI Coding Agent and print the response.

    Useful for scripting and automation.
    """
    # Validate repository path
    repo_path = Path(repo)
    if not repo_path.exists():
        console.print(f"[red]Error: Repository path does not exist: {repo}[/red]")
        sys.exit(1)

    # Create ephemeral copy if requested
    if ephemeral:
        repo = _ephemeral_repo(str(repo_path))
        repo_path = Path(repo)
        console.print(f"[dim]Ephemeral repo: {repo_path}[/dim]")

    # Initialize the agent
    try:
        tool_registry = ToolRegistry(repo_root=str(repo_path.absolute()), allow_write=allow_write)

        # Log callback for verbose mode
        def log_callback(msg: str):
            console.print(f"[dim]{msg}[/dim]")

        orchestrator = ClaudeOrchestrator(
            model=model,
            verbose=verbose,
            log_callback=log_callback if verbose else None
        )
    except Exception as e:
        console.print(f"[red]Error initializing agent: {e}[/red]")
        sys.exit(1)

    # Process the prompt
    try:
        response = orchestrator.run_once(prompt, tool_registry)
        console.print(response)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
