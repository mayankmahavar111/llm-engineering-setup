#!/bin/bash

################################################################################
# llm-engineering-setup installer
# One-time setup script for Claude Code productivity system
################################################################################

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

################################################################################
# SECTION 1: HEADER
################################################################################

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}llm-engineering-setup installer${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

################################################################################
# SECTION 2: PRE-REQUISITE CHECKS (warn, do not exit)
################################################################################

echo -e "${YELLOW}Checking prerequisites...${NC}"
echo ""

PREREQ_OK=true

# Check python3 (version 3.10+)
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    if (( PYTHON_MAJOR > 3 || (PYTHON_MAJOR == 3 && PYTHON_MINOR >= 10) )); then
        echo -e "${GREEN}✓${NC} python3 ($PYTHON_VERSION)"
    else
        echo -e "${RED}✗${NC} python3 found but version is $PYTHON_VERSION (need 3.10+)"
        PREREQ_OK=false
    fi
else
    echo -e "${RED}✗${NC} python3 not found"
    PREREQ_OK=false
fi

# Check pip3
if command -v pip3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} pip3"
else
    echo -e "${RED}✗${NC} pip3 not found"
    PREREQ_OK=false
fi

# Check uvx
if command -v uvx &> /dev/null; then
    echo -e "${GREEN}✓${NC} uvx"
else
    echo -e "${RED}✗${NC} uvx not found (install hint: pip install uv)"
    PREREQ_OK=false
fi

# Check curl
if command -v curl &> /dev/null; then
    echo -e "${GREEN}✓${NC} curl"
else
    echo -e "${RED}✗${NC} curl not found"
    PREREQ_OK=false
fi

# Check jq
if command -v jq &> /dev/null; then
    echo -e "${GREEN}✓${NC} jq"
else
    echo -e "${RED}✗${NC} jq not found"
    PREREQ_OK=false
fi

# Check LM Studio running on localhost:1234
echo -n "Checking LM Studio on localhost:1234... "
if curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC} LM Studio not responding"
    PREREQ_OK=false
fi

echo ""

################################################################################
# SECTION 3: INSTALL PYTHON DEPS
################################################################################

echo -e "${YELLOW}Installing Python dependencies...${NC}"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt" > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} Python dependencies installed"
else
    echo -e "${YELLOW}⚠${NC} requirements.txt not found at $SCRIPT_DIR/requirements.txt"
fi
echo ""

################################################################################
# SECTION 4: CREATE DIRECTORIES
################################################################################

echo -e "${YELLOW}Creating directories...${NC}"

mkdir -p "$HOME/.claude/commands/"
echo -e "${GREEN}✓${NC} Created $HOME/.claude/commands/"

mkdir -p "$HOME/.claude/agents/"
echo -e "${GREEN}✓${NC} Created $HOME/.claude/agents/"

mkdir -p "$HOME/.claude/mcp-servers/checkpoint-manager/"
echo -e "${GREEN}✓${NC} Created $HOME/.claude/mcp-servers/checkpoint-manager/"

mkdir -p "$HOME/.claude/scripts/"
echo -e "${GREEN}✓${NC} Created $HOME/.claude/scripts/"

echo ""

################################################################################
# SECTION 5: COPY FILES
################################################################################

echo -e "${YELLOW}Copying files...${NC}"

# Copy slash-commands
if [ -d "$SCRIPT_DIR/slash-commands" ]; then
    cp "$SCRIPT_DIR/slash-commands"/*.md "$HOME/.claude/commands/" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Copied slash-commands to $HOME/.claude/commands/"
else
    echo -e "${YELLOW}⚠${NC} slash-commands directory not found"
fi

# Copy agents
if [ -d "$SCRIPT_DIR/agents" ]; then
    cp "$SCRIPT_DIR/agents"/*.md "$HOME/.claude/agents/" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Copied agents to $HOME/.claude/agents/"
else
    echo -e "${YELLOW}⚠${NC} agents directory not found"
fi

# Copy mcp-servers/checkpoint-manager
if [ -d "$SCRIPT_DIR/mcp-servers/checkpoint-manager" ]; then
    cp "$SCRIPT_DIR/mcp-servers/checkpoint-manager"/* "$HOME/.claude/mcp-servers/checkpoint-manager/" 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Copied checkpoint-manager to $HOME/.claude/mcp-servers/checkpoint-manager/"
else
    echo -e "${YELLOW}⚠${NC} checkpoint-manager directory not found"
fi

# Copy and chmod scripts
if [ -d "$SCRIPT_DIR/scripts" ]; then
    cp "$SCRIPT_DIR/scripts"/*.sh "$HOME/.claude/scripts/" 2>/dev/null || true
    chmod +x "$HOME/.claude/scripts"/*.sh 2>/dev/null || true
    echo -e "${GREEN}✓${NC} Copied and made executable scripts in $HOME/.claude/scripts/"
else
    echo -e "${YELLOW}⚠${NC} scripts directory not found"
fi

echo ""

################################################################################
# SECTION 6: INITIALIZE DATABASE
################################################################################

echo -e "${YELLOW}Initializing checkpoint database...${NC}"

DB_PATH="$HOME/.claude/mcp-servers/checkpoint-manager/checkpoints.db"
SCHEMA_PATH="$SCRIPT_DIR/mcp-servers/checkpoint-manager/schema.sql"

if [ -f "$DB_PATH" ]; then
    echo -e "${GREEN}✓${NC} Database already exists at $DB_PATH (skipping init)"
else
    if [ -f "$SCHEMA_PATH" ]; then
        sqlite3 "$DB_PATH" < "$SCHEMA_PATH"
        echo -e "${GREEN}✓${NC} Database initialized at $DB_PATH"
    else
        echo -e "${YELLOW}⚠${NC} schema.sql not found at $SCHEMA_PATH"
    fi
fi

echo ""

################################################################################
# SECTION 7: PATCH settings.json
################################################################################

echo -e "${YELLOW}Patching settings.json...${NC}"

SETTINGS_PATH="$HOME/.claude/settings.json"

# Use python3 to merge JSON settings
python3 << 'PYTHON_SCRIPT'
import json
import os
from pathlib import Path

settings_path = os.path.expanduser("~/.claude/settings.json")
checkpoint_manager_path = os.path.expanduser("~/.claude/mcp-servers/checkpoint-manager/server.py")

# Read existing settings or start with empty dict
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        settings = json.load(f)
else:
    settings = {}

# Ensure mcpServers key exists
if "mcpServers" not in settings:
    settings["mcpServers"] = {}

# Add/update the MCP server entries
settings["mcpServers"]["lmstudio"] = {
    "command": "uvx",
    "args": ["--from", "git+https://github.com/infinitimeless/LMStudio-MCP", "lmstudio-mcp"]
}

settings["mcpServers"]["checkpoint-manager"] = {
    "command": "python3",
    "args": [checkpoint_manager_path]
}

# Write back with indent=2
with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')  # Add trailing newline

PYTHON_SCRIPT

echo -e "${GREEN}✓${NC} Patched settings.json at $SETTINGS_PATH"
echo ""

################################################################################
# SECTION 8: SUMMARY
################################################################################

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

echo -e "${YELLOW}Installation Summary:${NC}"
echo -e "${GREEN}✓${NC} Python dependencies installed"
echo -e "${GREEN}✓${NC} Files copied to ~/.claude/"
if [ -f "$DB_PATH" ]; then
    echo -e "${GREEN}✓${NC} Database initialized"
else
    echo -e "${YELLOW}⚠${NC} Database already existed"
fi
echo -e "${GREEN}✓${NC} settings.json patched"
echo ""

echo -e "${YELLOW}Next Steps:${NC}"
echo -e "${YELLOW}[ ]${NC} LM Studio installed and running (manual — link: https://lmstudio.ai)"
echo -e "${YELLOW}[ ]${NC} Download at least one model in LM Studio"
echo -e "    Recommended: deepseek-coder-6.7b-instruct, google/gemma-3-4b"
echo ""

if [ "$PREREQ_OK" = false ]; then
    echo -e "${YELLOW}⚠${NC}  Some prerequisites are missing. Please address warnings above."
    echo ""
fi

echo -e "${GREEN}Done. Restart Claude Code to pick up the new MCP servers.${NC}"
