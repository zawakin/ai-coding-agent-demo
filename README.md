# AI Coding Agent

A demonstration of Claude API's agentic capabilities including tool use, parallel execution, and MCP integration.

## Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Anthropic API key

### Installation

```bash
# Clone and install
git clone <your-repo-url>
cd ai-coding-agent
uv sync

# Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Usage

```bash
# Start interactive chat
uv run python -m agent.main chat

# Enable file writing (writes to demo/workspace/ only)
uv run python -m agent.main chat --allow-write

# Work with a specific repository
uv run python -m agent.main chat --repo /path/to/your/repo
```

## Features

**Core Tools:**
- File search (glob patterns)
- Content search (grep)
- File read/write operations
- Memory persistence across sessions
- Task delegation to sub-agents
- Web search with citations

**Safety:**
- Read-only by default
- Ephemeral mode creates temporary copies
- Write operations restricted to workspace directory
- Path traversal protection

## Architecture

```
agent/
  main.py              # CLI entry point
  orchestrator.py      # Claude API communication
  tools/
    registry.py        # Tool definitions
    search.py          # File and content search
    fs.py             # File operations
```

## Configuration

**Models:**
```bash
uv run python -m agent.main chat --model claude-opus-4
```

**Modes:**
```bash
# Safe demo mode (default)
uv run python -m agent.main chat --ephemeral --read-only

# Development mode
uv run python -m agent.main chat --no-ephemeral --allow-write
```

## Documentation

- [Claude Messages API](https://docs.anthropic.com/en/api/messages)
- [Tool Use Guide](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use)
- [MCP Connector](https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector)

## License

MIT
