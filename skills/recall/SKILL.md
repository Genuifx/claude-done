---
name: recall
description: "Search and browse past session summaries saved in ~/.claude-done/. Use when the user says /recall, 'search history', 'find previous session', 'what did we do last time', 'look up past discussions', or wants to find earlier work."
---

# Recall

Search and browse session summaries previously saved by `/done` in `~/.claude-done/`.

## Workflow

### Step 1: Parse User Intent

Determine what the user is looking for:

- **Keyword search**: user mentions a topic, file, or term → use `--keyword`
- **Date filter**: user says "today", "this week", "last 7 days", or a date range → use `--date`
- **Branch filter**: user mentions a branch name → use `--branch`
- **Recent list**: user says "recent", "latest", or just `/recall` with no specifics → use `--last`
- Combine flags as needed (e.g., `--keyword auth --date 7d`)

### Step 2: Run the Search Script

```bash
python3 SKILL_DIR/scripts/search.py [options]
```

Available options:

| Flag | Description | Examples |
|------|-------------|---------|
| `--keyword <text>` | Full-text search | `--keyword "auth flow"` |
| `--date <range>` | Date filter | `--date today`, `--date 7d`, `--date 2026-01-01:2026-01-31` |
| `--branch <name>` | Branch filter (fuzzy) | `--branch feat-auth` |
| `--last <N>` | Show most recent N entries | `--last 5` |

No arguments defaults to listing the 10 most recent entries.

### Step 3: Present Results

Show the results in a clean, readable format. If the user wants to see the full content of a specific entry, read the `.md` file directly using the Read tool.
