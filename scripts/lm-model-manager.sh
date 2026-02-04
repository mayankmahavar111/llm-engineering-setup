#!/bin/bash
# LM Studio Model Management Utility
# Handles automatic model unloading and loading for agents

LM_STUDIO_URL="http://localhost:1234/v1"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to get currently loaded model
get_current_model() {
    curl -s "${LM_STUDIO_URL}/models" 2>/dev/null | \
    python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    models = data.get('data', [])
    if models:
        print(models[0]['id'])
    else:
        print('none')
except:
    print('error')
"
}

# Function to unload current model
unload_model() {
    local current_model="$1"
    if [ "$current_model" != "none" ] && [ "$current_model" != "error" ]; then
        echo -e "${YELLOW}[Model Manager] Unloading current model: ${current_model}${NC}" >&2
        # LM Studio API call to unload model (if API supports it)
        # For now, just log - LM Studio will auto-unload when loading new model
        return 0
    fi
    return 0
}

# Function to load a specific model
load_model() {
    local model_name="$1"

    echo -e "${YELLOW}[Model Manager] Loading model: ${model_name}${NC}" >&2

    # LM Studio automatically loads the model when you make a request with it
    # We'll verify it's available
    local available=$(curl -s "${LM_STUDIO_URL}/models" 2>/dev/null | \
        python3 -c "
import sys, json
target = '${model_name}'
try:
    data = json.load(sys.stdin)
    models = [m['id'] for m in data.get('data', [])]
    print('yes' if target in models else 'no')
except:
    print('error')
")

    if [ "$available" = "yes" ]; then
        echo -e "${GREEN}[Model Manager] Model ${model_name} is available${NC}" >&2
        return 0
    elif [ "$available" = "no" ]; then
        echo -e "${RED}[Model Manager] Model ${model_name} not found in LM Studio${NC}" >&2
        echo -e "${YELLOW}Available models:${NC}" >&2
        curl -s "${LM_STUDIO_URL}/models" 2>/dev/null | \
            python3 -c "import sys,json; [print('  - '+m['id']) for m in json.load(sys.stdin).get('data',[])]" >&2
        return 1
    else
        echo -e "${RED}[Model Manager] Error checking LM Studio${NC}" >&2
        return 1
    fi
}

# Function to switch models (unload current, load new)
switch_model() {
    local target_model="$1"

    echo -e "${GREEN}═══════════════════════════════════════════${NC}" >&2
    echo -e "${GREEN}  LM Studio Model Manager${NC}" >&2
    echo -e "${GREEN}═══════════════════════════════════════════${NC}" >&2

    # Get current model
    local current_model=$(get_current_model)
    echo -e "${YELLOW}Current model: ${current_model}${NC}" >&2
    echo -e "${YELLOW}Target model:  ${target_model}${NC}" >&2

    # Check if already loaded
    if [ "$current_model" = "$target_model" ]; then
        echo -e "${GREEN}✓ Model already loaded, no switch needed${NC}" >&2
        echo -e "${GREEN}═══════════════════════════════════════════${NC}" >&2
        return 0
    fi

    # Unload current (LM Studio does this automatically)
    unload_model "$current_model"

    # Load target
    if load_model "$target_model"; then
        echo -e "${GREEN}✓ Successfully prepared ${target_model}${NC}" >&2
        echo -e "${GREEN}═══════════════════════════════════════════${NC}" >&2
        return 0
    else
        echo -e "${RED}✗ Failed to prepare ${target_model}${NC}" >&2
        echo -e "${GREEN}═══════════════════════════════════════════${NC}" >&2
        return 1
    fi
}

# Function to list available models
list_models() {
    echo "Available models in LM Studio:"
    curl -s "${LM_STUDIO_URL}/models" 2>/dev/null | \
        python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for model in data.get('data', []):
        print(f\"  - {model['id']}\")
except:
    print('  Error fetching models')
"
}

# Main command handling
case "$1" in
    switch)
        if [ -z "$2" ]; then
            echo "Usage: $0 switch <model-name>"
            exit 1
        fi
        switch_model "$2"
        ;;
    current)
        get_current_model
        ;;
    list)
        list_models
        ;;
    unload)
        current=$(get_current_model)
        unload_model "$current"
        ;;
    *)
        echo "LM Studio Model Manager"
        echo ""
        echo "Usage: $0 {switch|current|list|unload} [model-name]"
        echo ""
        echo "Commands:"
        echo "  switch <model>  - Unload current and prepare specified model"
        echo "  current         - Show currently loaded model"
        echo "  list            - List all available models"
        echo "  unload          - Unload current model"
        echo ""
        echo "Example:"
        echo "  $0 switch google/gemma-3-4b"
        exit 1
        ;;
esac
