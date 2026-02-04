---
description: Research a topic and create a comprehensive summary report using hybrid Claude+Ollama workflow
argument-hint: [topic]
---

Research "$ARGUMENTS" using the following hybrid workflow to minimize token usage:

## Phase 1: Claude's Critical Thinking (High-Value, Low-Token)

1. **Web Search & Discovery**
   - Use WebSearch to find the top 10-15 most relevant articles, papers, and resources
   - Evaluate source quality and relevance
   - Extract key URLs and brief summaries

2. **Information Extraction**
   - Use WebFetch to get content from the most important sources
   - Identify key themes, patterns, and insights
   - Create structured bullet points of main concepts

3. **Create Processing Brief**
   - Organize findings into a structured outline
   - Define sections for the final report
   - Prepare content summaries for the research-processor agent

## Phase 2: Offload to research-processor Agent (Heavy Lifting, Zero API Cost)

4. **Delegate to Local Ollama**
   - Launch the research-processor agent with:
     - All extracted content and summaries
     - The defined structure/outline
     - Target file path: `~/research/[topic]-summary-YYYY-MM-DD.md`
   - The agent will:
     - Process all content thoroughly
     - Generate comprehensive, well-formatted report
     - Save to the specified file

## Phase 3: Claude's Quality Review (Quick Validation)

5. **Review & Insights**
   - Read the generated report
   - Add high-level insights and conclusions
   - Suggest related topics for further research

## Output Format

The research-processor agent should generate a report with:

```markdown
# Research Summary: [Topic]

**Research Date:** [Date]
**Sources Analyzed:** [Count]
**Key Themes:** [List]

## Executive Summary
[3-5 paragraph overview]

## Main Findings

### [Theme 1]
[Detailed analysis]

### [Theme 2]
[Detailed analysis]

...

## Key Insights
- [Insight 1]
- [Insight 2]
...

## Practical Applications
[How this research can be applied]

## Further Reading
[List of sources with URLs]

---
*Generated using Claude Code hybrid workflow (Claude research + Ollama processing)*
```

## Token Efficiency

- **Claude usage:** ~5-10k tokens (research + review only)
- **Ollama usage:** ~20-50k tokens (heavy processing, $0 cost)
- **Savings:** 80-90% reduction in API costs

Let's start researching!
