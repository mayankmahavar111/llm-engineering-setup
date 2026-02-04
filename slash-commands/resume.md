---
description: Resume a previously saved session from checkpoint
argument-hint: <checkpoint-name>
---

I need you to restore session state from a saved checkpoint in the database.

**Checkpoint to load:** $ARGUMENTS

Please perform these steps:

1. **Load the checkpoint from database:**
   - Run: `python3 ~/.claude/mcp-servers/checkpoint-manager/resume_checkpoint.py "$ARGUMENTS"`
   - This retrieves checkpoint data from SQLite database (fast, token-efficient)
   - If checkpoint doesn't exist, list available checkpoints

2. **Parse and internalize the checkpoint data:**
   - Review the summary and understand the context
   - Understand the goals and current state
   - Note any todos that were in progress
   - Review file modifications, decisions, and artifacts

3. **Recreate session state:**
   - Restore the todo list if present using TodoWrite
   - Brief me on what we were working on
   - Highlight any pending tasks or blockers
   - Note the environment context (cwd, git branch if mentioned)
   - Reference key decisions made
   - Mention important artifacts available

4. **Ask for next steps:**
   - Summarize where we left off (2-3 sentences)
   - Ask me: "Ready to continue? What would you like to work on next?"

**Important:** This is a context restoration command. You should internalize all the information from the checkpoint but present me with only a brief, actionable summary. Keep the full checkpoint details in your working memory for our continued conversation.
