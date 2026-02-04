---
description: Research a topic and create a comprehensive summary report using hybrid Antigravity+LocalLLM workflow
---

Research "TOPIC" using the following hybrid workflow to minimize token usage:

## Phase 1: Antigravity Research (High-Value)

1. **Web Search & Discovery**
   - Use `search_web` to find the top 10-15 most relevant articles/resources for "TOPIC".
   - Extract key URLs and brief summaries.

2. **Information Extraction**
   - Use `read_url_content` (or `read_browser_page` if needed) to get content from the most important sources.
   - Summarize the key findings in your context.

3. **Create Processing Brief**
   - Organize findings into a structured outline.
   - Prepare a long-form prompt containing the source material and the request for a summary.

## Phase 2: Offload to Local LLM (Zero Cost)

4. **Generate Report**
   - Use `./scripts/lm-write-file.sh` to generate the final report.
   - **Command**:
     ```bash
     ./scripts/lm-write-file.sh \
       "$HOME/research/TOPIC-summary-DATE.md" \
       "Write a comprehensive research report on TOPIC based on the provided context." \
       "CONTEXT_WITH_SOURCE_MATERIAL"
     ```
   - Note: Ensure the context passed to the script is properly escaped or passed via a temporary file if it's very large.

## Phase 3: Review

5. **Review**
   - confirm the file was created and show a preview.
