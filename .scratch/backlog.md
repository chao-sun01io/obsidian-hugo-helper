# obsidian-hugo-helper — backlog

Future improvements beyond v1. v1 scope is frozen in [`v1/spec.md`](v1/spec.md);
anything here was consciously deferred. Roughly ordered by likely value.

## Deferred from the v1 spec

- **Body / format conversion.** Obsidian embeds (`![[file]]`), wikilinks
  (`[[Note]]`), callouts (`> [!note]`), and Dataview blocks currently pass through
  untouched and will render wrong in Hugo. Convert them to Markdown / Hugo
  shortcodes. Biggest single lever for making arbitrary notes publishable.
  - Sub-item: handle Obsidian **image embeds** `![[pic.png]]` in the asset scanner
    (v1 only matches standard `![](...)`).
- **Filename / path slugification.** Bundle dir = note filename verbatim, so
  `My Great Post.md` → `/My%20Great%20Post/`. Add optional slugification (kebab,
  lowercase) with a config toggle; respect an explicit frontmatter `slug`.
- **Deal with multilingo** and default locale and language.
- **Stale cleanup / sync.** v1 is stateless overwrite — un-publishing or deleting a
  note leaves an orphan bundle. Add an optional manifest so removed notes' bundles
  (and their copied assets) can be cleaned up safely without touching hand-authored
  Hugo content.
- **Obsidian-CLI-backed selection.** `select.py` is already the seam. Once the
  official CLI stabilizes, allow richer selection (link graph, tags, "everything
  linked from a Published MOC") instead of just `publish_to.hugo`.
- **Frontmatter field mapping / synthesis.** Rename Obsidian keys to Hugo keys, and
  synthesize a `date` from file mtime when absent (instead of skipping).

## Surfaced during implementation

- **Per-run overrides.** `--source-vault` / `--target-content` flags to override the
  config for one-off runs; a `default_path` config key applied when a note omits
  `publish_to.hugo.path`.
- **`hugo:` scalar shorthand.** Today a non-mapping value under `hugo` is treated as
  empty params. Consider supporting `hugo: posts/tech` as shorthand for
  `hugo: {path: posts/tech}`.
- **Within-bundle asset staleness.** Re-runs overwrite `index.md` and referenced
  assets but never remove now-unreferenced files already in a bundle. Tie into the
  stale-cleanup manifest work above.
- **Asset scan fidelity.** The image regex is deliberately simple. Edge cases:
  reference-style images (`![alt][ref]`), HTML `<img>` tags, images inside fenced
  code blocks (currently would be matched even though they shouldn't be).
- **Report polish.** Machine-readable output (`--json`) and a summary of assets
  copied per note; optionally print relative paths instead of absolute.
- **Dev tooling.** No linter/formatter config yet — the repo trips default Flake8
  (79-col). Add `ruff`/`black` config (line length 88) so style is intentional, and
  wire `pytest` + lint into a pre-commit or CI check.
- **Encoding / edge inputs.** Confirm behavior on non-UTF-8 notes and notes with no
  frontmatter block at all.
