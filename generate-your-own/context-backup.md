# Prompt: Generate Context Save/Restore Scripts

You are a bash and file system scripting expert. Generate a session checkpointing system for AI coding work.

## Requirements

- **save-context.sh**: Snapshot current session state
- **restore-context.sh**: Load a previously saved session
- Store checkpoints in a retrievable format
- Include user-provided notes/summary of what they're working on
- Fast and non-intrusive

## Your Setup (Fill These In)

- Storage format preference?
  - JSON files (simpler, human-readable, one file per session)
  - SQLite (more queryable, better for many sessions)
  - Git branch snapshots (if you use branches for context switching)

- What session state should be captured?
  - List of open files (paths)
  - Modified files (git diff, or just filenames?)
  - Current git branch
  - User-provided summary/notes
  - Environment variables or configs
  - Anything else?

- Where should checkpoints be stored? (default: `$HOME/.claude/checkpoints/`)
- Should restore auto-apply the git branch, or just print it?

## Output Format

Generate two bash scripts:

**Script 1: save-context.sh**
- Usage: `save-context.sh "session-name"` or `save-context.sh` (interactive)
- Prompts user for a summary, captures file state, saves checkpoint
- Output: confirmation message with session ID

**Script 2: restore-context.sh**
- Usage: `restore-context.sh "session-name"`
- Outputs or applies the saved session state
- Option to list all saved sessions

Include comments, error handling, and examples for both scripts.

The checkpoint-manager MCP in this repo shows a full version of this concept — these scripts are simpler alternatives.

Generate both scripts now.
