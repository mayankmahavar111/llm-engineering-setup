#!/bin/bash
# Read file and get LM Studio to summarize it to save Claude tokens

FILE_PATH="$1"
SUMMARY_TYPE="${2:-detailed}" # detailed, brief, or structure

if [[ ! -f "$FILE_PATH" ]]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

# Read file content
CONTENT=$(cat "$FILE_PATH")
CHAR_COUNT=${#CONTENT}

# Prepare prompt based on summary type
case "$SUMMARY_TYPE" in
    brief)
        PROMPT="Provide a brief 2-3 sentence summary of this file content:\n\n$CONTENT"
        ;;
    structure)
        PROMPT="Analyze the structure of this file and provide: 1) File type/format, 2) Main sections, 3) Key information contained. Be concise.\n\n$CONTENT"
        ;;
    detailed)
        PROMPT="Provide a detailed summary of this file including: 1) Purpose, 2) Key sections and their content, 3) Important details, 4) Any action items or todos mentioned.\n\n$CONTENT"
        ;;
    *)
        PROMPT="Summarize this file content:\n\n$CONTENT"
        ;;
esac

# Call LM Studio API
RESPONSE=$(curl -s http://localhost:1234/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"meta-llama-3.1-8b-instruct\",
        \"messages\": [
            {\"role\": \"system\", \"content\": \"You are a helpful assistant that summarizes file content concisely and accurately.\"},
            {\"role\": \"user\", \"content\": $(echo "$PROMPT" | jq -Rs .)}
        ],
        \"temperature\": 0.3,
        \"max_tokens\": 1000
    }")

# Extract the summary
SUMMARY=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')
RESPONSE_LENGTH=${#SUMMARY}

# Log usage
$HOME/.claude/scripts/log-lmstudio-usage.sh "file-reader" "$CHAR_COUNT" "$RESPONSE_LENGTH" "meta-llama-3.1-8b-instruct" "file-reading"

# Output results
echo "=== FILE: $FILE_PATH ==="
echo "=== ORIGINAL SIZE: $CHAR_COUNT chars (~$((CHAR_COUNT / 4)) tokens) ==="
echo "=== SUMMARY SIZE: $RESPONSE_LENGTH chars (~$((RESPONSE_LENGTH / 4)) tokens) ==="
echo "=== TOKEN SAVINGS: ~$((CHAR_COUNT / 4 - RESPONSE_LENGTH / 4)) tokens ==="
echo ""
echo "$SUMMARY"
