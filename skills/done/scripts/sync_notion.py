#!/usr/bin/env python3
"""Sync a markdown summary to Notion as a child page.

Uses only Python standard library (urllib, json, argparse).
Reads config from ~/.claude-done/config.json for notion_token and notion_page_id.
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error

CONFIG_PATH = os.path.expanduser("~/.claude-done/config.json")
NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def parse_markdown_to_blocks(text):
    """Convert markdown text to Notion block objects.

    Skips the first H1 heading since it's used as the page title.
    """
    blocks = []
    lines = text.split("\n")
    i = 0
    skipped_title = False
    while i < len(lines):
        line = lines[i]

        # Heading 2
        if line.startswith("## "):
            blocks.append(make_heading(line[3:].strip(), level=2))
            i += 1
            continue

        # Heading 3
        if line.startswith("### "):
            blocks.append(make_heading(line[4:].strip(), level=3))
            i += 1
            continue

        # Heading 1 — skip the first one (it's the page title)
        if line.startswith("# "):
            if not skipped_title:
                skipped_title = True
                i += 1
                continue
            blocks.append(make_heading(line[2:].strip(), level=1))
            i += 1
            continue

        # To-do item: - [ ] or - [x]
        todo_match = re.match(r"^[-*]\s+\[([ xX])\]\s+(.*)", line)
        if todo_match:
            checked = todo_match.group(1).lower() == "x"
            blocks.append(make_todo(todo_match.group(2).strip(), checked))
            i += 1
            continue

        # Bulleted list item
        if re.match(r"^[-*]\s+", line):
            content = re.sub(r"^[-*]\s+", "", line).strip()
            if content:
                blocks.append(make_bulleted_list(content))
            i += 1
            continue

        # Bold metadata lines like **Date:** value
        bold_match = re.match(r"^\*\*(.+?):\*\*\s*(.*)", line)
        if bold_match:
            label = bold_match.group(1)
            value = bold_match.group(2)
            blocks.append(make_paragraph(f"{label}: {value}"))
            i += 1
            continue

        # Code block
        if line.startswith("```"):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            blocks.append(make_code("\n".join(code_lines), lang or "plain text"))
            continue

        # Empty line — skip
        if not line.strip():
            i += 1
            continue

        # Default: paragraph
        blocks.append(make_paragraph(line))
        i += 1

    return blocks


def rich_text(content):
    """Create a Notion rich_text array from a string, handling inline code and bold."""
    segments = []
    # Split by inline code first
    parts = re.split(r"(`[^`]+`)", content)
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            segments.append({
                "type": "text",
                "text": {"content": part[1:-1]},
                "annotations": {"code": True},
            })
        else:
            # Handle bold within non-code parts
            bold_parts = re.split(r"(\*\*[^*]+\*\*)", part)
            for bp in bold_parts:
                if bp.startswith("**") and bp.endswith("**"):
                    segments.append({
                        "type": "text",
                        "text": {"content": bp[2:-2]},
                        "annotations": {"bold": True},
                    })
                elif bp:
                    segments.append({
                        "type": "text",
                        "text": {"content": bp},
                    })
    return segments


def make_heading(text, level=2):
    key = f"heading_{level}"
    return {
        "object": "block",
        "type": key,
        key: {"rich_text": rich_text(text)},
    }


def make_paragraph(text):
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text(text)},
    }


def make_bulleted_list(text):
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text(text)},
    }


def make_todo(text, checked=False):
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {"rich_text": rich_text(text), "checked": checked},
    }


def make_code(text, language="plain text"):
    # Notion limits rich_text content to 2000 chars per segment
    segments = []
    for i in range(0, len(text), 2000):
        segments.append({"type": "text", "text": {"content": text[i:i+2000]}})
    return {
        "object": "block",
        "type": "code",
        "code": {"rich_text": segments, "language": language},
    }


def create_notion_page(token, parent_page_id, title, blocks):
    """Create a child page under the given parent page."""
    # Notion API limits to 100 blocks per request
    children = blocks[:100]

    payload = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": [{"text": {"content": title}}]
        },
        "children": children,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{NOTION_API}/pages",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        },
        method="POST",
    )

    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode("utf-8"))
    page_id = result["id"]
    url = result.get("url", f"https://notion.so/{page_id.replace('-', '')}")

    # Append remaining blocks in batches of 100
    remaining = blocks[100:]
    while remaining:
        batch = remaining[:100]
        remaining = remaining[100:]
        append_payload = {"children": batch}
        append_data = json.dumps(append_payload).encode("utf-8")
        append_req = urllib.request.Request(
            f"{NOTION_API}/blocks/{page_id}/children",
            data=append_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Notion-Version": NOTION_VERSION,
            },
            method="PATCH",
        )
        urllib.request.urlopen(append_req)

    return url


def main():
    parser = argparse.ArgumentParser(description="Sync markdown summary to Notion")
    parser.add_argument("--title", required=True, help="Page title")
    parser.add_argument("--file", required=True, help="Path to markdown file")
    args = parser.parse_args()

    # Load config
    try:
        config = load_config()
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading config: {e}", file=sys.stderr)
        sys.exit(1)

    token = config.get("notion_token")
    page_id = config.get("notion_page_id")

    if not token:
        print("Error: notion_token not found in config", file=sys.stderr)
        sys.exit(1)
    if not page_id:
        print("Error: notion_page_id not found in config", file=sys.stderr)
        sys.exit(1)

    # Read markdown file
    try:
        with open(args.file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Parse and create page
    blocks = parse_markdown_to_blocks(content)

    try:
        url = create_notion_page(token, page_id, args.title, blocks)
        print(url)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"Notion API error ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
