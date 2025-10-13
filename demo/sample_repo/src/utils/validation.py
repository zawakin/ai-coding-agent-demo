"""Utility functions for input validation."""

import re


def validate_email(email: str) -> bool:
    """
    Validate an email address format.

    Args:
        email: The email address to validate

    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False

    # Simple email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """
    Validate a username format.

    Args:
        username: The username to validate

    Returns:
        True if valid, False otherwise
    """
    if not username:
        return False

    # Username must be 3-20 characters, alphanumeric and underscore only
    if len(username) < 3 or len(username) > 20:
        return False

    pattern = r'^[a-zA-Z0-9_]+$'
    return bool(re.match(pattern, username))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially harmful characters.

    Args:
        text: The input text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove HTML tags and special characters
    sanitized = re.sub(r'<[^>]+>', '', text)
    sanitized = sanitized.strip()

    return sanitized
