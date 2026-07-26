"""Resolve a note's destination leaf-bundle directory under the content root."""

from __future__ import annotations

from pathlib import Path, PurePosixPath


def confine_relative(value: str) -> Path:
    """Turn a config-supplied relative path into a safe path confined under the
    content root: drop empty/'.'/'..' segments and any leading slash.
    """
    parts = [
        part
        for part in PurePosixPath(str(value)).parts
        if part not in ("", ".", "..", "/")
    ]
    return Path(*parts)


def bundle_dir(target_content: Path, hugo_params: dict, note_path: Path) -> Path:
    """Destination leaf-bundle directory for a note.

    content/[publish_to.hugo.path]/<notename>/  (default flat when no path).
    """
    rel = confine_relative(hugo_params.get("path", "") or "")
    return target_content / rel / note_path.stem
