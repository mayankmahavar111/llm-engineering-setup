---
description: Save current session state (todos, context, file changes) for later resume
argument-hint: [checkpoint-name]
---

I need you to create a checkpoint of the current session state and save it to the database.

**Checkpoint name:** $ARGUMENTS

Please perform these steps:

1. **Check if checkpoint exists:**
   - Run: `python3 ~/.claude/mcp-servers/checkpoint-manager/resume_checkpoint.py "$ARGUMENTS" 2>/dev/null`
   - If checkpoint exists, retrieve the existing data for merging
   - If checkpoint doesn't exist, start with empty data

2. **Analyze current session context:**
   - Read the current todo list state
   - Identify which files have been modified/discussed in recent conversation
   - Determine the current working directory and git state (if applicable)
   - Extract the main user goal/objective from our conversation

3. **Merge with existing checkpoint data (if exists):**
   - **Summary:** Update with new information, keep context from old summary
   - **Current Goal:** Update if changed, otherwise keep existing
   - **Todos:** Merge old and new todos (update status, add new ones, keep completed)
   - **File Modifications:** Add new files to the existing list (no duplicates)
   - **Key Decisions:** Add new decisions to existing ones
   - **Artifacts:** Add new artifacts to existing ones
   - **Working Directory/Git State:** Update with current values

4. **Generate merged checkpoint data:**
   - Create a concise summary combining old context with new progress (2-3 paragraphs max)
   - Merge todos: Keep all existing todos + add new ones
   - Merge files: Keep all existing files + add new ones
   - Merge decisions: Keep all existing decisions + add new ones
   - Merge artifacts: Keep all existing artifacts + add new ones

5. **Save merged checkpoint to database:**
   - Run the checkpoint save script: `python3 ~/.claude/mcp-servers/checkpoint-manager/save_checkpoint.py`
   - Pass the MERGED checkpoint data as JSON via stdin
   - The script will save to SQLite database for fast, token-efficient retrieval
   - Format:
     ```json
     {
       "name": "$ARGUMENTS",
       "summary": "...",
       "current_goal": "...",
       "working_directory": "...",
       "git_branch": "...",
       "git_status": "...",
       "todos": [{"content": "...", "status": "...", "active_form": "..."}],
       "file_modifications": [{"file_path": "...", "modification_type": "created|modified|deleted"}],
       "key_decisions": [{"decision_title": "...", "decision_content": "..."}],
       "artifacts": [{"artifact_title": "...", "artifact_content": "...", "artifact_type": "..."}]
     }
     ```

6. **Confirm:**
   - Tell me what you saved and where
   - Indicate if this was a new checkpoint or an update to existing
   - Give me a brief summary of what's captured (including merged data)
   - Show checkpoint ID/name for easy resume

If no checkpoint name is provided, use timestamp: `checkpoint-YYYY-MM-DD-HHMMSS`
