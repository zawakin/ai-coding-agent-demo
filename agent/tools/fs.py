"""File System API - read and write files safely within the repository."""

from typing import Dict, List, Any
from .utils import safe_join, ensure_writable


def read_file_definition() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the read_file tool.
    """
    return {
        "name": "read_file",
        "description": (
            "Read a single text file (UTF-8). Use after search to inspect implementation details. "
            "Do not read large/binary files; read only the minimum needed for the task."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from repository root"
                }
            },
            "required": ["path"]
        }
    }


def write_file_definition() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the write_file tool.
    """
    return {
        "name": "write_file",
        "description": (
            "Create or overwrite a small text file (UTF-8). "
            "Keep changes minimal and follow existing patterns."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path from repository root"
                },
                "content": {
                    "type": "string",
                    "description": "Full content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    }


def run_read_file(inputs: Dict[str, Any], root: str) -> List[Dict[str, str]]:
    """
    Execute the read_file tool to read a file's contents.

    Args:
        inputs: Dictionary containing 'path'
        root: Root directory of the repository

    Returns:
        List of content blocks with the file contents or error message
    """
    try:
        path = safe_join(root, inputs["path"])

        if not path.exists():
            return [{"type": "text", "text": f"(file not found: {inputs['path']})"}]

        if path.is_dir():
            return [{"type": "text", "text": f"(path is a directory: {inputs['path']})"}]

        # Read the file
        content = path.read_text(encoding="utf-8", errors="ignore")

        # For very large files, consider truncating
        max_size = 100_000  # ~100KB of text
        if len(content) > max_size:
            content = content[:max_size] + f"\n\n... (truncated, file is too large)"

        return [{"type": "text", "text": content}]

    except ValueError as e:
        # Path traversal or other security issue
        return [{"type": "text", "text": f"(error: {str(e)})"}]
    except Exception as e:
        return [{"type": "text", "text": f"(error reading file: {str(e)})"}]


def run_write_file(inputs: Dict[str, Any], root: str) -> List[Dict[str, str]]:
    """
    Execute the write_file tool to create or overwrite a file.

    Args:
        inputs: Dictionary containing 'path' and 'content'
        root: Root directory of the repository

    Returns:
        List of content blocks with success message or error
    """
    try:
        path = safe_join(root, inputs["path"])
        content = inputs["content"]

        # Verify path is within allowed write root
        ensure_writable(path)

        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)

        # Write the file
        path.write_text(content, encoding="utf-8")

        return [{"type": "text", "text": f"(successfully wrote {len(content)} bytes to {inputs['path']})"}]

    except ValueError as e:
        # Path traversal or other security issue
        return [{"type": "text", "text": f"(error: {str(e)})"}]
    except Exception as e:
        return [{"type": "text", "text": f"(error writing file: {str(e)})"}]
