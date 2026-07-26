"""Scan a note body for Markdown image references and copy the referenced files.

Only images the note actually references are copied (not the whole shared assets
dir), and each is placed at the same relative subpath inside the leaf bundle so
the untouched Markdown link resolves as a Hugo page resource.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlparse

# Standard Markdown images: ![alt](target). Obsidian embeds (![[...]]) are out of
# scope for v1 and are intentionally not matched.
_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(\s*([^)]+?)\s*\)")


def _extract_target(inner: str) -> str:
    """Pull the path out of a Markdown image destination, dropping any title.

    Handles `<path with spaces>` and a trailing quoted "title" / 'title'.
    """
    inner = inner.strip()
    if inner.startswith("<"):
        end = inner.find(">")
        if end != -1:
            return inner[1:end].strip()
    match = re.match(r"""^(\S+)(?:\s+["'].*["'])?$""", inner)
    return match.group(1) if match else inner


def find_image_refs(content: str) -> list[str]:
    """Return the raw destinations of every standard Markdown image in the body."""
    return [_extract_target(m.group(1)) for m in _IMAGE_RE.finditer(content)]


def _is_local(ref: str) -> bool:
    """Local, relative reference — not a URL, absolute path, or data URI."""
    if not ref or ref.startswith(("/", "#")):
        return False
    parsed = urlparse(ref)
    return not parsed.scheme  # http, https, data, mailto… all have a scheme


def plan_asset_copies(
    note_dir: Path, content: str
) -> tuple[list[tuple[Path, PurePosixPath]], list[str]]:
    """Resolve referenced images relative to the note's directory.

    Returns (copies, warnings) where each copy is (source_file, relative_dest)
    and relative_dest is the path to reproduce inside the bundle. References that
    are remote/absolute are ignored; missing files and refs that escape the
    bundle (via `..`) produce warnings and are skipped.
    """
    copies: list[tuple[Path, PurePosixPath]] = []
    warnings: list[str] = []
    seen: set[str] = set()

    for ref in find_image_refs(content):
        if not _is_local(ref) or ref in seen:
            continue
        seen.add(ref)

        rel = PurePosixPath(unquote(ref))
        if ".." in rel.parts:
            warnings.append(
                f"asset {ref!r} escapes the bundle (contains '..'); not copied"
            )
            continue

        source = note_dir / Path(*rel.parts)
        if not source.is_file():
            warnings.append(f"missing asset {ref!r} referenced by {note_dir}")
            continue

        copies.append((source, rel))

    return copies, warnings


def copy_assets(bundle: Path, copies: list[tuple[Path, PurePosixPath]]) -> None:
    """Copy resolved assets into the bundle, preserving their relative subpath."""
    for source, rel in copies:
        dest = bundle / Path(*rel.parts)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
