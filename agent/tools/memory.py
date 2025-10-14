"""Memory tool for persisting agent learnings and important information."""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

MEMORY_FILE = "AGENTS.md"


def definition() -> Dict[str, Any]:
    """Return the tool definition for save_memory."""
    return {
        "name": "save_memory",
        "description": (
            "Save important information, learnings, or decisions to persistent memory. "
            "Use this when you discover key facts about the codebase, user preferences, "
            "project conventions, or other information that should be remembered across sessions. "
            "The content will be appended to AGENTS.md with a timestamp."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The information to save. Be concise but complete. Include context if needed.",
                }
            },
            "required": ["content"],
        },
    }


def run(inputs: Dict[str, Any], root: str) -> List[Dict[str, str]]:
    """
    Save memory content to AGENTS.md in the project root.

    Args:
        inputs: Dictionary with 'content' key
        root: Project root directory path

    Returns:
        List of tool result blocks
    """
    content = inputs["content"]
    memory_path = Path(root) / MEMORY_FILE

    # Format entry with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n## {timestamp}\n\n{content}\n"

    # Append to file (create if doesn't exist)
    with open(memory_path, "a", encoding="utf-8") as f:
        f.write(entry)

    return [
        {
            "type": "text",
            "text": f"(saved {len(content)} bytes to {MEMORY_FILE})",
        }
    ]
