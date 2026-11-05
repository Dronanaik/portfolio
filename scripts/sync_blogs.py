#!/usr/bin/env python3
"""
Auto-generates blogs/index.json from all Markdown files in blogs/*.md.
Works with pure Markdown files (starting with # Title, no front matter needed!)
and preserves any existing category/tags/date fields already in blogs/index.json.
Usage:
    python3 scripts/sync_blogs.py
"""

import json
import math
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BLOGS_DIR = ROOT_DIR / "blogs"
INDEX_FILE = BLOGS_DIR / "index.json"


def parse_front_matter(md_text: str):
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

        if val.startswith("[") and val.endswith("]"):
            try:
                meta[key] = json.loads(val)
                continue
            except Exception:
                pass

        if (val.startswith('"') and val.endswith('"')) or (
            val.startswith("'") and val.endswith("'")
        ):
            val = val[1:-1]

        meta[key] = val

    return meta, body.strip()


def estimate_read_time(text: str) -> str:
    words = len(re.findall(r"\w+", text))
    minutes = max(1, math.ceil(words / 220))
    return f"{minutes} min read"


def main():
    BLOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing blogs/index.json to preserve user-edited tags/categories/dates
    existing_by_file = {}
    if INDEX_FILE.exists():
        try:
            for item in json.loads(INDEX_FILE.read_text(encoding="utf-8")):
                if item.get("file"):
                    existing_by_file[item["file"]] = item
        except Exception:
            pass

    posts = []
    for md_path in sorted(BLOGS_DIR.glob("*.md"), reverse=True):
        file_rel = f"./blogs/{md_path.name}"
        existing = existing_by_file.get(file_rel, {})

        raw = md_path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)

        h1_match = re.match(r"^#\s+(.+?)\s*(?:\n|$)", body)
        inferred_title = h1_match.group(1).strip() if h1_match else None

        slug = meta.get("id") or existing.get("id") or re.sub(r"^\d{4}-\d{2}-", "", md_path.stem)
        title = (
            meta.get("title")
            or inferred_title
            or existing.get("title")
            or md_path.stem.replace("-", " ").title()
        )
        date_str = meta.get("date") or existing.get("date") or "2026-11-04"
        display_date = meta.get("displayDate") or existing.get("displayDate") or date_str
        category = meta.get("category") or existing.get("category") or "AI & Engineering"
        tags = meta.get("tags") or existing.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        summary = meta.get("summary") or existing.get("summary")
        if not summary:
            paragraphs = [
                re.sub(r"\s+", " ", p.strip())
                for p in re.split(r"\n\s*\n", body)
                if p.strip()
                and not p.strip().startswith("#")
                and not p.strip().startswith(">")
            ]
            for p in paragraphs:
                if p.startswith("*") and p.endswith("*"):
                    continue
                summary = re.sub(r"[*_`]", "", p)[:240]
                break

        read_time = meta.get("readTime") or estimate_read_time(body)

        post_entry = {
            "id": slug,
            "title": title,
            "date": date_str,
            "displayDate": display_date,
            "readTime": read_time,
            "category": category,
            "tags": tags,
            "summary": summary or "",
            "file": file_rel,
        }
        if meta.get("externalUrl") or existing.get("externalUrl"):
            post_entry["externalUrl"] = meta.get("externalUrl") or existing.get("externalUrl")

        posts.append(post_entry)

    posts.sort(key=lambda x: x.get("date", ""), reverse=True)
    INDEX_FILE.write_text(json.dumps(posts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Synced {len(posts)} blog posts -> {INDEX_FILE.relative_to(ROOT_DIR)}")


if __name__ == "__main__":
    main()
