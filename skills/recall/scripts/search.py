#!/usr/bin/env python3
"""
Search and list session summaries in ~/.claude-done/

Usage:
    search.py                          # List recent 10 entries
    search.py --last 5                 # List recent 5 entries
    search.py --keyword "auth"         # Full-text search
    search.py --date today             # Today's entries
    search.py --date 7d               # Last 7 days
    search.py --date 2026-01-01:2026-01-31  # Date range
    search.py --branch feat-auth       # Filter by branch (fuzzy)
"""

import argparse
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

DONE_DIR = Path.home() / ".claude-done"


def parse_filename(filename):
    """Extract date, branch, session_id, title from filename."""
    # Format: YYYY-MM-DD_branch_sessionid_kebab-title.md
    m = re.match(r"^(\d{4}-\d{2}-\d{2})_(.+?)_([a-f0-9]{8})_(.+)\.md$", filename)
    if not m:
        return None
    return {
        "date": m.group(1),
        "branch": m.group(2),
        "session_id": m.group(3),
        "title": m.group(4).replace("-", " ").title(),
        "filename": filename,
    }


def get_entries():
    """Load all valid entries from ~/.claude-done/, sorted by date desc."""
    if not DONE_DIR.is_dir():
        return []
    entries = []
    for f in sorted(DONE_DIR.iterdir(), reverse=True):
        if f.suffix == ".md":
            parsed = parse_filename(f.name)
            if parsed:
                parsed["path"] = str(f)
                entries.append(parsed)
    return entries


def filter_by_date(entries, date_arg):
    """Filter entries by date spec: 'today', 'Nd', or 'YYYY-MM-DD:YYYY-MM-DD'."""
    today = datetime.now().date()
    if date_arg == "today":
        start = end = today
    elif re.match(r"^\d+d$", date_arg):
        days = int(date_arg[:-1])
        start = today - timedelta(days=days - 1)
        end = today
    elif ":" in date_arg:
        parts = date_arg.split(":", 1)
        try:
            start = datetime.strptime(parts[0], "%Y-%m-%d").date()
            end = datetime.strptime(parts[1], "%Y-%m-%d").date()
        except ValueError:
            print(f"Invalid date range: {date_arg}", file=sys.stderr)
            return entries
    else:
        print(f"Unknown date format: {date_arg}", file=sys.stderr)
        return entries

    return [
        e for e in entries
        if start <= datetime.strptime(e["date"], "%Y-%m-%d").date() <= end
    ]


def filter_by_branch(entries, branch):
    """Filter entries where branch contains the search term (case-insensitive)."""
    branch_lower = branch.lower()
    return [e for e in entries if branch_lower in e["branch"].lower()]


def filter_by_keyword(entries, keyword):
    """Full-text search in file contents. Returns entries with matching context."""
    keyword_lower = keyword.lower()
    results = []
    for e in entries:
        try:
            content = Path(e["path"]).read_text(encoding="utf-8")
        except OSError:
            continue
        if keyword_lower in content.lower():
            # Find matching lines for context
            matches = []
            for i, line in enumerate(content.splitlines(), 1):
                if keyword_lower in line.lower():
                    matches.append((i, line.strip()))
            e = dict(e)
            e["matches"] = matches[:3]  # Show up to 3 matching lines
            results.append(e)
    return results


def format_entry(e, show_matches=False):
    """Format a single entry for display."""
    line = f"  {e['date']}  [{e['branch']}]  {e['title']}"
    line += f"\n  {e['path']}"
    if show_matches and e.get("matches"):
        for lineno, text in e["matches"]:
            line += f"\n    L{lineno}: {text[:120]}"
    return line


def main():
    parser = argparse.ArgumentParser(description="Search ~/.claude-done/ session summaries")
    parser.add_argument("--keyword", help="Full-text search keyword")
    parser.add_argument("--date", help="Date filter: today, Nd, or YYYY-MM-DD:YYYY-MM-DD")
    parser.add_argument("--branch", help="Filter by branch name (fuzzy match)")
    parser.add_argument("--last", type=int, default=0, help="Show last N entries")
    args = parser.parse_args()

    if not DONE_DIR.is_dir():
        print("No session summaries found. Run /done to create your first one.")
        return

    entries = get_entries()
    if not entries:
        print("No session summaries found in ~/.claude-done/")
        return

    show_matches = False

    if args.date:
        entries = filter_by_date(entries, args.date)
    if args.branch:
        entries = filter_by_branch(entries, args.branch)
    if args.keyword:
        entries = filter_by_keyword(entries, args.keyword)
        show_matches = True

    # Default to last 10 if no specific filter narrows results
    limit = args.last if args.last > 0 else 10
    if not (args.keyword or args.date or args.branch):
        entries = entries[:limit]
    elif args.last > 0:
        entries = entries[:limit]

    if not entries:
        print("No matching entries found.")
        return

    print(f"Found {len(entries)} session(s):\n")
    for e in entries:
        print(format_entry(e, show_matches=show_matches))
        print()


if __name__ == "__main__":
    main()
