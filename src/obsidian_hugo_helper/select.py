"""Walk the vault and select notes flagged with `publish_to.hugo`.

This module is the seam where a future Obsidian-CLI-backed selector could be
swapped in: it is the only place that knows how candidate notes are discovered.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import frontmatter


@dataclass
class Note:
    path: Path
    metadata: dict
    content: str
    hugo_params: dict


def _hugo_params(metadata: dict) -> dict | None:
    """Return the note's Hugo params, or None if it is not a Hugo candidate.

    A note is a candidate iff its frontmatter `publish_to` is a mapping that
    contains the key `hugo`. The value under `hugo` may be empty/null (defaults)
    or a mapping of Hugo params.
    """
    publish_to = metadata.get("publish_to")
    if not isinstance(publish_to, dict) or "hugo" not in publish_to:
        return None
    params = publish_to.get("hugo")
    if isinstance(params, dict):
        return params
    return {}


def _is_hidden(path: Path, root: Path) -> bool:
    """True if any path segment below the root starts with a dot (.obsidian, .trash…)."""
    return any(part.startswith(".") for part in path.relative_to(root).parts)


def select_notes(source_vault: Path) -> tuple[list[Note], list[str]]:
    """Return (candidate notes, warnings) discovered under source_vault."""
    notes: list[Note] = []
    warnings: list[str] = []

    for path in sorted(source_vault.rglob("*.md")):
        if not path.is_file() or _is_hidden(path, source_vault):
            continue
        try:
            post = frontmatter.load(path)
        except Exception as exc:  # malformed frontmatter — skip, don't abort the run
            warnings.append(f"SKIP {path}: could not parse frontmatter: {exc}")
            continue

        params = _hugo_params(post.metadata)
        if params is None:
            continue

        notes.append(
            Note(
                path=path,
                metadata=dict(post.metadata),
                content=post.content,
                hugo_params=params,
            )
        )

    return notes, warnings
