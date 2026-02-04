---
description: Save current session state (todos, context, file changes) for later resume
---

I need you to create a checkpoint of the current session state and save it to the database.

**Checkpoint name:** (Ask user for name if not provided, or use 'checkpoint-YYYY-MM-DD-HHMMSS')

Please perform these steps:

1. **Check if checkpoint exists:**
   - Run: `python3 /Users/mayankmahavar/llm-engineering-setup/mcp-servers/checkpoint-manager/resume_checkpoint.py "CHECKPOINT_NAME" 2>/dev/null`
   - If checkpoint exists, retrieve the existing data for merging
   - If checkpoint doesn't exist, start with empty data

2. **Analyze current session context:**
   - Read the current todo list state (from task.md if available)
   - Identify which files have been modified/discussed in recent conversation
   - Determine the current working directory
   - Extract the main user goal/objective from our conversation

3. **Merge with existing checkpoint data (if exists):**
   - **Summary:** Update with new information
   - **Current Goal:** Update if changed
   - **Todos:** Merge old and new todos
   - **File Modifications:** Add new files
   - **Key Decisions:** Add new decisions
   - **Artifacts:** Add new artifacts

4. **Save merged checkpoint to database:**
   - Prepare the JSON payload.
   - Run the checkpoint save script:
     ```bash
     python3 /Users/mayankmahavar/llm-engineering-setup/mcp-servers/checkpoint-manager/save_checkpoint.py <<EOF
     {
       "name": "CHECKPOINT_NAME",
       "summary": "...",
       "current_goal": "...",
       "working_directory": "...",
       "todos": [...],
       "file_modifications": [...],
       "key_decisions": [...],
       "artifacts": [...]
     }
     EOF
     ```
   - Make sure to properly escape the JSON or write it to a temporary file first if it's complex.

5. **Confirm:**
   - Tell me what you saved and where.
