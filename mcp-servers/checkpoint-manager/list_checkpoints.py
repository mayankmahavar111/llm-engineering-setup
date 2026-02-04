#!/usr/bin/env python3
"""List all checkpoints from the SQLite database with statistics."""

import sys
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.claude/mcp-servers/checkpoint-manager/checkpoints.db")

def format_timestamp(timestamp_str):
    """Format ISO timestamp to readable format."""
    if not timestamp_str:
        return "Unknown"
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return timestamp_str

def truncate_summary(summary, max_length=150):
    """Truncate summary to max_length with ellipsis."""
    if not summary:
        return "[No summary provided]"
    summary = summary.strip()
    if len(summary) > max_length:
        return summary[:max_length].rstrip() + "..."
    return summary

def list_checkpoints():
    """Query and display all checkpoints from the database."""

    # Check if database exists
    if not os.path.exists(DB_PATH):
        print("=" * 80)
        print("NO CHECKPOINTS FOUND")
        print("=" * 80)
        print()
        print("The checkpoint database is empty.")
        print("Use /checkpoint <name> to create your first checkpoint.")
        return 0

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Query checkpoints with counts of related records
        query = """
        SELECT
            c.*,
            COUNT(DISTINCT t.id) as todo_count,
            COUNT(DISTINCT f.id) as file_count,
            COUNT(DISTINCT d.id) as decision_count,
            COUNT(DISTINCT a.id) as artifact_count
        FROM checkpoints c
        LEFT JOIN todos t ON c.id = t.checkpoint_id
        LEFT JOIN file_modifications f ON c.id = f.checkpoint_id
        LEFT JOIN key_decisions d ON c.id = d.checkpoint_id
        LEFT JOIN artifacts a ON c.id = a.checkpoint_id
        GROUP BY c.id
        ORDER BY c.updated_at DESC
        """

        cursor.execute(query)
        checkpoints = cursor.fetchall()
        conn.close()

        # Handle no checkpoints
        if not checkpoints:
            print("=" * 80)
            print("NO CHECKPOINTS FOUND")
            print("=" * 80)
            print()
            print("The checkpoint database is empty.")
            print("Use /checkpoint <name> to create your first checkpoint.")
            return 0

        # Display header
        print("=" * 80)
        print(f"AVAILABLE CHECKPOINTS ({len(checkpoints)} total)")
        print("=" * 80)
        print()

        # Display each checkpoint
        for idx, checkpoint in enumerate(checkpoints, 1):
            name = checkpoint['name']
            created_at = format_timestamp(checkpoint['created_at'])
            updated_at = format_timestamp(checkpoint['updated_at'])
            summary = truncate_summary(checkpoint['summary'] if checkpoint['summary'] else '')

            todo_count = checkpoint['todo_count']
            file_count = checkpoint['file_count']
            decision_count = checkpoint['decision_count']
            artifact_count = checkpoint['artifact_count']

            # Format output
            print(f"{idx}. {name}")
            print(f"   Updated: {updated_at} | Created: {created_at}")
            print(f"   Summary: {summary}")
            print(f"   Stats: {todo_count} todos, {file_count} files, {decision_count} decisions, {artifact_count} artifacts")
            print()

        # Display footer
        print("=" * 80)
        print()
        print("Use /resume <checkpoint-name> to restore a checkpoint")

        return 0

    except sqlite3.Error as e:
        print(f"Error: Failed to access database - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    exit_code = list_checkpoints()
    sys.exit(exit_code)
