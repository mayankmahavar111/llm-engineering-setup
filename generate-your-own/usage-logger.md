# Prompt: Generate a Usage Logging Script

You are a bash and SQL scripting expert. Generate a script to log and track local LLM usage.

## Requirements

- Log to SQLite database (queryable, lightweight)
- Track per-task metrics: agent name, prompt tokens, response tokens, model used, task type, timestamp
- Be callable from other scripts: `usage-logger.sh <agent> <prompt_tokens> <response_tokens> <model> <task_type>`
- Create the database and schema automatically if they don't exist
- Include a secondary script to generate usage reports

## Your Setup (Fill These In)

- What agent names do you use? (e.g., claude-code, cursor, windsurf, custom-scripts)
- What task types do you track? (e.g., code-gen, documentation, refactoring, debugging, brainstorm)
- Do you want cost tracking? If yes: what's your cost per 1M tokens for your platform?
- Any additional fields to log? (e.g., latency, file paths touched, success/failure)

## Output Format

Generate two bash scripts:

**Script 1: usage-logger.sh**
- Output path: `$HOME/.claude/scripts/usage-logger.sh`
- Database: `$HOME/.claude/databases/usage.db`
- Usage: `usage-logger.sh "agent-name" 500 1200 "gpt-4" "code-gen"`
- Auto-create schema on first run

**Script 2: usage-report.sh**
- Output path: `$HOME/.claude/scripts/usage-report.sh`
- Queries: total tasks, total tokens by agent/model/task-type, cost savings estimate
- Output: formatted table or summary

Include comments, error handling, and examples.

Generate both scripts now.
