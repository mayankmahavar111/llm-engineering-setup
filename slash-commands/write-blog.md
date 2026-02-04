---
description: Write a blog post or article using hybrid workflow (Claude outlines, Ollama writes)
argument-hint: [topic]
---

Write a blog post about "$ARGUMENTS" using the hybrid workflow:

## Phase 1: Claude's Strategy (Structure & Key Points)

1. **Research & Planning**
   - Quick web search for latest info (if needed)
   - Define target audience
   - Create outline with main sections
   - Identify key points to cover

2. **Content Brief**
   - List 5-7 main points
   - Determine tone (technical, casual, formal)
   - Set target length (1500-2500 words recommended)
   - Identify examples to include

## Phase 2: Offload to content-writer Agent (Heavy Writing)

3. **Delegate to Local Ollama**
   - Launch content-writer agent with:
     - Topic and outline
     - Key points to elaborate
     - Target file: `~/blog/[slug]-YYYY-MM-DD.md`
     - Tone and audience
   - Agent generates:
     - Complete, polished article
     - Proper markdown formatting
     - Code examples (if applicable)

## Phase 3: Claude's Editorial Review (Polish & SEO)

4. **Review & Optimize**
   - Check flow and clarity
   - Suggest SEO improvements
   - Add meta description
   - Recommend related topics

## Output Format

```markdown
---
title: [Title]
date: [Date]
tags: [Tag1, Tag2, Tag3]
description: [Meta description]
---

# [Title]

[Complete article with proper sections]

## Related Topics
- [Topic 1]
- [Topic 2]
```

Let's create great content!
