#!/usr/bin/env python3
"""
MCP Server for Checkpoint Management
Manages project checkpoints with todos, file modifications, decisions, and artifacts
"""

import sqlite3
import os
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent, ToolInput
import mcp.server.stdio

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("checkpoint-manager")

# Initialize MCP server
server = Server("checkpoint-manager")

# Database path
DB_PATH = os.path.expanduser("~/.claude/mcp-servers/checkpoint-manager/checkpoints.db")


class CheckpointManager:
    """Manages checkpoint operations with SQLite database"""

    def __init__(self, db_path: str):
        """Initialize database connection and create tables if needed"""
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
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
                        title TEXT NOT NULL,
                        description TEXT,
                        status TEXT DEFAULT 'pending',
                        priority TEXT DEFAULT 'medium',
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
                        status TEXT,
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
                        title TEXT NOT NULL,
                        rationale TEXT,
                        impact TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
                    )
                """)

                # Create artifacts table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS artifacts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        checkpoint_id INTEGER NOT NULL,
                        name TEXT NOT NULL,
                        artifact_type TEXT,
                        path TEXT,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
                    )
                """)

                conn.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def save_checkpoint(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update a checkpoint with all related data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if checkpoint exists
                cursor.execute("SELECT id FROM checkpoints WHERE name = ?", (name,))
                existing = cursor.fetchone()

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
                        data.get('working_directory'),
                        data.get('git_branch'),
                        data.get('git_status'),
                        checkpoint_id
                    ))
                    action = "updated"
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
                        data.get('working_directory'),
                        data.get('git_branch'),
                        data.get('git_status')
                    ))
                    checkpoint_id = cursor.lastrowid
                    action = "created"

                # Clear related records for update
                if existing:
                    cursor.execute("DELETE FROM todos WHERE checkpoint_id = ?", (checkpoint_id,))
                    cursor.execute("DELETE FROM file_modifications WHERE checkpoint_id = ?", (checkpoint_id,))
                    cursor.execute("DELETE FROM key_decisions WHERE checkpoint_id = ?", (checkpoint_id,))
                    cursor.execute("DELETE FROM artifacts WHERE checkpoint_id = ?", (checkpoint_id,))

                # Insert todos
                for todo in data.get('todos', []):
                    cursor.execute("""
                        INSERT INTO todos (checkpoint_id, title, description, status, priority)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        todo.get('title'),
                        todo.get('description'),
                        todo.get('status', 'pending'),
                        todo.get('priority', 'medium')
                    ))

                # Insert file modifications
                for mod in data.get('file_modifications', []):
                    cursor.execute("""
                        INSERT INTO file_modifications (checkpoint_id, file_path, status, description)
                        VALUES (?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        mod.get('file_path'),
                        mod.get('status'),
                        mod.get('description')
                    ))

                # Insert key decisions
                for decision in data.get('key_decisions', []):
                    cursor.execute("""
                        INSERT INTO key_decisions (checkpoint_id, title, rationale, impact)
                        VALUES (?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        decision.get('title'),
                        decision.get('rationale'),
                        decision.get('impact')
                    ))

                # Insert artifacts
                for artifact in data.get('artifacts', []):
                    cursor.execute("""
                        INSERT INTO artifacts (checkpoint_id, name, artifact_type, path, description)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        checkpoint_id,
                        artifact.get('name'),
                        artifact.get('artifact_type'),
                        artifact.get('path'),
                        artifact.get('description')
                    ))

                conn.commit()
                logger.info(f"Checkpoint '{name}' {action} successfully (ID: {checkpoint_id})")

                return {
                    "status": "success",
                    "message": f"Checkpoint '{name}' {action} successfully",
                    "checkpoint_id": checkpoint_id,
                    "action": action
                }
        except sqlite3.IntegrityError as e:
            logger.error(f"Integrity error: {e}")
            raise ValueError(f"Checkpoint name must be unique: {e}")
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    def resume_checkpoint(self, name: str) -> Dict[str, Any]:
        """Load a checkpoint by name with all related data"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                # Fetch checkpoint
                cursor.execute("SELECT * FROM checkpoints WHERE name = ?", (name,))
                checkpoint_row = cursor.fetchone()

                if not checkpoint_row:
                    raise ValueError(f"Checkpoint '{name}' not found")

                checkpoint_id = checkpoint_row['id']

                # Build checkpoint dict
                checkpoint_data = {
                    "name": checkpoint_row['name'],
                    "summary": checkpoint_row['summary'],
                    "current_goal": checkpoint_row['current_goal'],
                    "working_directory": checkpoint_row['working_directory'],
                    "git_branch": checkpoint_row['git_branch'],
                    "git_status": checkpoint_row['git_status'],
                    "created_at": checkpoint_row['created_at'],
                    "updated_at": checkpoint_row['updated_at'],
                }

                # Fetch todos
                cursor.execute("""
                    SELECT title, description, status, priority
                    FROM todos WHERE checkpoint_id = ?
                    ORDER BY created_at
                """, (checkpoint_id,))
                checkpoint_data['todos'] = [dict(row) for row in cursor.fetchall()]

                # Fetch file modifications
                cursor.execute("""
                    SELECT file_path, status, description
                    FROM file_modifications WHERE checkpoint_id = ?
                    ORDER BY created_at
                """, (checkpoint_id,))
                checkpoint_data['file_modifications'] = [dict(row) for row in cursor.fetchall()]

                # Fetch key decisions
                cursor.execute("""
                    SELECT title, rationale, impact
                    FROM key_decisions WHERE checkpoint_id = ?
                    ORDER BY created_at
                """, (checkpoint_id,))
                checkpoint_data['key_decisions'] = [dict(row) for row in cursor.fetchall()]

                # Fetch artifacts
                cursor.execute("""
                    SELECT name, artifact_type, path, description
                    FROM artifacts WHERE checkpoint_id = ?
                    ORDER BY created_at
                """, (checkpoint_id,))
                checkpoint_data['artifacts'] = [dict(row) for row in cursor.fetchall()]

                # Convert to YAML for LLM consumption
                yaml_content = yaml.dump(checkpoint_data, default_flow_style=False, sort_keys=False)

                logger.info(f"Checkpoint '{name}' resumed successfully")

                return {
                    "status": "success",
                    "message": f"Checkpoint '{name}' loaded successfully",
                    "checkpoint_yaml": yaml_content,
                    "checkpoint_data": checkpoint_data
                }
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    def list_checkpoints(self) -> Dict[str, Any]:
        """List all checkpoints ordered by updated_at DESC"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT id, name, created_at, updated_at, summary
                    FROM checkpoints
                    ORDER BY updated_at DESC
                """)

                checkpoints = [dict(row) for row in cursor.fetchall()]
                logger.info(f"Listed {len(checkpoints)} checkpoints")

                return {
                    "status": "success",
                    "count": len(checkpoints),
                    "checkpoints": checkpoints
                }
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    def delete_checkpoint(self, name: str) -> Dict[str, Any]:
        """Delete a checkpoint and all related records"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if checkpoint exists
                cursor.execute("SELECT id FROM checkpoints WHERE name = ?", (name,))
                checkpoint = cursor.fetchone()

                if not checkpoint:
                    raise ValueError(f"Checkpoint '{name}' not found")

                # Delete checkpoint (CASCADE will delete related records)
                cursor.execute("DELETE FROM checkpoints WHERE name = ?", (name,))
                conn.commit()

                logger.info(f"Checkpoint '{name}' deleted successfully")

                return {
                    "status": "success",
                    "message": f"Checkpoint '{name}' deleted successfully"
                }
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise

    def update_checkpoint(self, name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Partially update a checkpoint"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Check if checkpoint exists
                cursor.execute("SELECT id FROM checkpoints WHERE name = ?", (name,))
                checkpoint = cursor.fetchone()

                if not checkpoint:
                    raise ValueError(f"Checkpoint '{name}' not found")

                checkpoint_id = checkpoint[0]

                # Build dynamic update query
                update_fields = []
                update_values = []

                field_mapping = {
                    'summary': 'summary',
                    'current_goal': 'current_goal',
                    'working_directory': 'working_directory',
                    'git_branch': 'git_branch',
                    'git_status': 'git_status'
                }

                for key, db_field in field_mapping.items():
                    if key in updates:
                        update_fields.append(f"{db_field} = ?")
                        update_values.append(updates[key])

                if not update_fields:
                    raise ValueError("No valid fields to update")

                update_values.append(name)  # For WHERE clause

                query = f"""
                    UPDATE checkpoints
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """

                cursor.execute(query, update_values)
                conn.commit()

                logger.info(f"Checkpoint '{name}' updated successfully")

                return {
                    "status": "success",
                    "message": f"Checkpoint '{name}' updated successfully",
                    "updated_fields": list(updates.keys())
                }
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise


# Initialize checkpoint manager
checkpoint_manager = CheckpointManager(DB_PATH)


# Register tools
@server.list_tools()
async def list_tools():
    """List all available tools"""
    return [
        Tool(
            name="save_checkpoint",
            description="Save a new checkpoint or update an existing one with project state",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Unique name for the checkpoint"
                    },
                    "data": {
                        "type": "object",
                        "description": "Checkpoint data including summary, goals, and related items",
                        "properties": {
                            "summary": {"type": "string"},
                            "current_goal": {"type": "string"},
                            "working_directory": {"type": "string"},
                            "git_branch": {"type": "string"},
                            "git_status": {"type": "string"},
                            "todos": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "status": {"type": "string"},
                                        "priority": {"type": "string"}
                                    }
                                }
                            },
                            "file_modifications": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "file_path": {"type": "string"},
                                        "status": {"type": "string"},
                                        "description": {"type": "string"}
                                    }
                                }
                            },
                            "key_decisions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "rationale": {"type": "string"},
                                        "impact": {"type": "string"}
                                    }
                                }
                            },
                            "artifacts": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "artifact_type": {"type": "string"},
                                        "path": {"type": "string"},
                                        "description": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["summary"]
                    }
                },
                "required": ["name", "data"]
            }
        ),
        Tool(
            name="resume_checkpoint",
            description="Load a checkpoint by name with all related data",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the checkpoint to resume"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="list_checkpoints",
            description="List all checkpoints ordered by most recent update",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="delete_checkpoint",
            description="Delete a checkpoint and all its related data",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the checkpoint to delete"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="update_checkpoint",
            description="Partially update a checkpoint with new values",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the checkpoint to update"
                    },
                    "updates": {
                        "type": "object",
                        "description": "Fields to update (summary, current_goal, working_directory, git_branch, git_status)",
                        "properties": {
                            "summary": {"type": "string"},
                            "current_goal": {"type": "string"},
                            "working_directory": {"type": "string"},
                            "git_branch": {"type": "string"},
                            "git_status": {"type": "string"}
                        }
                    }
                },
                "required": ["name", "updates"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Handle tool calls"""
    try:
        if name == "save_checkpoint":
            result = checkpoint_manager.save_checkpoint(
                arguments["name"],
                arguments["data"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "resume_checkpoint":
            result = checkpoint_manager.resume_checkpoint(arguments["name"])
            # Return YAML for token efficiency
            return [TextContent(type="text", text=result["checkpoint_yaml"])]

        elif name == "list_checkpoints":
            result = checkpoint_manager.list_checkpoints()
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "delete_checkpoint":
            result = checkpoint_manager.delete_checkpoint(arguments["name"])
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        elif name == "update_checkpoint":
            result = checkpoint_manager.update_checkpoint(
                arguments["name"],
                arguments["updates"]
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2))]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        error_response = {
            "status": "error",
            "message": str(e),
            "tool": name
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]


if __name__ == "__main__":
    logger.info("Starting Checkpoint Manager MCP Server")
    mcp.server.stdio.run(server)
