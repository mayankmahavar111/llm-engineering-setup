<!-- 
<meta name="description" content="Open-source AI Engineering Setup: A productivity layer for Claude Code and local LLM agents. Features session persistence, automated code review, and $0 cost local model execution.">
<meta name="keywords" content="AI Engineering, Local LLM Agents, Claude Code, AI Orchestration, Semantic Memory, Developer Productivity, LLM DevOps, Supabase Vector, LM Studio">
-->

# LLM Engineering Setup: AI-Assisted Develoment Environment

**Productivity Layer for Claude Code, Antigravity & Local LLM Agents**

A complete toolkit for AI-assisted software engineering. Automate your workflow with local agents, persistent sessions, and slash commands—running on top of **Claude Code**, **Antigravity**, or **Cursor**.

## 🚀 Key Features

- **Local LLM Agents**: Offload tasks like docs, testing, and reviews to local models (via LM Studio) for **$0 cost**.
- **Session Persistence**: Save and resume context across sessions with the `checkpoint` system. Never re-explain your code.
- **Automated Code Reviews**: 6-aspect PR analysis catching bugs, types, and style issues before merge.
- **Universal Compatibility**: Works with Claude Code, Antigravity, optimized for Mac/Linux.

## 📊 Performance Metrics

| Metric | Result |
|--------|--------|
| **Token Savings** | 80–90% on code gen / docs / tests |
| **Operational Cost** | $0 (using Local LLMs) |
| **Context Retention** | 100% (via Checkpoints) |
| **Dev Lifecycle** | Covers Planning → Coding → Testing → Review → Docs |

## 🛠️ How It Works

**Claude** (or your main AI) handles the high-level reasoning. **Local LLM Agents** handle the execution. A **SQLite-backed Checkpoint System** ensures state is never lost.

Full system architecture and installation guide → [SETUP.md](SETUP.md)

## ⚡ Quick Start

### For Developers (Manual Install)
```bash
git clone https://github.com/mayankmahavar111/llm-engineering-setup.git
cd llm-engineering-setup
bash install.sh
```

### For AI Agents (Universal Setup)
1.  **Open this repo** in your AI Editor.
2.  **Drag and drop** `AGENTS.md` into the chat.
3.  **Say**: "Follow these instructions to set up my environment."

*Requires: Python 3.9+, LM Studio (server on port 1234), `uv`.*

## 📂 Repository Structure

| Folder | Contents |
|--------|----------|
| `slash-commands/` | **Claude Code Slash Commands** for research, docs, and reviews |
| `agents/` | **Local Agent Definitions** for autonomous task execution |
| `mcp-servers/` | **Checkpoint Manager MCP** (SQLite-backed persistence) |
| `scripts/` | Utility scripts for model management and usage logging |
| `generate-your-own/` | Prompt templates to generate custom tools |

## 🔗 Integrations

- **Claude Code**: Native slash command support.
- **Antigravity**: optimized agent tools.
- **LM Studio**: Local model inference server.
- **Supabase**: Vector database integration (optional).

## License

MIT
