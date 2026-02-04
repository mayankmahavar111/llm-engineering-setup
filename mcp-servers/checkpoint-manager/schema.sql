-- Checkpoint Management System SQLite Schema
-- This schema manages checkpoints for tracking project state, tasks, decisions, and artifacts

-- Checkpoints table: Main table storing checkpoint metadata
CREATE TABLE IF NOT EXISTS checkpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    summary TEXT,
    current_goal TEXT,
    working_directory TEXT,
    git_branch TEXT,
    git_status TEXT
);

-- Todos table: Task management for each checkpoint
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    active_form TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('pending', 'in_progress', 'completed')),
    order_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
);

-- File modifications table: Track file changes associated with a checkpoint
CREATE TABLE IF NOT EXISTS file_modifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    modification_type TEXT NOT NULL CHECK(modification_type IN ('created', 'modified', 'deleted')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
);

-- Key decisions table: Store important decisions made during the checkpoint
CREATE TABLE IF NOT EXISTS key_decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id INTEGER NOT NULL,
    decision_title TEXT NOT NULL,
    decision_content TEXT,
    order_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
);

-- Artifacts table: Store generated artifacts or code snippets
CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkpoint_id INTEGER NOT NULL,
    artifact_title TEXT NOT NULL,
    artifact_content TEXT,
    artifact_type TEXT,
    order_index INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(id) ON DELETE CASCADE
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_todos_checkpoint_id ON todos(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status);
CREATE INDEX IF NOT EXISTS idx_file_modifications_checkpoint_id ON file_modifications(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_file_modifications_file_path ON file_modifications(file_path);
CREATE INDEX IF NOT EXISTS idx_key_decisions_checkpoint_id ON key_decisions(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_checkpoint_id ON artifacts(checkpoint_id);
CREATE INDEX IF NOT EXISTS idx_checkpoints_name ON checkpoints(name);
CREATE INDEX IF NOT EXISTS idx_checkpoints_created_at ON checkpoints(created_at);

-- View for quick checkpoint summary with counts
CREATE VIEW IF NOT EXISTS checkpoint_summary AS
SELECT
    c.id,
    c.name,
    c.created_at,
    c.updated_at,
    c.summary,
    c.current_goal,
    COALESCE(COUNT(DISTINCT t.id), 0) as total_todos,
    COALESCE(SUM(CASE WHEN t.status = 'completed' THEN 1 ELSE 0 END), 0) as completed_todos,
    COALESCE(COUNT(DISTINCT fm.id), 0) as total_file_modifications,
    COALESCE(COUNT(DISTINCT kd.id), 0) as total_decisions,
    COALESCE(COUNT(DISTINCT a.id), 0) as total_artifacts
FROM checkpoints c
LEFT JOIN todos t ON c.id = t.checkpoint_id
LEFT JOIN file_modifications fm ON c.id = fm.checkpoint_id
LEFT JOIN key_decisions kd ON c.id = kd.checkpoint_id
LEFT JOIN artifacts a ON c.id = a.checkpoint_id
GROUP BY c.id;
