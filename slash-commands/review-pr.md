---
description: Run a comprehensive PR review using specialized sub-agents (comments, tests, errors, types, code quality, simplification)
argument-hint: [aspects] [parallel]
---

# PR Review Command

## Overview

This command orchestrates a comprehensive pull request review by analyzing changed files and dispatching them to specialized review agents. It breaks down complex reviews into focused, parallel-capable tasks that save tokens and provide detailed feedback.

**Note:** This command uses the code-reviewer agent. Make sure `agents/` is set up first.

## Argument Parsing

The command accepts:
- **aspects**: Comma-separated list or space-separated words specifying which review types to run
  - Valid values: `comments`, `tests`, `errors`, `types`, `code`, `simplify`, `all`
  - Default: `all` (runs all applicable reviews)
- **parallel**: Optional flag to run all review agents in parallel instead of sequential

Examples:
```
/review-pr                          # All reviews, sequential
/review-pr all                      # All reviews, sequential (explicit)
/review-pr tests errors             # Only test and error reviews
/review-pr code simplify parallel   # Code + simplify reviews, parallel
/review-pr all parallel             # All reviews, parallel
```

## Process Flow

### 1. Determine Changed Files

```bash
git diff --name-only HEAD origin/main
```

Categorize files by type:
- Test files: `*_test.py`, `*_spec.js`, `test_*.go`, etc.
- Comment/doc files: `*.md`, `*.rst`, `CHANGELOG`, docstrings in modified code
- Code files: Source code with logic/behavior changes
- Type files: TypeScript/Python type definitions, interface changes

### 2. Parse Aspect Arguments

Map requested aspects to review agents and file sets:

| Aspect | Trigger | What Gets Reviewed | Agent Focus |
|--------|---------|-------------------|-------------|
| `code` | Always enabled | All changed files | General quality, bugs, style |
| `tests` | If `tests` requested OR test files changed | Test files + coverage | Test quality, assertions, mocks |
| `comments` | If `comments` requested OR doc changes detected | Comments, docstrings, README | Documentation clarity, accuracy |
| `errors` | If `errors` requested OR error handling changed | Error-prone sections | Exception handling, edge cases |
| `types` | If `types` requested OR type hints added | Type definitions, annotations | Type safety, generics, contracts |
| `simplify` | After all other aspects pass | All code reviewed | Refactor opportunities, clarity |

### 3. Build Review Queue

Create ordered list of review tasks:

```
Sequential Mode (default):
1. code → 2. tests → 3. comments → 4. errors → 5. types → 6. simplify

Parallel Mode:
- Launch all applicable reviews simultaneously
- Aggregate results as they complete
```

### 4. Launch Code Reviewer Agent

For each aspect, invoke the code-reviewer agent with:

```
task: launch_agent
agent: code-reviewer
scope: [changed files for this aspect]
focus: [aspect-specific instructions]
```

**Focus Instructions by Aspect:**

- **code**: "Review for bugs, security issues, code quality, style consistency, dead code, and performance problems"
- **tests**: "Review test coverage, assertion quality, mock appropriateness, test maintainability, edge case coverage"
- **comments**: "Review documentation accuracy, comment clarity, docstring completeness, README alignment with changes"
- **errors**: "Review error handling completeness, exception specificity, error messages clarity, recovery mechanisms"
- **types**: "Review type annotations correctness, generic constraints, interface compliance, null-safety"
- **simplify**: "Suggest refactoring opportunities, complexity reduction, clarity improvements, pattern standardization"

### 5. Aggregate Results

Combine reports from all agents in priority order:

```
CRITICAL ISSUES
├── [source] File:Line — Issue description
├── [source] File:Line — Issue description
└── ...

IMPORTANT ISSUES
├── [source] File:Line — Issue description
└── ...

SUGGESTIONS
├── [source] File:Line — Suggestion
└── ...

STRENGTHS
├── [source] — Pattern or achievement
└── ...
```

Label each finding with its source agent (e.g., `[code]`, `[tests]`, `[security]`) for clarity.

### 6. Print Action Plan

Generate summary output:

```
PR REVIEW SUMMARY
================

Changed Files: [count] files across [categories]
Review Aspects: [list of aspects run]
Execution Mode: [sequential | parallel]

CRITICAL ISSUES: [count]
  - [file:line] [category] [description]

IMPORTANT ISSUES: [count]
  - [file:line] [category] [description]

SUGGESTIONS: [count]
  - [file:line] [category] [description]

STRENGTHS: [count]
  - [category] [description]

Next Steps:
1. [Top priority fix]
2. [Secondary concern]
3. [Optional improvement]
```

## Usage Examples

### Full Sequential Review (Default)
```
/review-pr
```
Runs: code → tests → comments → errors → types → simplify (in order)

### Targeted Review
```
/review-pr tests errors
```
Runs only test quality and error handling reviews, skipping others

### Security-Focused Review
```
/review-pr code simplify
```
Runs code quality (includes security) and simplification suggestions

### Fast Parallel Review
```
/review-pr all parallel
```
Launches all applicable reviews simultaneously, aggregates as complete

### Type Safety Check
```
/review-pr types
```
Focuses only on type annotations and type safety issues

## Implementation Notes

1. **File Detection**: Use glob patterns and git metadata to categorize files automatically
2. **Smart Sequencing**: In sequential mode, run simpler analyses first (comments, tests) before complex ones (errors, simplify)
3. **Parallel Safety**: Each agent review is independent; parallel mode is safe for all aspect combinations
4. **Failure Handling**: If one agent fails, continue with others; report which aspects completed
5. **Output Caching**: Consider caching file diffs to avoid re-reading during parallel execution
6. **Timeout**: Set reasonable timeout for parallel reviews (e.g., 2 minutes max)

## Integration with CI/CD

This command can be invoked during PR checks:
```bash
claude /review-pr all parallel >> pr-review-report.txt
```

Results can be posted to PR comments or stored as artifacts.
