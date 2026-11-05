#!/usr/bin/env python3
"""
Auto-generates blogs/index.json from all Markdown files in blogs/*.md.
Usage:
    python3 scripts/sync_blogs.py
"""

import json
import math
import os
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BLOGS_DIR = ROOT_DIR / "blogs"
INDEX_FILE = BLOGS_DIR / "index.json"


def parse_front_matter(md_text: str):
    """Parse simple YAML front matter delimited by --- at the top of a Markdown file."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", md_text, re.DOTALL)
    if not match:
        return {}, md_text

    fm_raw, body = match.group(1), match.group(2)
    meta = {}
    for line in fm_raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()

        # Parse JSON-like lists e.g. ["a", "b"]
        if val.startswith("[") and val.endswith("]"):
            try:
                meta[key] = json.loads(val)
                continue
            except Exception:
                pass

        # Strip surrounding quotes
        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]

        meta[key] = val

    return meta, body.strip()


def estimate_read_time(text: str) -> str:
    words = len(re.findall(r"\w+", text))
    minutes = max(1, math.ceil(words / 200))
    return f"{minutes} min read"


def main():
    BLOGS_DIR.mkdir(parents=True, exist_ok=True)
    posts = []

    for md_path in sorted(BLOGS_DIR.glob("*.md"), reverse=True):
        raw = md_path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)

        slug = meta.get("id") or md_path.stem
        title = meta.get("title") or md_path.stem.replace("-", " ").title()
        date_str = meta.get("date") or "2026-01-01"
        display_date = meta.get("displayDate") or date_str
        category = meta.get("category") or "Engineering"
        tags = meta.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        # Auto-extract summary from first paragraph if not provided in front matter
        summary = meta.get("summary")
        if not summary:
            first_para = next(
                (
                    p.strip()
                    for p in body.split("\n\n")
                    if p.strip() and not p.strip().startswith("#")
                ),
                "",
            )
            summary = re.sub(r"[*_`#]", "", first_para)[:220]

        read_time = meta.get("readTime") or estimate_read_time(body)

        post_entry = {
            "id": slug,
            "title": title,
            "date": date_str,
            "displayDate": display_date,
            "readTime": read_time,
            "category": category,
            "tags": tags,
            "summary": summary,
            "file": f"./blogs/{md_path.name}",
        }
        if meta.get("externalUrl"):
            post_entry["externalUrl"] = meta["externalUrl"]

        posts.append(post_entry)

    # Sort newest first by ISO date string
    posts.sort(key=lambda x: x.get("date", ""), reverse=True)

    INDEX_FILE.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Synced {len(posts)} blog posts -> {INDEX_FILE.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()

