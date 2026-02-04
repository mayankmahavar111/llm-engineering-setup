# Prompt: Generate a Custom Status Line Script

You are a bash scripting expert. Generate a status line script for Claude Code or another AI tool that displays live metrics.

## Requirements

- Output a **single line of text** (this is how statusLine works in Claude Code)
- The script runs frequently (every few seconds), so it must be fast
- Use caching where appropriate to avoid hammering APIs
- Make it platform-aware (macOS, Linux)

## Your Setup (Fill These In)

- Which AI tool? (Claude Code, Cursor, Windsurf, etc.)
- What metrics do you want to show? (Pick 1–3 from this list or add your own)
  - Tokens used / context window % used
  - LM Studio current model
  - Ollama current model
  - Current git branch
  - Current time
  - CPU/memory usage
  - API response latency
  - Cache hit rate

- If showing API metrics: What's your API endpoint? (e.g., http://localhost:1234 for LM Studio, http://localhost:11434 for Ollama)
- Any other tools or data sources to pull from?

## Output Format

Generate a bash script ready to use as a statusLine command:
- Output path: `$HOME/.claude/scripts/statusline.sh`
- Include error handling (if API is down, show a fallback message)
- Include comments explaining each section
- After generating, show the settings.json addition needed to activate it

## Example Output Structure

```
#!/bin/bash
# Status line showing [metric1] | [metric2] | [metric3]
# The script fetches and caches data, outputs one line
```

Generate this script now.
