#!/bin/bash
# Use LM Studio to generate content and write to file

OUTPUT_FILE="$1"
TASK_DESCRIPTION="$2"
# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_SCRIPT="$SCRIPT_DIR/log-lmstudio-usage.sh"

if [[ -z "$OUTPUT_FILE" || -z "$TASK_DESCRIPTION" ]]; then
    echo "Usage: $0 <output_file> <task_description> [context]"
    echo "Example: $0 ~/output.md 'Write a summary of...' 'Context: ...'"
    exit 1
fi

# Prepare the prompt
if [[ -n "$CONTEXT" ]]; then
    FULL_PROMPT="$TASK_DESCRIPTION\n\nContext:\n$CONTEXT"
else
    FULL_PROMPT="$TASK_DESCRIPTION"
fi

PROMPT_LENGTH=${#FULL_PROMPT}

echo "🤖 Using LM Studio to generate content..."
echo "📝 Task: $TASK_DESCRIPTION"
echo "📄 Output: $OUTPUT_FILE"
echo ""

# Call LM Studio API
RESPONSE=$(curl -s http://localhost:1234/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d "{
        \"model\": \"meta-llama-3.1-8b-instruct\",
        \"messages\": [
            {\"role\": \"system\", \"content\": \"You are a technical documentation writer. Write clear, well-structured content in markdown format. Be comprehensive and accurate.\"},
            {\"role\": \"user\", \"content\": $(echo "$FULL_PROMPT" | jq -Rs .)}
        ],
        \"temperature\": 0.5,
        \"max_tokens\": 4096
    }")

# Extract the generated content
CONTENT=$(echo "$RESPONSE" | jq -r '.choices[0].message.content')

if [[ -z "$CONTENT" || "$CONTENT" == "null" ]]; then
    echo "❌ Error: Failed to generate content from LM Studio"
    echo "Response: $RESPONSE"
    exit 1
fi

CONTENT_LENGTH=${#CONTENT}
ESTIMATED_TOKENS=$((CONTENT_LENGTH / 4))

# Write to file
echo "$CONTENT" > "$OUTPUT_FILE"

# Log usage
"$LOG_SCRIPT" "file-writer" "$PROMPT_LENGTH" "$CONTENT_LENGTH" "meta-llama-3.1-8b-instruct" "file-writing"

# Output results
echo "✅ Content generated and written successfully!"
echo ""
echo "=== STATISTICS ==="
echo "Prompt size: $PROMPT_LENGTH chars (~$((PROMPT_LENGTH / 4)) tokens)"
echo "Generated: $CONTENT_LENGTH chars (~$ESTIMATED_TOKENS tokens)"
echo "File: $OUTPUT_FILE"
echo ""
echo "💰 TOKEN SAVINGS:"
echo "   If Claude wrote this: ~$ESTIMATED_TOKENS output tokens"
echo "   Cost saved: ~\$$(awk "BEGIN {printf \"%.3f\", $ESTIMATED_TOKENS / 1000000 * 15}")"
echo ""
echo "=== PREVIEW ==="
head -20 "$OUTPUT_FILE"
echo ""
echo "... (see full content in $OUTPUT_FILE)"
