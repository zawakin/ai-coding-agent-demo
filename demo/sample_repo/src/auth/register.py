"""User registration functionality."""


def register_user(username: str, email: str, password: str) -> dict:
    """
    Register a new user.

    Args:
        username: Desired username
        email: User's email address
        password: User's password

    Returns:
        A dictionary with registration result
    """
    # Validate inputs
    if not username or not email or not password:
        return {
            "success": False,
            "error": "All fields are required"
        }

    if len(password) < 8:
        return {
            "success": False,
            "error": "Password must be at least 8 characters"
        }

    # TODO: Implement actual registration logic
    # - Check if username/email already exists
    # - Hash the password
    # - Store in database

    return {
        "success": True,
        "user_id": f"user_{username}",
        "message": "Registration successful"
    }
