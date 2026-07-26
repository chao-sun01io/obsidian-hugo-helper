# obsidian-hugo-helper — v1 Spec

Status: ready-for-agent

Personal tool that converts flagged notes from a single Obsidian vault into content
for a single Hugo site. Selection and file placement are the core job; Markdown body
conversion is explicitly out of scope for v1.

## Purpose & scope

- Personal tool: **one Obsidian vault → one Hugo site**.
- **Selective** publishing — only flagged notes are converted.
- **Body Markdown passes through untouched.** No format/syntax conversion. Assumes notes
  are already general Markdown and that image references are standard Markdown
  (`![](assets/x.png)`), **not** Obsidian embeds (`![[…]]`).

## Selection

- Walk `source_vault` on the filesystem.
- A note is a Hugo candidate **iff its frontmatter `publish_to` is a map containing the
  key `hugo`**. Presence of the key is the flag; its value may be empty (defaults) or a
  map of Hugo params.
- `publish_to` is a namespaced map of publish targets (`hugo`, `wechat`, …). This tool
  reads only the `hugo` namespace and ignores siblings.
- The Obsidian CLI is **deferred**. `select.py` is the seam where a future CLI-backed
  selector can be swapped in.

## Frontmatter transform

- **Allowlist**: keep the fields listed under `frontmatter.essential` and
  `frontmatter.optional`. **Strip everything else, including the entire `publish_to`
  block.**
- A missing **essential** field → **skip the note and warn** (run continues).
- A missing **optional** field → simply omitted.
- Assumes the kept fields are already Hugo-compatible (no renaming, slug generation, or
  date synthesis in v1).

## Placement — Model B leaf bundles

- Each note becomes a Hugo **leaf bundle**:
  `content/[publish_to.hugo.path]/<notename>/index.md`.
- No `publish_to.hugo.path` → flat at content root: `content/<notename>/index.md`.
- `path` is relative to the content root; leading slashes and `..` are normalized and
  **confined under the content dir** (a note cannot write outside it).
- Bundle directory name = the note's filename (without `.md`). Slugification is deferred.

## Assets (in v1)

- Vault convention: images live in an `assets/` dir (name configurable) sharing the
  note's root.
- **Scan the body for Markdown image references and copy only referenced images** — not
  the whole shared `assets/` dir.
- **Preserve the reference's relative subpath inside the bundle** so the untouched link
  resolves as a Hugo page resource. e.g. `note.md` + `assets/diagram.png` →
  `.../index.md` + `.../assets/diagram.png`.

## Re-run semantics

- **Fully stateless overwrite.** Every run regenerates all currently-published bundles,
  overwriting them.
- **No manifest, no stale detection.** Un-publishing (removing `publish_to.hugo`) or
  deleting a note leaves its old bundle in `content/` for the user to remove by hand. The
  tool says nothing about leftovers.

## Warnings (within-run only)

- Missing essential field → skip note + warn.
- Destination collision (two published notes → same bundle path) → **skip all colliding
  notes** + warn, naming them and the contested path. Fix by giving one a
  `publish_to.hugo.path`.

## Config

YAML, passed via `--config` (default `./obsidian-hugo-helper.yaml`). Schema frozen for v1:

```yaml
source_vault:   /path/to/Vault           # dir to scan for publish_to.hugo notes
target_content: /path/to/site/content    # Hugo content root
assets_dir:     assets                    # per-note-root attachments folder name
frontmatter:
  essential: [title, date]                # missing → skip note + warn
  optional:  [tags, draft, description]    # kept if present
  # anything not listed here (and the whole publish_to block) is stripped
```

## CLI

- Single command, no subcommands.
- Flags: `--config PATH`, `--dry-run`, `-v/--verbose`.
  - `--dry-run`: full scan/selection/checks, print what would be written and all
    warnings, **touch no files**.
  - default output: summary line + warnings; verbose lists every published note and
    copied asset.
- Exit code `0` on normal completion **even if notes were skipped**; non-zero only on
  fatal errors (missing/invalid config, unreadable `source_vault`).

## Project

- `uv`-managed Python 3.11+ package, `src/` layout.
- Runtime dependency: `python-frontmatter` (with `PyYAML` underneath, reused for config).
- Console-script entry point (`obsidian-hugo-helper`). `pytest` for tests.
- Modules:
  - `__main__.py` — argparse CLI
  - `config.py` — load + validate YAML
  - `select.py` — walk vault, parse frontmatter, find `publish_to.hugo` (CLI seam)
  - `frontmatter.py` — allowlist/strip, essential-field check
  - `assets.py` — scan body for image refs, copy preserving subpath
  - `pipeline.py` — orchestrate, collisions, dry-run, warnings

```
obsidian-hugo-helper/
├── pyproject.toml
├── obsidian-hugo-helper.example.yaml
├── src/obsidian_hugo_helper/
│   ├── __main__.py
│   ├── config.py
│   ├── select.py
│   ├── frontmatter.py
│   ├── assets.py
│   └── pipeline.py
└── tests/
```

## Explicitly deferred (post-v1)

- Body/format conversion (wikilinks, embeds, callouts, Dataview).
- Filename/path slugification.
- Obsidian-CLI-backed selection.
- Stale cleanup / manifest-based sync.
- CI integration.
- Frontmatter field-mapping / auto-date synthesis.
