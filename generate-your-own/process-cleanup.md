# Prompt: Generate a Process Cleanup Script

You are a bash scripting expert. Generate a safe cleanup script for orphaned background processes from AI tools.

## Requirements

- Identify and kill only processes belonging to AI tools (never system processes)
- Target orphaned/hung processes that have been running too long
- Clean stale cache files from AI tools
- Include dry-run mode (show what would be killed, don't actually kill)
- Be conservative and safe — human review recommended before executing

## Your Setup (Fill These In)

- Which AI tools do you use? (Check all that apply)
  - Claude Code
  - Cursor
  - Windsurf
  - Custom scripts
  - Others?

- What should the script clean?
  - Orphaned child processes of these tools (stuck longer than N minutes)
  - Stale node/python processes
  - Temporary cache files (where do they live? ~/.cache/claude/, ~/.cursor/, etc.)
  - Log files older than X days
  - Anything else?

- Process timeout: How long should a process run before being considered "stuck"? (e.g., 30 minutes)
- Dry-run: Should the script default to dry-run mode, or require a `--force` flag to actually kill?

## Output Format

Generate a bash script:
- Output path: `$HOME/.claude/scripts/process-cleanup.sh`
- Usage: `process-cleanup.sh --dry-run` (show what would be cleaned)
- Usage: `process-cleanup.sh --force` (actually clean)
- List processes and files before/after
- Log actions to a file: `$HOME/.claude/logs/cleanup.log`
- Include comments and safety warnings

The example in this repo (`scripts/clear-bg-processes.sh`) is a reference — adapt for your tools.

Generate this script now.
