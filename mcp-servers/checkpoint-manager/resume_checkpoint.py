#!/usr/bin/env python3
"""
Resume Checkpoint Viewer
Retrieves and displays checkpoint data from the SQLite database in a
structured format that's easy for Claude to parse.
"""

import sys
import sqlite3
import os
from datetime import datetime
import textwrap

# Determine DB path: Use env var if set, otherwise default to 'checkpoints.db' in the repo root
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "checkpoints.db")
DB_PATH = os.getenv("CHECKPOINT_DB_PATH", DEFAULT_DB_PATH)
SEPARATOR = "=" * 80


def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)


def format_timestamp(timestamp_str):
    """Format timestamp for display."""
    if not timestamp_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return timestamp_str


def wrap_text(text, width=80, initial_indent="", subsequent_indent=""):
    """Wrap text to specified width with proper indentation."""
    if not text:
        return ""
    wrapper = textwrap.TextWrapper(
        width=width,
        initial_indent=initial_indent,
        subsequent_indent=subsequent_indent,
        break_long_words=False,
        break_on_hyphens=False
    )
    return wrapper.fill(text)


def format_todo(todo):
    """Format a single todo item."""
    status = todo['status'] if todo['status'] else 'pending'
    content = todo['content'] if todo['content'] else 'Untitled'

    # Create status indicator
    status_map = {
        'completed': '[✓]',
        'in_progress': '[→]',
        'pending': '[ ]'
    }
    status_indicator = status_map.get(status, f'[{status}]')

    return f"  {status_indicator} {content}"


def format_file_modification(file_mod):
    """Format a single file modification."""
    action = file_mod['modification_type'] if file_mod['modification_type'] else 'modified'
    path = file_mod['file_path'] if file_mod['file_path'] else 'unknown'
    return f"  - {path} ({action})"


def format_decision(idx, decision):
    """Format a single key decision."""
    title = decision['decision_title'] if decision['decision_title'] else 'Untitled Decision'
    content = decision['decision_content'] if decision['decision_content'] else ''

    output = f"  {idx}. {title}\n"

    if content:
        wrapped = wrap_text(content, width=76, subsequent_indent="     ")
        output += f"     {wrapped}\n"

    return output


def format_artifact(idx, artifact):
    """Format a single artifact."""
    name = artifact['artifact_title'] if artifact['artifact_title'] else 'Unnamed'
    artifact_type = artifact['artifact_type'] if artifact['artifact_type'] else 'unknown'
    content = artifact['artifact_content'] if artifact['artifact_content'] else ''

    # Preview first 200 characters
    preview = content[:200] if content else '[No content]'
    if len(content) > 200:
        preview += '...'

    output = f"  {idx}. {name} (type: {artifact_type})\n"
    output += f"     {preview}\n"

    return output


def resume_checkpoint(name):
    """Retrieve and display a checkpoint from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Query checkpoint by name
        cursor.execute(
            "SELECT * FROM checkpoints WHERE name = ? LIMIT 1",
            (name,)
        )
        checkpoint = cursor.fetchone()

        if not checkpoint:
            list_checkpoints()
            print(f"\nCheckpoint '{name}' not found")
            sys.exit(1)

        # Get related data
        cursor.execute(
            "SELECT * FROM todos WHERE checkpoint_id = ? ORDER BY created_at",
            (checkpoint['id'],)
        )
        todos = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM file_modifications WHERE checkpoint_id = ? ORDER BY created_at",
            (checkpoint['id'],)
        )
        files = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM key_decisions WHERE checkpoint_id = ? ORDER BY created_at",
            (checkpoint['id'],)
        )
        decisions = cursor.fetchall()

        cursor.execute(
            "SELECT * FROM artifacts WHERE checkpoint_id = ? ORDER BY created_at",
            (checkpoint['id'],)
        )
        artifacts = cursor.fetchall()

        # Format and display checkpoint
        print(f"\n{SEPARATOR}")
        print(f"CHECKPOINT: {checkpoint['name']}")
        print(SEPARATOR)
        print()

        # Timestamps
        created = format_timestamp(checkpoint['created_at'])
        updated = format_timestamp(checkpoint['updated_at'])
        print(f"CREATED: {created}")
        print(f"UPDATED: {updated}")
        print()

        # Summary
        if checkpoint['summary']:
            print("SUMMARY:")
            summary_text = wrap_text(
                checkpoint['summary'],
                width=76,
                initial_indent="  ",
                subsequent_indent="  "
            )
            print(summary_text)
            print()

        # Current Goal
        if checkpoint['current_goal']:
            print("CURRENT GOAL:")
            goal_text = wrap_text(
                checkpoint['current_goal'],
                width=76,
                initial_indent="  ",
                subsequent_indent="  "
            )
            print(goal_text)
            print()

        # Environment
        if any([checkpoint['working_directory'], checkpoint['git_branch'],
                checkpoint['git_status']]):
            print("ENVIRONMENT:")
            if checkpoint['working_directory']:
                print(f"  Working Directory: {checkpoint['working_directory']}")
            if checkpoint['git_branch']:
                print(f"  Git Branch: {checkpoint['git_branch']}")
            if checkpoint['git_status']:
                print(f"  Git Status: {checkpoint['git_status']}")
            print()

        # Todos
        if todos:
            print(f"TODOS ({len(todos)} total):")
            for todo in todos:
                print(format_todo(todo))
            print()

        # Files Modified
        if files:
            print(f"FILES MODIFIED ({len(files)} total):")
            for file_mod in files:
                print(format_file_modification(file_mod))
            print()

        # Key Decisions
        if decisions:
            print(f"KEY DECISIONS ({len(decisions)} total):")
            for idx, decision in enumerate(decisions, 1):
                print(format_decision(idx, decision), end='')
            print()

        # Artifacts
        if artifacts:
            print(f"ARTIFACTS ({len(artifacts)} total):")
            for idx, artifact in enumerate(artifacts, 1):
                print(format_artifact(idx, artifact), end='')
            print()

        print(SEPARATOR)

    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

    sys.exit(0)


def list_checkpoints():
    """List all available checkpoints."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT id, name, summary, updated_at FROM checkpoints ORDER BY updated_at DESC"
        )
        checkpoints = cursor.fetchall()

        if not checkpoints:
            print("No checkpoints found in database")
            sys.exit(1)

        print("\nAvailable checkpoints:")
        for idx, cp in enumerate(checkpoints, 1):
            updated = format_timestamp(cp['updated_at'])
            summary = cp['summary'] if cp['summary'] else '[No summary]'
            summary_preview = summary[:100]
            if len(summary) > 100:
                summary_preview += '...'

            print(f"  {idx}. {cp['name']} (updated: {updated})")
            print(f"     Summary: {summary_preview}")

    except sqlite3.Error as e:
        print(f"Database error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: resume_checkpoint.py <checkpoint-name>")
        print()
        print("Available checkpoints:")
        list_checkpoints()
        sys.exit(1)

    checkpoint_name = sys.argv[1]
    resume_checkpoint(checkpoint_name)


if __name__ == "__main__":
    main()
