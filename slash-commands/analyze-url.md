---
description: Analyze a URL using Firecrawl + LM Studio to save tokens
argument-hint: [URL] [optional: analysis instructions]
---

You are analyzing a URL using the token-efficient Firecrawl + LM Studio workflow.

Parse the arguments: The first argument is the URL, everything after that is analysis instructions.

**WORKFLOW (MANDATORY):**

1. **Scrape with Firecrawl:**
   - Use `mcp__firecrawl__firecrawl_scrape` to fetch the URL
   - Extract as markdown with `onlyMainContent: true`
   - Set `maxAge: 3600000` for faster cached scrapes

2. **Analyze with LM Studio:**
   - Take the scraped content
   - Use `mcp__lmstudio__chat_completion` to analyze it
   - Pass clear instructions for what analysis is needed
   - Temperature: 0.7, max_tokens: 2048

3. **Return Results:**
   - Present the LM Studio analysis to the user
   - Do NOT use Claude's own analysis - you're just the orchestrator
   - This saves Claude tokens!

**IMPORTANT:**
- Always use Firecrawl first, then LM Studio
- Do not analyze content yourself - let LM Studio do it
- Only coordinate and format the final response

**Arguments received:** $ARGUMENTS

If no analysis instructions provided after the URL, default to: "Summarize the main points, key information, and important details from this content."
