"""Utility functions for tool implementations."""

import os
from pathlib import Path


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
