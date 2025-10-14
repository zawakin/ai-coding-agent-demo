"""System prompts for the AI Coding Agent."""

from typing import List, Dict
from pathlib import Path


def base_system_prompt(repo_root: str = None) -> List[Dict[str, str]]:
    """
    Returns the base system prompt that instructs Claude to be an AI Coding Agent.
    Includes instructions for parallel tool execution and loaded memory from AGENTS.md.

    Args:
        repo_root: Repository root directory to load AGENTS.md from (optional)

    Returns:
        List of system prompt content blocks
    """
    # Base instructions
    base_text = (
        "You are an AI Coding Agent. "
        "Ask clarifying questions when requirements or constraints are ambiguous. "
        "Before writing code, search the repository for relevant files, read only the minimum needed, "
        "and adhere to existing patterns and conventions.\n\n"
        "<use_parallel_tool_calls>\n"
        "Whenever multiple independent operations are needed, invoke relevant tools in parallel.\n"
        "Err on the side of parallel calls for read-only operations like reading multiple files.\n"
        "</use_parallel_tool_calls>\n\n"
        "<use_memory_tool>\n"
        "Use the save_memory tool to persist important learnings across sessions. Save:\n"
        "- Key facts about the codebase architecture and patterns\n"
        "- User preferences and coding conventions\n"
        "- Important decisions and their rationale\n"
        "- Common pitfalls or gotchas discovered\n"
        "- Project-specific workflows or requirements\n"
        "Be selective: only save information that will be valuable in future sessions.\n"
        "</use_memory_tool>\n\n"
        "<use_delegate_task>\n"
        "Use the delegate_task tool to spawn sub-agents for independent subtasks. Delegate when:\n"
        "- Performing parallel analysis or research across different areas\n"
        "- Breaking down complex tasks into focused subtasks\n"
        "- Isolating exploratory work that doesn't affect the main task\n"
        "Sub-agents are read-only and have access to search/read tools. "
        "Provide clear, specific task descriptions and relevant context. "
        "Use parallel delegation for independent tasks to improve efficiency.\n"
        "</use_delegate_task>"
    )

    # Load memory from AGENTS.md if available
    memory_text = ""
    if repo_root:
        memory_path = Path(repo_root) / "AGENTS.md"
        if memory_path.exists():
            try:
                memory_content = memory_path.read_text(encoding="utf-8")
                if memory_content.strip():
                    memory_text = (
                        "\n\n<agent_memory>\n"
                        "The following contains learnings and important information from previous sessions:\n\n"
                        f"{memory_content}\n"
                        "</agent_memory>"
                    )
            except Exception:
                # Silently ignore errors reading memory file
                pass

    return [
        {
            "type": "text",
            "text": base_text + memory_text,
        }
    ]
