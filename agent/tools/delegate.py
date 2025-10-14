"""Delegate tool for spawning sub-agents to handle specific tasks."""

from typing import Any, Dict, List
import os


def definition() -> Dict[str, Any]:
    """Return the tool definition for delegate_task."""
    return {
        "name": "delegate_task",
        "description": (
            "Delegate a specific task to a sub-agent with read-only access. "
            "Use this when you need to:\n"
            "- Perform independent analysis or research in parallel\n"
            "- Break down complex tasks into smaller subtasks\n"
            "- Isolate exploratory work from main execution\n"
            "The sub-agent has access to all read tools (search, read_file, ask_user) "
            "but cannot modify files. Returns only the final text response."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": (
                        "Clear, specific task description for the sub-agent. "
                        "Be explicit about what information or analysis you need back."
                    ),
                },
                "context": {
                    "type": "string",
                    "description": (
                        "Optional context or constraints for the sub-agent. "
                        "Include relevant background information that isn't in the task description."
                    ),
                },
            },
            "required": ["task"],
        },
    }


def run(inputs: Dict[str, Any], repo_root: str, model: str = "claude-sonnet-4-5") -> List[Dict[str, str]]:
    """
    Execute a delegated task with a new read-only sub-agent.

    Args:
        inputs: Dictionary with 'task' and optional 'context'
        repo_root: Repository root directory
        model: Claude model to use (default: claude-sonnet-4-5)

    Returns:
        List of tool result blocks containing the sub-agent's response
    """
    # Lazy import to avoid circular dependency
    from ..orchestrator import ClaudeOrchestrator
    from .registry import ToolRegistry

    task = inputs["task"]
    context = inputs.get("context", "")

    # Build the full prompt for sub-agent
    if context:
        prompt = f"{context}\n\n{task}"
    else:
        prompt = task

    # Get API key from environment (same as parent agent)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return [
            {
                "type": "text",
                "text": "[Sub-agent error: ANTHROPIC_API_KEY not set]",
            }
        ]

    # Create a read-only sub-agent
    # Note: allow_write=False ensures sub-agent cannot modify files
    tool_registry = ToolRegistry(repo_root=repo_root, allow_write=False, model=model, api_key=api_key)
    sub_agent = ClaudeOrchestrator(
        model=model,
        verbose=False,  # Suppress sub-agent logs to avoid clutter
    )

    try:
        # Execute the delegated task
        result = sub_agent.run_once(prompt, tool_registry)

        # Return the result
        return [
            {
                "type": "text",
                "text": f"[Sub-agent completed task]\n\n{result}",
            }
        ]
    except Exception as e:
        # Handle errors gracefully
        return [
            {
                "type": "text",
                "text": f"[Sub-agent error: {str(e)}]",
            }
        ]
