"""Load and validate the YAML config."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


class ConfigError(Exception):
    """Raised for a missing or malformed config. Fatal (non-zero exit)."""


@dataclass(frozen=True)
class FrontmatterConfig:
    essential: list[str]
    optional: list[str]


@dataclass(frozen=True)
class Config:
    source_vault: Path
    target_content: Path
    assets_dir: str
    frontmatter: FrontmatterConfig


def _require_str(data: dict, key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"config: '{key}' is required and must be a non-empty string")
    return value


def _str_list(value, key: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        raise ConfigError(f"config: '{key}' must be a list of strings")
    return list(value)


def load_config(path: Path) -> Config:
    if not path.is_file():
        raise ConfigError(f"config file not found: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ConfigError(f"config: invalid YAML: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("config: top level must be a mapping")

    source_vault = Path(_require_str(raw, "source_vault")).expanduser()
    target_content = Path(_require_str(raw, "target_content")).expanduser()

    if not source_vault.is_dir():
        raise ConfigError(f"config: source_vault is not a directory: {source_vault}")

    assets_dir = raw.get("assets_dir", "assets")
    if not isinstance(assets_dir, str) or not assets_dir.strip():
        raise ConfigError("config: 'assets_dir' must be a non-empty string")

    fm_raw = raw.get("frontmatter") or {}
    if not isinstance(fm_raw, dict):
        raise ConfigError("config: 'frontmatter' must be a mapping")

    frontmatter = FrontmatterConfig(
        essential=_str_list(fm_raw.get("essential"), "frontmatter.essential"),
        optional=_str_list(fm_raw.get("optional"), "frontmatter.optional"),
    )

    return Config(
        source_vault=source_vault,
        target_content=target_content,
        assets_dir=assets_dir,
        frontmatter=frontmatter,
    )
