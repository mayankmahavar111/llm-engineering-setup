#!/usr/bin/env python3
"""
Save Checkpoint Script
Reads checkpoint JSON from stdin and saves to SQLite database.
Mirrors the logic of the MCP server's save_checkpoint method.
"""

import sys
import json
import sqlite3
import os
from datetime import datetime

# Determine DB path: Use env var if set, otherwise default to 'checkpoints.db' in the repo root
# This allows the script to work anywhere without hardcoding.
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "checkpoints.db")
DB_PATH = os.getenv("CHECKPOINT_DB_PATH", DEFAULT_DB_PATH)


def init_db():
    """Initialize database schema if it doesn't exist"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Create checkpoints table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkpoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    summary TEXT,
                    current_goal TEXT,
                    working_directory TEXT,
                    git_branch TEXT,
                    git_status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create todos table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkpoint_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    active_form TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed')),
                    order_index INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
                )
            """)

            # Create file_modifications table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_modifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkpoint_id INTEGER NOT NULL,
                    file_path TEXT NOT NULL,
                    modification_type TEXT NOT NULL CHECK(modification_type IN ('created', 'modified', 'deleted')),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
                )
            """)

            # Create key_decisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS key_decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkpoint_id INTEGER NOT NULL,
                    decision_title TEXT NOT NULL,
                    decision_content TEXT,
                    order_index INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
                )
            """)

            # Create artifacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    checkpoint_id INTEGER NOT NULL,
                    artifact_title TEXT NOT NULL,
                    artifact_content TEXT,
                    artifact_type TEXT,
                    order_index INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
                )
            """)

            conn.commit()
    except sqlite3.Error as e:
        raise RuntimeError(f"Database initialization error: {e}")


def save_checkpoint(data):
    """
    Save or update a checkpoint with all related data.

    Args:
        data: Dictionary containing checkpoint information
              Must include 'name' field

    Returns:
        None (prints output to stdout/stderr)
    """
    # Validate required fields
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")

    name = data.get('name')
    if not name:
        raise ValueError("Checkpoint 'name' is required")

    if not isinstance(name, str) or not name.strip():
        raise ValueError("Checkpoint 'name' must be a non-empty string")

    name = name.strip()

    try:
        # Ensure database is initialized
        init_db()

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Begin transaction
            cursor.execute("BEGIN TRANSACTION")

            try:
                # Check if checkpoint exists
                cursor.execute("SELECT id FROM checkpoints WHERE name = ?", (name,))
                existing = cursor.fetchone()

                # Extract context info (support both direct fields and nested context object)
                context = data.get('context', {})
                working_directory = data.get('working_directory') or context.get('working_directory')
                git_branch = data.get('git_branch') or context.get('git_branch')
                git_status = data.get('git_status') or context.get('git_status')

                if existing:
                    checkpoint_id = existing[0]
                    # Update existing checkpoint
                    cursor.execute("""
                        UPDATE checkpoints
                        SET summary = ?, current_goal = ?, working_directory = ?,
                            git_branch = ?, git_status = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (
                        data.get('summary'),
                        data.get('current_goal'),
                        working_directory,
                        git_branch,
                        git_status,
                        checkpoint_id
                    ))
                    # Clear related records for update
                    cursor.execute("DELETE FROM todos WHERE checkpoint_id = ?", (checkpoint_id,))
                    cursor.execute("DELETE FROM file_modifications WHERE checkpoint_id = ?", (checkpoint_id,))
                    cursor.execute("DELETE FROM key_decisions WHERE checkpoint_id = ?", (checkpoint_id,))
                    cursor.execute("DELETE FROM artifacts WHERE checkpoint_id = ?", (checkpoint_id,))
                else:
                    # Insert new checkpoint
                    cursor.execute("""
                        INSERT INTO checkpoints
                        (name, summary, current_goal, working_directory, git_branch, git_status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        name,
                        data.get('summary'),
                        data.get('current_goal'),
                        working_directory,
                        git_branch,
                        git_status
                    ))
                    checkpoint_id = cursor.lastrowid

                # Count items for output message
                todos_count = 0
                files_count = 0
                decisions_count = 0
                artifacts_count = 0

                # Insert todos
                todos = data.get('todos', [])
                if not isinstance(todos, list):
                    todos = []

                for todo in todos:
                    if not isinstance(todo, dict):
                        continue  # Skip invalid todos

                    content = todo.get('content') or todo.get('title') or todo.get('description')
                    if not content:
                        continue  # Skip todos without content

                    active_form = todo.get('activeForm') or todo.get('active_form') or content
                    status = todo.get('status', 'pending')

                    # Validate status
                    if status not in ['pending', 'in_progress', 'completed']:
                        status = 'pending'

                    cursor.execute("""
                        INSERT INTO todos (checkpoint_id, content, active_form, status, order_index)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        content,
                        active_form,
                        status,
                        todos_count
                    ))
                    todos_count += 1

                # Insert file modifications (support both field names)
                files = data.get('file_modifications') or data.get('files_modified', [])
                if not isinstance(files, list):
                    files = []

                for mod in files:
                    if not isinstance(mod, dict):
                        raise ValueError("Each file modification must be an object")

                    file_path = mod.get('file_path')
                    if not file_path:
                        raise ValueError("Each file modification must have 'file_path' field")

                    modification_type = mod.get('modification_type') or mod.get('status') or 'modified'

                    # Validate modification_type
                    if modification_type not in ['created', 'modified', 'deleted']:
                        modification_type = 'modified'

                    cursor.execute("""
                        INSERT INTO file_modifications (checkpoint_id, file_path, modification_type, description)
                        VALUES (?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        file_path,
                        modification_type,
                        mod.get('description')
                    ))
                    files_count += 1

                # Insert key decisions
                decisions = data.get('key_decisions', [])
                if not isinstance(decisions, list):
                    decisions = []

                for decision in decisions:
                    if not isinstance(decision, dict):
                        continue  # Skip invalid decisions

                    decision_title = decision.get('decision_title') or decision.get('title')
                    if not decision_title:
                        continue  # Skip decisions without title

                    decision_content = decision.get('decision_content') or decision.get('rationale') or decision.get('content') or decision.get('description')

                    cursor.execute("""
                        INSERT INTO key_decisions (checkpoint_id, decision_title, decision_content, order_index)
                        VALUES (?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        decision_title,
                        decision_content,
                        decisions_count
                    ))
                    decisions_count += 1

                # Insert artifacts
                artifacts = data.get('artifacts', [])
                if not isinstance(artifacts, list):
                    artifacts = []

                for artifact in artifacts:
                    if not isinstance(artifact, dict):
                        continue  # Skip invalid artifacts

                    artifact_title = artifact.get('artifact_title') or artifact.get('name') or artifact.get('title')
                    if not artifact_title:
                        continue  # Skip artifacts without title

                    artifact_content = artifact.get('artifact_content') or artifact.get('description') or artifact.get('content')
                    artifact_type = artifact.get('artifact_type') or artifact.get('type')

                    cursor.execute("""
                        INSERT INTO artifacts (checkpoint_id, artifact_title, artifact_content, artifact_type, order_index)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        artifact_title,
                        artifact_content,
                        artifact_type,
                        artifacts_count
                    ))
                    artifacts_count += 1

                conn.commit()

                # Print success message with counts
                print(f"Saved checkpoint '{name}' ({todos_count} todos, {files_count} files, {decisions_count} decisions, {artifacts_count} artifacts)")
                sys.exit(0)

            except (ValueError, sqlite3.Error) as e:
                conn.rollback()
                raise

    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            print(f"Error: Checkpoint name '{name}' already exists. Use update to modify it.", file=sys.stderr)
        else:
            print(f"Error: Database integrity error: {e}", file=sys.stderr)
        sys.exit(1)
    except sqlite3.Error as e:
        print(f"Error: Database error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Read JSON from stdin
        input_data = sys.stdin.read().strip()
        if not input_data:
            raise ValueError("No input provided. Please pipe JSON data to stdin.")

        data = json.loads(input_data)
        save_checkpoint(data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
