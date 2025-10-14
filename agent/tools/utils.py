"""Utility functions for tool implementations."""

import os
from pathlib import Path


# Write operations are restricted to this directory
# Can be overridden with AGENT_WRITE_ROOT environment variable
ALLOWED_WRITE_ROOT = Path(
    os.getenv("AGENT_WRITE_ROOT", "demo/workspace")
).resolve()


def safe_join(root: str, rel_path: str) -> Path:
    """
    Safely join a root directory with a relative path, preventing path traversal.

    Args:
        root: The root directory
        rel_path: The relative path to join

    Returns:
        The resolved absolute path

    Raises:
        ValueError: If the path would escape the root directory
    """
    root_path = Path(root).resolve()
    target_path = (root_path / rel_path).resolve()

    if not str(target_path).startswith(str(root_path)):
        raise ValueError(f"Path traversal detected: {rel_path}")

    return target_path


def ensure_writable(path: Path) -> None:
    """
    Verify that a path is within the allowed write root.

    This provides an additional safety layer for write operations.
    Only paths under ALLOWED_WRITE_ROOT (default: demo/workspace) can be written.

    Args:
        path: The path to check

    Raises:
        ValueError: If the path is outside the allowed write root
    """
    path_resolved = path.resolve()

    # If ALLOWED_WRITE_ROOT doesn't exist, create it
    if not ALLOWED_WRITE_ROOT.exists():
        ALLOWED_WRITE_ROOT.mkdir(parents=True, exist_ok=True)

    if not str(path_resolved).startswith(str(ALLOWED_WRITE_ROOT)):
        raise ValueError(
            f"Write blocked: path outside workspace\n"
            f"  Attempted: {path_resolved}\n"
            f"  Allowed: {ALLOWED_WRITE_ROOT}\n"
            f"  (Set AGENT_WRITE_ROOT env var to change)"
        )


def is_text_file(file_path: Path, max_size: int = 2_000_000) -> bool:
    """
    Check if a file is likely a text file and not too large.

    Args:
        file_path: Path to the file
        max_size: Maximum file size in bytes (default: 2MB)

    Returns:
        True if the file appears to be a readable text file
    """
    if not file_path.exists() or file_path.is_dir():
        return False

    if file_path.stat().st_size > max_size:
        return False

    # Check for common binary file extensions
    binary_extensions = {
        '.pyc', '.pyo', '.so', '.dylib', '.dll', '.exe',
        '.bin', '.dat', '.db', '.sqlite', '.jpg', '.jpeg',
        '.png', '.gif', '.bmp', '.ico', '.pdf', '.zip',
        '.tar', '.gz', '.bz2', '.xz', '.7z', '.rar',
    }

    if file_path.suffix.lower() in binary_extensions:
        return False

    return True
