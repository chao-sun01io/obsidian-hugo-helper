from pathlib import Path

import frontmatter

from obsidian_hugo_helper.config import Config, FrontmatterConfig
from obsidian_hugo_helper.pipeline import run

FM = FrontmatterConfig(essential=["title", "date"], optional=["tags"])


def _write_note(path: Path, metadata: dict, body: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post(body, **metadata)
    path.write_text(frontmatter.dumps(post), encoding="utf-8")


def _config(vault: Path, content: Path) -> Config:
    return Config(source_vault=vault, target_content=content, assets_dir="assets", frontmatter=FM)


def test_publishes_flagged_note_with_asset(tmp_path):
    vault = tmp_path / "vault"
    content = tmp_path / "content"
    (vault / "assets").mkdir(parents=True)
    (vault / "assets" / "d.png").write_bytes(b"img")
    _write_note(
        vault / "post.md",
        {"title": "T", "date": "2026-01-01", "secret": "x", "publish_to": {"hugo": {"path": "posts"}}},
        "Hello ![](assets/d.png)",
    )
    # A note not flagged for hugo must be ignored.
    _write_note(vault / "draft.md", {"title": "D", "date": "2026-01-01"})

    report = run(_config(vault, content))

    index = content / "posts" / "post" / "index.md"
    assert index.is_file()
    published = frontmatter.load(index)
    assert published.metadata == {"title": "T", "date": "2026-01-01"}  # stripped secret + publish_to
    assert "publish_to" not in published.metadata
    assert (content / "posts" / "post" / "assets" / "d.png").read_bytes() == b"img"
    assert len(report.published) == 1
    assert report.skipped == []


def test_missing_essential_is_skipped(tmp_path):
    vault = tmp_path / "vault"
    content = tmp_path / "content"
    _write_note(vault / "bad.md", {"title": "T", "publish_to": {"hugo": {}}})

    report = run(_config(vault, content))

    assert not (content / "bad").exists()
    assert len(report.published) == 0
    assert any("missing essential" in s for s in report.skipped)


def test_collision_skips_all(tmp_path):
    vault = tmp_path / "vault"
    content = tmp_path / "content"
    _write_note(vault / "a" / "dup.md", {"title": "A", "date": "2026-01-01", "publish_to": {"hugo": {}}})
    _write_note(vault / "b" / "dup.md", {"title": "B", "date": "2026-01-01", "publish_to": {"hugo": {}}})

    report = run(_config(vault, content))

    assert not (content / "dup").exists()
    assert len(report.published) == 0
    assert len(report.skipped) == 2
    assert any("COLLISION" in w for w in report.warnings)


def test_dry_run_writes_nothing(tmp_path):
    vault = tmp_path / "vault"
    content = tmp_path / "content"
    _write_note(vault / "post.md", {"title": "T", "date": "2026-01-01", "publish_to": {"hugo": {}}})

    report = run(_config(vault, content), dry_run=True)

    assert not content.exists()
    assert len(report.published) == 1
    assert report.dry_run is True
