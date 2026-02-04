# llm-engineering-setup — System Blueprint

## What This Is

This is a productivity layer built on top of Claude Code (and compatible with any AI coding tool). It gives you: slash commands that automate workflows, agents that offload heavy work to local LLMs at $0 cost, a checkpoint system that eliminates context loss, and a code review pipeline that runs 6 checks in parallel. The net result: zero wasted time re-explaining context, zero cost on code generation/docs/tests, full lifecycle coverage from planning to review.

## How It All Connects

A simple flow diagram in text/ascii:

```
You type a command or Claude decides to use an agent
        │
        ▼
┌─────────────────┐     ┌──────────────────┐
│  Slash Commands  │     │     Agents       │
│  (orchestrate)   │────▶│  (do the work)   │
└─────────────────┘     └────────┬─────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌──────────────┐        ┌─────────────────┐
          │  LM Studio   │        │  Checkpoint MCP  │
          │ (local LLMs) │        │  (session state) │
          └──────────────┘        └─────────────────┘
```

Slash commands are the entry points. They orchestrate. Agents are the workers — they call LM Studio to do heavy lifting locally. The checkpoint MCP keeps state across sessions.

## MCP Servers

### checkpoint-manager (custom)
- **What:** SQLite-backed MCP server. Saves and restores session state — todos, decisions, file changes, artifacts — across Claude Code sessions.
- **Why:** Claude Code sessions have no memory. Every time context resets, you re-explain everything. This kills that. 292 sessions, zero context lost.
- **How it works:** The /checkpoint command saves state to a local SQLite DB. The /resume command loads it back. The MCP server exposes save/resume/list as tools Claude can call directly.
- **Files:** mcp-servers/checkpoint-manager/

### lmstudio (third-party)
- **What:** Connects Claude Code to a local LM Studio instance via MCP. Gives Claude access to locally-running open-source models.
- **Why:** Code generation, doc writing, test generation, explanations — all of this burns Claude API tokens. Running it locally on a 6-7B model costs $0 and is fast enough for the task.
- **How it works:** Install via `uvx` (see install.sh). LM Studio runs models locally. Agents call `mcp__lmstudio__chat_completion` to use them.
- **Requires:** LM Studio installed + at least one model downloaded. See install.sh for setup.

## Slash Commands

These go in ~/.claude/commands/. Each is a .md file. Claude Code picks them up automatically as /commandname.

| Command | What it does | Why |
|---------|-------------|-----|
| /checkpoint | Saves current session state to SQLite DB | Never lose context again |
| /resume | Loads a saved session — todos, decisions, files, artifacts | Pick up exactly where you left off |
| /list-checkpoints | Lists all saved checkpoints with stats | Find your sessions fast |
| /generate-docs | Claude plans doc structure, local LLM writes it | Docs in seconds, $0 cost |
| /research-and-summarize | Claude searches + extracts, local LLM writes the report | Research without burning tokens |
| /write-blog | Claude outlines, local LLM writes the post | Full articles at zero cost |
| /analyze-url | Firecrawl scrapes, local LLM analyzes | URL analysis without token burn |
| /review-pr | Runs 6 review aspects on changed files (bugs, tests, errors, types, style, simplify) | Catches issues before merge |

## Agents

These go in ~/.claude/agents/. Claude launches them as sub-processes via the Task tool. Each one uses a local LM Studio model to do the heavy work.

| Agent | Model | What it handles | Token savings |
|-------|-------|----------------|---------------|
| code-completion | deepseek-coder-6.7b | Fast completions, boilerplate, snippets | 90% |
| code-generator | deepseek-coder-6.7b | Full implementations from specs | 90% |
| code-reviewer | gemma-3-4b | Bug detection, security, style, performance | 85% |
| code-explainer | llama-3.2-3b | Explains code, adds comments | 85% |
| test-generator | codellama-7b | Unit tests, integration tests, fixtures | 80% |
| doc-generator | gemma-3-4b | API docs, user guides, technical specs | 90% |
| doc-analyzer | gemma-3-4b | Reads + analyzes docs, extracts insights | 85% |
| content-writer | gemma-3-4b | Blog posts, reports, long-form writing | 90% |
| research-processor | gemma-3-4b | Synthesizes research into reports | 85% |

**How agents work:** Claude decides what needs doing and what agent fits. It launches the agent with a spec. The agent reads the code/content, sends it to LM Studio, gets a result, writes it. Claude reviews the output. The expensive thinking stays with Claude. The repetitive generation moves to local models.

## Example Scripts

Generic utility scripts in scripts/. These work out of the box but are also starting points — see generate-your-own/ if you want tailored versions.

| Script | What it does |
|--------|-------------|
| lm-model-manager.sh | Switch models in LM Studio via CLI (current, switch, list) |
| lm-read-file.sh | Feed a file to LM Studio, get a summary back |
| lm-write-file.sh | Give LM Studio a task, it writes the output to a file |
| log-lmstudio-usage.sh | Logs every LM Studio call to SQLite (track your savings) |
| clear-bg-processes.sh | Kills stuck background processes from Claude Code |

## Generate Your Own

The generate-your-own/ folder contains prompt templates. Paste any of them into Claude (or any AI). Fill in your setup details. It generates a custom script for you.

Available prompts:
- **status-line.md** — generates your Claude Code status line (shows context %, tokens, git branch, etc.)
- **model-manager.md** — generates a model switcher for your LLM setup (LM Studio, Ollama, etc.)
- **usage-logger.md** — generates a usage tracker + cost calculator
- **context-backup.md** — generates a lightweight session save/restore system
- **process-cleanup.md** — generates a cleanup script for your AI tool's background processes

## Install

Run once:

```bash
git clone https://github.com/mayankmahavar/llm-engineering-setup.git
cd llm-engineering-setup
bash install.sh
```

That's it. install.sh handles everything: pip deps, directory creation, file copying, DB init, settings.json patching.

**Manual prerequisites** (install.sh will warn if missing):
- Python 3.10+
- LM Studio (https://lmstudio.ai) — installed and running
- At least one model downloaded in LM Studio. Recommended: `deepseek-coder-6.7b-instruct` and `google/gemma-3-4b`
- `uvx` — install with `pip install uv`

After install, restart Claude Code. The new slash commands and agents will be available immediately.

## For AI Tools (Cursor, Windsurf, etc.)

The concepts here are Claude Code-specific in file paths, but the architecture is tool-agnostic:
- **Slash commands** = any tool's custom prompt/macro system
- **Agents** = any tool's sub-agent or task delegation system
- **Checkpoint MCP** = session persistence — adapt the SQLite logic to your tool's extension API
- **LM Studio integration** = any tool can call a local LLM via HTTP. The MCP is just the bridge Claude Code uses.

If you're integrating into a different tool, the slash-commands/ and agents/ folders are your starting point for the prompt logic. The mcp-servers/ folder is the reference implementation for session persistence.
