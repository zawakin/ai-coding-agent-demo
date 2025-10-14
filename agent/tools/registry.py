"""Tool Registry - central registry for all tools available to the agent."""

from typing import Any, Dict, List
import os
from . import question, search, fs, memory, delegate
from ..system_prompts import base_system_prompt


class ToolRegistry:
    """
    Central registry for all tools available to the AI Coding Agent.
    Handles tool definition, execution dispatch, and configuration.
    """

    def __init__(self, repo_root: str, allow_write: bool = True, model: str = "claude-sonnet-4-5", api_key: str = ""):
        """
        Initialize the tool registry.

        Args:
            repo_root: Root directory of the repository to work with
            allow_write: Whether to allow file write operations (default: True)
            model: Claude model to use for delegate tasks (default: claude-sonnet-4-5)
            api_key: Anthropic API key for delegate tasks
        """
        self.repo_root = repo_root
        self.allow_write = allow_write
        self.model = model
        self.api_key = api_key

    def client_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Returns the list of client-side tool definitions.
        These are tools that are executed locally by this agent.

        Returns:
            List of tool definition dictionaries in Claude's JSON Schema format
        """
        tools = [
            question.definition(),
            search.search_files_definition(),
            search.search_in_files_definition(),
            fs.read_file_definition(),
            memory.definition(),  # Always available for learning
            delegate.definition(),  # Always available for task delegation
        ]

        # Only include write_file tool if write operations are allowed
        if self.allow_write:
            tools.append(fs.write_file_definition())

        return tools

    def server_tools_schema(self) -> List[Dict[str, Any]]:
        """
        Returns the list of server-side tool definitions.
        These are tools that are executed by Anthropic's servers.

        Currently includes:
        - web_search_20250305: Web search with automatic citations

        Note: Server tools require organization-level enablement.

        Returns:
            List of server tool definition dictionaries
        """
        # Web search tool (requires organization enablement)
        return [
            {
                "type": "web_search_20250305",
                "name": "web_search",
                "max_uses": 3
            }
        ]

    def mcp_servers_config(self) -> List[Dict[str, Any]] | None:
        """
        Returns the MCP (Model Context Protocol) server configuration.
        This allows the agent to connect to external MCP servers via HTTP/SSE.

        Note: Requires the beta header 'anthropic-beta: mcp-client-2025-04-04'

        Returns:
            List of MCP server configurations, or None if not configured
        """
        # Example: Load from environment variables
        mcp_url = os.getenv("MY_MCP_URL")
        mcp_token = os.getenv("MY_MCP_BEARER")

        if not mcp_url:
            return None

        return [
            {
                "type": "url",
                "url": mcp_url,
                "name": "example-mcp",
                "authorization_token": mcp_token
            }
        ]

    def beta_headers(self) -> List[str]:
        """
        Returns the list of beta feature headers required for the current configuration.

        Returns:
            List of beta header values
        """
        headers = []

        # MCP connector requires beta header
        if self.mcp_servers_config():
            headers.append("mcp-client-2025-04-04")

        return headers

    def system_prompt(self) -> List[Dict[str, str]]:
        """
        Returns the system prompt for the agent.
        Includes loaded memory from AGENTS.md if available.

        Returns:
            System prompt in Claude's format
        """
        return base_system_prompt(repo_root=self.repo_root)

    def execute(self, name: str, inputs: Dict[str, Any], tool_use_id: str) -> List[Dict[str, Any]]:
        """
        Execute a tool by name and return the result in Claude's tool_result format.

        Args:
            name: Name of the tool to execute
            inputs: Input parameters for the tool
            tool_use_id: Unique ID for this tool invocation (from Claude)

        Returns:
            List of content blocks formatted as tool_result
        """
        # Dispatch to the appropriate tool implementation
        if name == "ask_user":
            content = question.run(inputs)
        elif name == "search_files":
            content = search.run_search_files(inputs, self.repo_root)
        elif name == "search_in_files":
            content = search.run_search_in_files(inputs, self.repo_root)
        elif name == "read_file":
            content = fs.run_read_file(inputs, self.repo_root)
        elif name == "write_file":
            content = fs.run_write_file(inputs, self.repo_root)
        elif name == "save_memory":
            content = memory.run(inputs, self.repo_root)
        elif name == "delegate_task":
            content = delegate.run(inputs, self.repo_root, self.model)
        else:
            # Unknown tool
            content = [{"type": "text", "text": f"Unknown tool: {name}"}]

        # Return in tool_result format
        return [
            {
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": content
            }
        ]
