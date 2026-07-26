"""Command-line entry point for obsidian-hugo-helper."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import ConfigError, load_config
from .pipeline import Report, run

DEFAULT_CONFIG = "obsidian-hugo-helper.yaml"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="obsidian-hugo-helper",
        description="Convert flagged Obsidian vault notes into Hugo content.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(DEFAULT_CONFIG),
        help=f"path to the YAML config (default: ./{DEFAULT_CONFIG})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would be written without touching any files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="list every published note and skip in addition to the summary",
    )
    return parser


def _print_report(report: Report, verbose: bool) -> None:
    if report.dry_run:
        print("[dry-run] no files were written")

    if verbose:
        for line in report.published:
            print(f"PUBLISH {line}")
        for line in report.skipped:
            print(line)

    for line in report.warnings:
        print(f"WARN {line}", file=sys.stderr)

    print(
        f"Done: {len(report.published)} published, "
        f"{len(report.skipped)} skipped, "
        f"{len(report.warnings)} warning(s)."
    )


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    report = run(config, dry_run=args.dry_run)
    _print_report(report, verbose=args.verbose)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
