"""Search API - glob-based file search and grep-based content search."""

import glob
import os
from typing import Dict, List, Any
from .utils import is_text_file
from pathlib import Path


def search_files_definition() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the search_files tool.
    """
    return {
        "name": "search_files",
        "description": (
            "List files by glob-style pattern relative to the repository root. "
            "Use to discover modules by name. Returns up to 200 matches."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern like 'src/**/auth*.ts' or '**/*.py'"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "minimum": 1,
                    "maximum": 200
                }
            },
            "required": ["pattern"]
        }
    }


def search_in_files_definition() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the search_in_files tool.
    """
    return {
        "name": "search_in_files",
        "description": (
            "Grep-like textual search across files. Use to locate definitions, API usage, or TODOs. "
            "Avoid huge binary files. Provide small 'paths' to narrow scope when possible."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "The text to search for"
                },
                "paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of glob patterns to search within (e.g., ['src/**/*.py'])"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of matches to return",
                    "minimum": 1,
                    "maximum": 200
                }
            },
            "required": ["keyword"]
        }
    }


def run_search_files(inputs: Dict[str, Any], root: str) -> List[Dict[str, str]]:
    """
    Execute the search_files tool to find files matching a glob pattern.

    Args:
        inputs: Dictionary containing 'pattern' and optional 'limit'
        root: Root directory to search from

    Returns:
        List of content blocks with matching file paths
    """
    pattern = inputs["pattern"]
    limit = int(inputs.get("limit", 100))

    # Use glob to find matching files
    search_pattern = os.path.join(root, pattern)
    matches = sorted(glob.glob(search_pattern, recursive=True))

    # Convert to relative paths and limit results
    rel_paths = [os.path.relpath(p, root) for p in matches[:limit]]

    if not rel_paths:
        result_text = "(no matches found)"
    else:
        result_text = "\n".join(rel_paths)
        if len(matches) > limit:
            result_text += f"\n\n(showing {limit} of {len(matches)} matches)"

    return [{"type": "text", "text": result_text}]


def run_search_in_files(inputs: Dict[str, Any], root: str) -> List[Dict[str, str]]:
    """
    Execute the search_in_files tool to search for text within files.

    Args:
        inputs: Dictionary containing 'keyword', optional 'paths', and optional 'limit'
        root: Root directory to search from

    Returns:
        List of content blocks with matching lines
    """
    keyword = inputs["keyword"]
    paths = inputs.get("paths") or ["**/*"]
    limit = int(inputs.get("limit", 80))

    results = []
    count = 0

    try:
        for pattern in paths:
            search_pattern = os.path.join(root, pattern)
            for file_path in glob.glob(search_pattern, recursive=True):
                path = Path(file_path)

                # Skip directories and binary files
                if not is_text_file(path):
                    continue

                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        for line_num, line in enumerate(f, 1):
                            if keyword in line:
                                rel_path = os.path.relpath(file_path, root)
                                results.append(f"{rel_path}:{line_num}:{line.rstrip()}")
                                count += 1
                                if count >= limit:
                                    raise StopIteration
                except (IOError, OSError):
                    # Skip files that can't be read
                    continue
    except StopIteration:
        pass

    if not results:
        result_text = "(no matches found)"
    else:
        result_text = "\n".join(results)
        if count >= limit:
            result_text += f"\n\n(limited to {limit} matches)"

    return [{"type": "text", "text": result_text}]
