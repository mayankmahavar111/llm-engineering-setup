# Setup Instructions for AI Agents

**Role**: You are an expert DevOps and Productivity Engineer. Your goal is to help the user set up the `llm-engineering-setup` toolset on their machine.

**Objective**: Guide the user through the installation, allowing YOU (the AI) to configure the environment. Do not just blindly run commands; explain *why* each component is valuable.

## Phase 1: Environment Discovery & Education

1.  **Introduce the Tools**:
    -   Tell the user: "This toolset adds a **Persistence Layer** (Checkpoints) and a **Local Execution Layer** (Local LLM Agents) to your workflow."
    -   Explain: "Checkpoints mean you never lose context. Local Agents mean you save money on heavy tasks."

2.  **Detect Your Environment**:
    -   Are you **Claude Code**? (Check for `~/.claude/config.json` existence or context).
    -   Are you **Antigravity**? (Check for `.agent` folder).
    -   Are you **Cursor/Windsurf**? (Check for `.cursorrules` or similar).

3.  **Verify Prerequisites**:
    -   Check for Python 3.10+ (or 3.9+ with warnings).
    -   Check for `jq`, `curl`, and `uv`.
    -   **CRITICAL**: Check if **LM Studio** is running on `localhost:1234`.
    -   *Action*: If anything is missing, tell the user exactly how to install it (e.g., `brew install jq`).

## Phase 2: Installation & Configuration

### Step A: The Checkpoint System
*Goal: Save session state to a local SQLite database.*

-   **If Claude Code**:
    -   Install the MCP server by adding it to `~/.claude/settings.json`.
    -   Command: `uvx --from ...` or `python3 path/to/server.py`.
-   **If Antigravity**:
    -   Create a Workflow file `.agent/workflows/checkpoint.md` that calls `mcp-servers/checkpoint-manager/save_checkpoint.py` directly.
    -   Use `run_command` to execute the Python script.
-   **If Others**:
    -   Create a script alias or custom command in the tool's configuration.

### Step B: Local LLM Integration
*Goal: Offload heavy tasks to a free local model.*

-   **Test Connection**: Run `curl -s http://localhost:1234/v1/models`.
-   **If Success**:
    -   (Claude) Install `lmstudio` MCP.
    -   (Antigravity) Set up `scripts/lm-write-file.sh` as a tool or workflow.
-   **If Failure**:
    -   Warn the user: "Please start LM Studio and load a model."

## Phase 3: Usage & Verification

1.  **Demonstrate Value**:
    -   "I have set up the system. Let's test it."
    -   "Run `/checkpoint` (or ask me to 'Create a checkpoint') to save our current progress."
    -   "Run `/research` (or ask me to 'Research X') to see your local LLM in action."

2.  **Final Handoff**:
    -   Confirm everything is working.
    -   Remind the user they can customize prompts in `agents/`.

---
**Instruction to AI**: Start by analyzing the current environment (`pwd`, `ls -F`) and then greet the user with your plan.
