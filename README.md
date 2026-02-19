<p align="center">
  <img src="assets/logo.svg" alt="Claude Done" width="700">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Plugin-blueviolet" alt="Claude Code Plugin">
  <img src="https://img.shields.io/badge/Skills-/done_·_/recall-blue" alt="Skills: /done · /recall">
  <img src="https://img.shields.io/badge/Notion-Sync-000000?logo=notion&logoColor=white" alt="Notion Sync">
  <img src="https://img.shields.io/badge/Python-3.6+-3776AB?logo=python&logoColor=white" alt="Python 3.6+">
  <img src="https://img.shields.io/badge/Dependencies-Zero-brightgreen" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
</p>

# Claude Done

English | [中文](./README.zh-CN.md)

Your sessions with Claude Code are full of decisions, discoveries, and context that vanish the moment you close the terminal. Claude Done fixes that.

Two skills. One saves. One recalls. That's it.

## How It Works

- **`/done`** — Saves a structured summary of your current session to `~/.claude-done/`
- **`/recall`** — Searches and browses your past session summaries

Summaries are plain Markdown files with consistent naming and structure. Over time, you build a searchable knowledge base of everything you've worked on — decisions made, alternatives rejected, problems solved, and what's next.

Optionally, summaries can be **auto-synced to Notion** as child pages — zero dependencies, powered by a bundled Python script using only the standard library.

## Installation

### Via Plugin Marketplace
In Claude Code, register the marketplace first:
```
/plugin marketplace add Genuifx/claude-done
```
Then install the plugin from this marketplace:
```
/plugin install claude-done@done
```

### Verify

In a new Claude Code session:
- `/done` — should offer to save a session summary
- `/recall` — should search your past summaries

## The Workflow

```
Work on something → /done → summary saved

Next day → /recall → pick up where you left off
```

1. **Work normally** with Claude Code
2. **`/done`** when wrapping up — Claude reviews the full conversation and captures:
   - What was accomplished and key decisions
   - Alternatives explored and why they were rejected
   - Problems encountered and how they were resolved
   - Questions raised (resolved and unresolved)
   - Files changed and next steps
3. **`/recall`** in a future session to search your history
   - Keyword search: `/recall auth flow`
   - By date: `/recall last 7 days`
   - By branch: `/recall branch feat-auth`
   - Recent: `/recall` with no arguments lists the latest entries

## What Gets Saved

Each summary is a Markdown file in `~/.claude-done/` with this structure:

**Filename:** `2026-02-18_feat-auth_a1b2c3d4_fix-token-refresh.md`

```markdown
# Fix Token Refresh Logic

**Date:** 2026-02-18
**Branch:** feat-auth
**Session:** a1b2c3d4-...

## Summary
Investigated and fixed the token refresh race condition...

## Key Decisions
- Switched to mutex-based locking — simpler than the queue approach
- Kept backward compat with v1 tokens — migration too risky mid-sprint

## What Changed
- `src/auth/refresh.ts` — added mutex lock around refresh calls
- `src/auth/token.ts` — extended TTL buffer from 30s to 60s

## Problems & Solutions
- Race condition under concurrent requests — resolved with mutex pattern

## Questions Raised
- Should we add retry logic for failed refreshes? (unresolved)

## Next Steps
- [ ] Add integration tests for concurrent refresh scenarios
- [ ] Monitor error rates after deploy
```

Empty sections are omitted automatically.

## Skills Reference

| Skill | Trigger | What It Does |
|-------|---------|--------------|
| **done** | `/done`, "wrap up", "save session" | Reviews the full conversation and writes a structured summary |
| **recall** | `/recall`, "search history", "what did we do last time" | Searches `~/.claude-done/` by keyword, date, branch, or recency |

### Recall Search Options

| Flag | Example | Description |
|------|---------|-------------|
| `--keyword` | `--keyword "auth flow"` | Full-text search across summaries |
| `--date` | `--date today`, `--date 7d`, `--date 2026-01:2026-02` | Filter by date range |
| `--branch` | `--branch feat-auth` | Filter by branch name (fuzzy match) |
| `--last` | `--last 5` | Show N most recent entries |

Flags can be combined: `--keyword auth --date 7d`

## Notion Sync (Optional)

`/done` can automatically sync each summary to Notion as a child page. First time you run `/done`, it will ask if you want to set this up. You can also configure it manually:

### 1. Create a Notion Integration

1. Go to [notion.so/profile/integrations](https://www.notion.so/profile/integrations)
2. Click **"New integration"**, give it a name (e.g. "Claude Done")
3. Copy the **Internal Integration Token** (starts with `ntn_` or `secret_`)

### 2. Connect the Integration to Your Page

1. Open the Notion page where you want summaries saved
2. Click **"..."** (top right) → **"Connect to"** → select your integration

### 3. Write the Config

Create `~/.claude-done/config.json`:

```json
{
  "notion_token": "ntn_your_token_here",
  "notion_page_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

The `notion_page_id` is the 32-character hex string at the end of your page URL. For example:

```
https://www.notion.so/My-Page-1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d
                                └─────────── this part ───────────┘
```

Format it with hyphens: `1a2b3c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d`

### Skip Notion Sync

If you don't want Notion sync and don't want to be asked again:

```json
{
  "notion_sync": false
}
```

## Philosophy

- **Sessions are ephemeral. Knowledge shouldn't be.** Every session holds context worth keeping — decisions, dead ends, breakthroughs. `/done` captures it before it's gone.
- **Structure over chaos.** Consistent format means your 50th summary is as searchable as your first.
- **Two commands, zero friction.** No config, no setup, no workflow changes. Just `/done` and `/recall`.
- **Plain files, full control.** Everything lives in `~/.claude-done/` as Markdown. `grep` it, `git` it, back it up — it's yours.


## Credits

Inspired by [@shadcn](https://x.com/shadcn/status/2023812711151259772).

## License

MIT

