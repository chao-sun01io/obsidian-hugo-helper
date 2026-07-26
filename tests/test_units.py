from pathlib import Path

from obsidian_hugo_helper.assets import find_image_refs, plan_asset_copies
from obsidian_hugo_helper.config import FrontmatterConfig
from obsidian_hugo_helper.placement import bundle_dir, confine_relative
from obsidian_hugo_helper.select import _hugo_params
from obsidian_hugo_helper.transform import build_output_metadata

FM = FrontmatterConfig(essential=["title", "date"], optional=["tags", "draft"])


def test_hugo_params_detection():
    assert _hugo_params({"publish_to": {"hugo": {"path": "posts"}}}) == {"path": "posts"}
    assert _hugo_params({"publish_to": {"hugo": None}}) == {}
    assert _hugo_params({"publish_to": {"wechat": {}}}) is None
    assert _hugo_params({"publish_to": "hugo"}) is None
    assert _hugo_params({}) is None


def test_allowlist_strips_and_keeps():
    meta = {
        "title": "Hi",
        "date": "2026-01-01",
        "tags": ["a"],
        "secret": "x",
        "publish_to": {"hugo": {}},
    }
    out, missing = build_output_metadata(meta, FM)
    assert out == {"title": "Hi", "date": "2026-01-01", "tags": ["a"]}
    assert missing == []


def test_missing_essential_reported():
    _, missing = build_output_metadata({"title": "Hi"}, FM)
    assert missing == ["date"]


def test_confine_relative_blocks_escape():
    assert confine_relative("/posts/../../etc") == Path("posts/etc")
    assert confine_relative("") == Path(".")


def test_bundle_dir_flat_and_nested(tmp_path):
    note = tmp_path / "My Post.md"
    assert bundle_dir(tmp_path, {}, note) == tmp_path / "My Post"
    assert bundle_dir(tmp_path, {"path": "posts/tech"}, note) == tmp_path / "posts/tech/My Post"


def test_find_image_refs_handles_titles_and_angles():
    body = '![a](assets/x.png) ![b](<assets/y z.png>) ![c](assets/t.png "title") ![d](https://e/z.png)'
    assert find_image_refs(body) == ["assets/x.png", "assets/y z.png", "assets/t.png", "https://e/z.png"]


def test_plan_asset_copies_skips_remote_and_missing(tmp_path):
    (tmp_path / "assets").mkdir()
    (tmp_path / "assets" / "x.png").write_bytes(b"png")
    body = "![](assets/x.png) ![](https://e/z.png) ![](assets/missing.png)"
    copies, warnings = plan_asset_copies(tmp_path, body)
    assert [str(rel) for _, rel in copies] == ["assets/x.png"]
    assert any("missing.png" in w for w in warnings)
