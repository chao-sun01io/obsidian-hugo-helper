"""Orchestrate selection, transformation, collision handling and writing."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter

from .assets import copy_assets, plan_asset_copies
from .config import Config
from .placement import bundle_dir
from .select import Note, select_notes
from .transform import build_output_metadata


@dataclass
class Report:
    published: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    dry_run: bool = False


def _write_note(note: Note, output_metadata: dict, bundle: Path) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(note.content, **output_metadata)
    text = frontmatter.dumps(post)
    (bundle / "index.md").write_text(text + "\n", encoding="utf-8")


def run(config: Config, *, dry_run: bool = False) -> Report:
    report = Report(dry_run=dry_run)

    notes, warnings = select_notes(config.source_vault)
    report.warnings.extend(warnings)

    # Stage 1: drop notes missing an essential field.
    survivors: list[tuple[Note, dict, Path]] = []
    for note in notes:
        output_metadata, missing = build_output_metadata(
            note.metadata, config.frontmatter
        )
        if missing:
            report.skipped.append(
                f"SKIP {note.path}: missing essential field(s): {', '.join(missing)}"
            )
            continue
        dest = bundle_dir(config.target_content, note.hugo_params, note.path)
        survivors.append((note, output_metadata, dest))

    # Stage 2: destination collisions -> skip ALL notes in the group.
    by_dest: dict[Path, list[tuple[Note, dict, Path]]] = defaultdict(list)
    for item in survivors:
        by_dest[item[2]].append(item)

    for dest, group in by_dest.items():
        if len(group) > 1:
            sources = ", ".join(str(n.path) for n, _, _ in group)
            report.warnings.append(
                f"COLLISION {dest}: {sources} — skipped all; "
                f"disambiguate with publish_to.hugo.path"
            )
            for note, _, _ in group:
                report.skipped.append(f"SKIP {note.path}: destination collision")
            continue

        note, output_metadata, _ = group[0]
        copies, asset_warnings = plan_asset_copies(note.path.parent, note.content)
        report.warnings.extend(asset_warnings)

        if not dry_run:
            _write_note(note, output_metadata, dest)
            copy_assets(dest, copies)

        rel_dest = dest / "index.md"
        assets_note = f" (+{len(copies)} asset(s))" if copies else ""
        report.published.append(f"{note.path} -> {rel_dest}{assets_note}")

    return report
