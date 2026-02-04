---
description: Generate comprehensive documentation for code/APIs using hybrid workflow
argument-hint: [file or module path]
---

Generate documentation for "$ARGUMENTS" using the hybrid Claude+Ollama workflow:

## Phase 1: Claude's Analysis (Architecture & Planning)

1. **Code Analysis**
   - Read and analyze the target code file(s)
   - Identify public APIs, functions, and classes
   - Understand the overall architecture and patterns
   - Determine documentation structure

2. **Create Documentation Brief**
   - Define sections needed (API reference, usage guide, examples)
   - Extract function signatures and parameters
   - Identify important usage patterns
   - Note any edge cases or gotchas

## Phase 2: Offload to doc-generator Agent (Heavy Writing)

3. **Delegate to Local Ollama**
   - Launch doc-generator agent with:
     - Code file paths
     - Documentation structure
     - Target output path: `~/docs/[module]-documentation.md`
     - Audience level
   - Agent generates:
     - Complete API reference
     - Usage examples
     - Integration guides
     - Troubleshooting tips

## Phase 3: Claude's Review (Quality & Accuracy)

4. **Review & Enhance**
   - Verify technical accuracy
   - Add architectural insights
   - Suggest improvements

## Expected Output

Complete markdown documentation with:
- Table of contents
- API reference
- Code examples
- Best practices
- Common pitfalls

Start generating documentation!
