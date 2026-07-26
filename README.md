# obsidian-hugo-helper

Convert flagged writings in an Obsidian vault into Hugo content.

A personal tool: it scans one vault, publishes only the notes you mark, and writes
each as a Hugo leaf bundle. Note bodies pass through as-is — v1 does no Markdown
format conversion (see [`.scratch/v1/spec.md`](.scratch/v1/spec.md) for scope).

## Install

```sh
uv sync
```

## Assumption for Obsidian settings

The tool does **no** Obsidian-syntax conversion in v1 — it assumes your vault is
authored as plain Markdown that Hugo already understands. Configure Obsidian so its
output matches these assumptions (**Settings → Files and links**, unless noted):

| Assumption the tool relies on | Obsidian setting |
| --- | --- |
| Links/images are standard Markdown (`![](...)`), not embeds (`![[...]]`) | **Use `[[Wikilinks]]`** → **off** |
| Image paths are relative to the note (`assets/pic.png`) | **New link format** → **Relative path to file** |
| Attachments live in an `assets/` folder beside the note | **Default location for new attachments** → **In subfolder under current folder**; **Subfolder name** → `assets` (must match `assets_dir` in the config) |
| Frontmatter is Hugo-ready | Author `title`, `date`, `tags`, … as Properties in the form Hugo expects (a note template / Templater makes this repeatable) |
| A note opts in via `publish_to.hugo` | Add the `publish_to` property (see below) |

Because bodies pass through untouched, anything Obsidian-specific that you leave in a
note — callouts (`> [!note]`), wikilinks (`[[Note]]`), embeds (`![[file]]`), Dataview
blocks — is copied verbatim and will **not** render correctly in Hugo. Keep published
notes to plain Markdown (or wait for the conversion work tracked in
[`.scratch/backlog.md`](.scratch/backlog.md)).

## Configure

Copy the example and edit it:

```sh
cp obsidian-hugo-helper.example.yaml obsidian-hugo-helper.yaml
```

```yaml
source_vault:   /path/to/Vault           # scanned for publish_to.hugo notes
target_content: /path/to/site/content    # Hugo content root
assets_dir:     assets                    # per-note-root attachments folder
frontmatter:
  essential: [title, date]                # missing -> note skipped + warned
  optional:  [tags, draft, description]    # kept if present
  # everything else (and the whole publish_to block) is stripped
```

## Flag a note for publishing

Add a `publish_to.hugo` key to the note's frontmatter. Its presence is the flag;
an optional `path` places the bundle under the content root (default: flat).

```yaml
---
title: My Great Post
date: 2026-07-25
tags: [go, hugo]
publish_to:
  hugo:
    path: posts/tech       # -> content/posts/tech/My Great Post/index.md
  wechat:                  # other targets are ignored by this tool
    account: main
---
```

## Run

```sh
uv run obsidian-hugo-helper --config obsidian-hugo-helper.yaml --dry-run   # preview
uv run obsidian-hugo-helper --config obsidian-hugo-helper.yaml             # write
uv run obsidian-hugo-helper --config obsidian-hugo-helper.yaml --verbose   # per-note output
```

Referenced images (standard Markdown `![](assets/x.png)`) are copied beside the
note's `index.md`, preserving their relative subpath. Runs are stateless: they
overwrite published bundles but never delete anything — un-publishing a note leaves
its old bundle for you to remove by hand.

## Develop

```sh
uv run pytest
```
