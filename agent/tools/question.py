"""Question API - allows the agent to ask the user for clarification."""

from typing import Dict, List, Any


def definition() -> Dict[str, Any]:
    """
    Returns the JSON Schema definition for the ask_user tool.
    """
    return {
        "name": "ask_user",
        "description": (
            "Ask the end-user a clarifying question when requirements are missing or ambiguous. "
            "Use sparingly and ask one or two crisp questions at a time."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "One concise question to the user"
                }
            },
            "required": ["question"]
        }
    }


def run(inputs: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Execute the ask_user tool.

    In this demo, we simply return the question text with a special marker.
    In a real implementation, this would pause execution and wait for user input.

    Args:
        inputs: Dictionary containing the 'question' field

    Returns:
        List of content blocks to return to Claude
    """
    question = inputs.get("question", "")
    return [
        {
            "type": "text",
            "text": f"[QUESTION_TO_USER] {question}"
        }
    ]
