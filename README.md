# llm-engineering-setup

A productivity layer for AI-assisted development. Slash commands, local LLM agents, session persistence, and automated code review — all running on top of Claude Code.

## What It Does

- **8 slash commands** that automate your dev workflow (research, docs, reviews, checkpoints)
- **9 agents** that offload code generation, testing, docs, and analysis to local models — at $0 cost
- **Session persistence** — save and resume context across Claude Code sessions. Zero re-explaining.
- **6-aspect PR review** — bugs, tests, errors, types, style, simplification. Catches issues before merge.

## The Numbers

| Metric | Result |
|--------|--------|
| Token savings on code gen / docs / tests | 80–90% |
| Cost of running local agents | $0 |
| Context loss across sessions | 0 |
| Dev lifecycle stages covered | 6 (plan → design → code → test → review → docs) |

## How It Works

Claude handles the thinking. Local LLM agents (via LM Studio) handle the execution. A checkpoint system keeps state across sessions so nothing is ever lost.

Full system map, install guide, and MCP details → [SETUP.md](SETUP.md)

## Quick Start

### For Humans (Manual Install)
```bash
git clone https://github.com/mayankmahavar111/llm-engineering-setup.git
cd llm-engineering-setup
bash install.sh
```

### For AI Agents (Universal Setup)
1.  **Open this repo** in your AI Editor (Antigravity, Cursor, etc.).
2.  **Drag and drop** `AGENTS.md` into the chat.
3.  **Say**: "Follow these instructions to set up my environment."

The AI will detect your environment (Claude vs Antigravity vs Cursor) and configure itself automatically.

Requires: Python 3.9+, LM Studio (port 1234), `uv`.

## What's Inside

| Folder | What |
|--------|------|
| `slash-commands/` | Claude Code slash commands — copy to `~/.claude/commands/` |
| `agents/` | Agent definitions — copy to `~/.claude/agents/` |
| `mcp-servers/` | Checkpoint manager MCP server (SQLite-backed) |
| `scripts/` | Example utility scripts (model manager, usage logger, etc.) |
| `generate-your-own/` | Prompt templates — paste into any AI to generate custom scripts for your setup |

## Not Just Claude Code

The architecture works with any AI coding tool. The prompts, agent logic, and checkpoint concept are tool-agnostic. See the "For AI Tools" section in [SETUP.md](SETUP.md) for how to adapt.

## License

MIT
