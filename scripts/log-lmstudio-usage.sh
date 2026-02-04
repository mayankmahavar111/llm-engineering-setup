#!/bin/bash
# Log LM Studio usage to SQLite database

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

DB_PATH="${DB_PATH:-$REPO_ROOT/conversations.db}"

# Initiate DB if needed
sqlite3 "$DB_PATH" "CREATE TABLE IF NOT EXISTS lm_studio_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    agent_name TEXT,
    prompt_length INTEGER,
    response_length INTEGER,
    total_chars INTEGER,
    estimated_tokens INTEGER,
    model_used TEXT,
    task_type TEXT,
    timestamp DATETIME
);"

SESSION_ID="${CLAUDE_SESSION_ID:-unknown}"

# Function to estimate tokens (rough: 4 chars = 1 token)
estimate_tokens() {
    local char_count=$1
    echo $((char_count / 4))
}

# Log usage
log_usage() {
    local agent_name="$1"
    local prompt_length="$2"
    local response_length="$3"
    local model_used="$4"
    local task_type="$5"

    local total_chars=$((prompt_length + response_length))
    local estimated_tokens=$(estimate_tokens "$total_chars")

    sqlite3 "$DB_PATH" <<EOF
INSERT INTO lm_studio_usage (
    session_id,
    agent_name,
    prompt_length,
    response_length,
    total_chars,
    estimated_tokens,
    model_used,
    task_type,
    timestamp
) VALUES (
    '$SESSION_ID',
    '$agent_name',
    $prompt_length,
    $response_length,
    $total_chars,
    $estimated_tokens,
    '$model_used',
    '$task_type',
    datetime('now')
);
EOF
}

# Main execution
if [[ $# -lt 5 ]]; then
    echo "Usage: $0 <agent_name> <prompt_length> <response_length> <model_used> <task_type>"
    exit 1
fi

log_usage "$1" "$2" "$3" "$4" "$5"
