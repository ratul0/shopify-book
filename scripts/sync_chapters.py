#!/usr/bin/env python3
"""Synchronize Shopify book chapters between root copies, Hugo content, and navigation."""
from __future__ import annotations

import pathlib
import re
import sys
import urllib.parse
from typing import List, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
DOCS_DIR = CONTENT_DIR / "docs"
CHAPTER_PATTERN = re.compile(r"^(\d+)\s*-\s*(.+)\.md$")
INVALID_FILENAME_CHARS = re.compile(r"[\\/:*?\"<>|]")

DOCS_INTRO = (
    "This section collects the full Shopify app development playbook, guiding you from "
    "platform fundamentals through extensions, deployment, and monetization."
)
ROOT_INTRO = (
    "Welcome to a hands-on journey through Shopify app development. This book reframes "
    "the platform through familiar full-stack patterns so you can build production-ready "
    "apps with confidence."
)
ROOT_CLOSING = (
    "Work through the chapters in order or dive into the sections you need most, and refer "
    "back as your Shopify apps evolve."
)
ROOT_OVERVIEW = (
    "This curriculum walks you through building modern Shopify apps, mapping each concept "
    "to familiar full-stack patterns so you can ship production features faster."
)


def _find_first_h1(lines: List[str]) -> Tuple[int, str]:
    """Return index and text of the first H1 outside code fences."""
    in_code = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith("# "):
            return idx, stripped[2:].strip()
    raise ValueError("No H1 heading found")


def _sanitize_filename(title: str) -> str:
    cleaned = INVALID_FILENAME_CHARS.sub("", title).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _normalize_root_file(path: pathlib.Path, expected_number: int) -> Tuple[int, str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # Strip leading blank lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    h1_index, heading = _find_first_h1(lines)
    body_lines = lines[h1_index + 1 :]
    while body_lines and body_lines[0].strip() == "":
        body_lines.pop(0)
    normalized_lines = [f"# {heading}", "", *body_lines]
    normalized_text = "\n".join(normalized_lines).rstrip() + "\n"
    if normalized_text != text:
        path.write_text(normalized_text, encoding="utf-8")
    sanitized = _sanitize_filename(heading)
    expected_name = f"{expected_number:02d} - {sanitized}.md"
    if path.name != expected_name:
        new_path = path.with_name(expected_name)
        if new_path.exists() and new_path != path:
            raise FileExistsError(f"Target filename already exists: {new_path}")
        path.rename(new_path)
        path = new_path
    return expected_number, heading, path.name


def _gather_chapters() -> List[Tuple[int, str, str]]:
    candidates = []
    for file in ROOT.glob("*.md"):
        match = CHAPTER_PATTERN.match(file.name)
        if not match:
            continue
        number = int(match.group(1))
        candidates.append((number, file))
    candidates.sort(key=lambda item: item[0])
    chapters: List[Tuple[int, str, str]] = []
    for index, (_, path) in enumerate(candidates, start=1):
        normalized = _normalize_root_file(path, index)
        chapters.append(normalized)
    return chapters


def _write_docs_copy(number: int, heading: str, filename: str) -> None:
    src_path = ROOT / filename
    dest_path = DOCS_DIR / f"chapter-{number:02d}.md"
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(src_path.read_text(encoding="utf-8"), encoding="utf-8")


def _build_index_files(chapters: List[Tuple[int, str, str]]) -> None:
    if not chapters:
        return
    book_title = chapters[0][1]
    # content/docs/_index.md
    docs_lines = [
        "---",
        'title: "Documentation"',
        "bookCollapseSection: false",
        "weight: 1",
        "---",
        "",
        DOCS_INTRO,
        "",
    ]
    for number, heading, _ in chapters:
        docs_lines.append(f"- [{heading}](./chapter-{number:02d})")
    docs_text = "\n".join(docs_lines).rstrip() + "\n"
    (DOCS_DIR / "_index.md").write_text(docs_text, encoding="utf-8")

    # content/_index.md
    root_lines = [
        "---",
        f'title: "{book_title}"',
        "---",
        "",
        ROOT_INTRO,
        "",
        "## Chapter Guide",
        "",
    ]
    for number, heading, _ in chapters:
        root_lines.append(f"- [{heading}](./docs/chapter-{number:02d})")
    root_lines.extend(["", ROOT_CLOSING])
    root_text = "\n".join(root_lines).rstrip() + "\n"
    (CONTENT_DIR / "_index.md").write_text(root_text, encoding="utf-8")

    # index.md at project root
    index_lines = [
        "---",
        "layout: home",
        "---",
        "",
        f"# {book_title}",
        "",
        ROOT_OVERVIEW,
        "",
        "## Chapter Guide",
        "",
    ]
    for _, heading, filename in chapters:
        link = urllib.parse.quote(filename)
        index_lines.append(f"- [{heading}](./{link})")
    index_text = "\n".join(index_lines).rstrip() + "\n"
    (ROOT / "index.md").write_text(index_text, encoding="utf-8")


def main() -> int:
    try:
        chapters = _gather_chapters()
    except FileExistsError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    for number, heading, filename in chapters:
        _write_docs_copy(number, heading, filename)
    _build_index_files(chapters)
    return 0


if __name__ == "__main__":
    sys.exit(main())
