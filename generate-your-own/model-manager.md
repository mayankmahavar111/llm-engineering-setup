# Prompt: Generate a Model Management Script

You are a bash scripting expert. Generate a model management script for local LLM platforms.

## Requirements

- Support listing available models
- Support checking the currently loaded/active model
- Support switching between models
- Make it fast and lightweight
- Include error handling for connection failures

## Your Setup (Fill These In)

- Which platform do you use?
  - LM Studio (default: http://localhost:1234)
  - Ollama (default: http://localhost:11434)
  - vLLM (custom endpoint)
  - Something else?

- What's your API endpoint and port?
- Do you want a menu-driven interface (interactive selection) or command-line args (e.g., `model-manager.sh switch google/gemma-3-4b`)?
- Any model naming conventions or categories you follow? (e.g., all models in `/models/` folder)

## Output Format

Generate a bash script:
- Output path: `$HOME/.claude/scripts/model-manager.sh`
- Commands needed: `current`, `switch <modelname>`, `list`
- Example: `~/.claude/scripts/model-manager.sh current` returns current model name
- Include comments and usage instructions at the top
- Make it executable and test-ready

The example in this repo (`scripts/lm-model-manager.sh`) uses LM Studio — adapt for your setup.

Generate this script now.
