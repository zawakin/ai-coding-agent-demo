"""Claude API Orchestrator - handles communication with Claude and tool execution."""

from typing import Any, Dict, List
from anthropic import Anthropic
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# API version
ANTHROPIC_VERSION = "2023-06-01"


class ClaudeOrchestrator:
    """
    Orchestrates communication between the user, Claude API, and tool execution.
    Manages conversation history and handles the tool use loop.
    """

    def __init__(self, model: str = "claude-sonnet-4-5", verbose: bool = False, log_callback=None):
        """
        Initialize the orchestrator.

        Args:
            model: The Claude model to use (default: claude-sonnet-4-5)
            verbose: Enable verbose logging of tool execution (default: False)
            log_callback: Optional callback function for logging (receives message string)
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.history: List[Dict[str, Any]] = []
        self.verbose = verbose
        self.log_callback = log_callback

    def _log(self, message: str):
        """Log a message if verbose mode is enabled."""
        if self.verbose and self.log_callback:
            self.log_callback(message)

    def run_once(self, user_text: str, tool_registry) -> str:
        """
        Process a single user message and return Claude's response.
        Handles the complete tool use loop if tools are invoked (multi-turn).

        Args:
            user_text: The user's input message
            tool_registry: The ToolRegistry instance for tool definitions and execution

        Returns:
            Claude's text response
        """
        # Add user message to history
        self.history.append({"role": "user", "content": user_text})

        # Prepare request parameters
        tools = tool_registry.client_tools_schema() + tool_registry.server_tools_schema()
        mcp_servers = tool_registry.mcp_servers_config()
        beta_headers = tool_registry.beta_headers()

        # Build extra headers if needed
        extra_headers = {}
        if beta_headers:
            extra_headers["anthropic-beta"] = ",".join(beta_headers)

        # Tool use loop: continue until no more tool_use blocks are returned
        turn_count = 0
        max_turns = 10  # Safety limit to prevent infinite loops

        while turn_count < max_turns:
            turn_count += 1
            self._log(f"📤 Sending request to Claude (turn {turn_count})...")

            # Prepare API request
            request_params = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": self.history,
                "system": tool_registry.system_prompt(),
                "tools": tools,
                "tool_choice": {"type": "auto", "disable_parallel_tool_use": False},
            }

            # Add MCP servers if configured
            if mcp_servers:
                request_params["mcp_servers"] = mcp_servers

            # Make API call
            if extra_headers:
                response = self.client.messages.create(
                    **request_params,
                    extra_headers=extra_headers
                )
            else:
                response = self.client.messages.create(**request_params)

            # Check if Claude wants to use tools
            tool_uses = [block for block in response.content if getattr(block, "type", None) == "tool_use"]

            # Add assistant's response to history
            self.history.append({"role": "assistant", "content": response.content})

            if not tool_uses:
                # No more tools to use, return final response
                return self._extract_text(response.content)

            # Execute all tool calls and collect results
            results_content: List[Dict[str, Any]] = []
            self._log(f"🔧 Executing {len(tool_uses)} tool(s)...")

            for tool_use in tool_uses:
                tool_name = tool_use.name
                tool_inputs = tool_use.input
                tool_use_id = tool_use.id

                # Log tool execution
                input_preview = str(tool_inputs)[:100]
                if len(str(tool_inputs)) > 100:
                    input_preview += "..."
                self._log(f"  ├─ {tool_name}: {input_preview}")

                # Execute the tool
                tool_result_blocks = tool_registry.execute(tool_name, tool_inputs, tool_use_id)
                results_content.extend(tool_result_blocks)

            # Add tool results as a single user message
            # This format is required: tool_result blocks must be in a user message
            self.history.append({"role": "user", "content": results_content})

            # Loop continues - Claude may want to use more tools

        # Safety fallback: if we hit max turns, return the last response
        self._log(f"⚠️  Reached maximum turns ({max_turns}), returning last response")
        return self._extract_text(self.history[-1]["content"]) if self.history[-1]["role"] == "assistant" else "(no response)"

    def _extract_text(self, content: List[Any]) -> str:
        """
        Extract text content from Claude's response content blocks.

        Args:
            content: List of content blocks from Claude's response

        Returns:
            Concatenated text from all text blocks
        """
        text_parts = []
        for block in content:
            if getattr(block, "type", None) == "text":
                text_parts.append(block.text)
        return "".join(text_parts)

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history.

        Returns:
            List of message dictionaries
        """
        return self.history

    def clear_history(self):
        """Clear the conversation history."""
        self.history = []
