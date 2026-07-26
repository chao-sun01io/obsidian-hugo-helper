"""Frontmatter allowlist/strip and essential-field checking.

Named `transform` rather than `frontmatter` to avoid shadowing the
`python-frontmatter` library (which imports as `frontmatter`).
"""

from __future__ import annotations

from .config import FrontmatterConfig


def build_output_metadata(
    metadata: dict, fm: FrontmatterConfig
) -> tuple[dict, list[str]]:
    """Apply the allowlist and check essential fields.

    Returns (output_metadata, missing_essential). Only keys listed as essential
    or optional survive; everything else (including the whole `publish_to` block)
    is stripped. `missing_essential` lists essential keys absent from the note.
    """
    missing = [key for key in fm.essential if key not in metadata]
    allowed = set(fm.essential) | set(fm.optional)
    output = {key: value for key, value in metadata.items() if key in allowed}
    return output, missing
