# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.3] - 2026-10-27

### Fixed

- **HTML tables were never closed**, so the browser nested the entire rest of the README inside the
  last cell. A 9-row table became 1,600px wide, pushed the sidebar off-screen and made the page look
  like it overflowed. The parser now reads an HTML table up to `</table>` and rebuilds its rows.
- Side effect of the same bug: the table of contents only listed a handful of headings, because the
  headings after the table were swallowed into it.

## [1.2.2] - 2026-10-27

### Fixed

- README tables wrap to the container width again instead of scrolling horizontally. The previous
  fix turned tables into their own scroll box, which forced readers to drag sideways to see a row.
  Cells now break long words, so even a 200-character URL fits.
- The detail sidebar could collapse to zero height in some WebView2 builds (`max-height` +
  `overflow` on the sticky wrapper), leaving an empty right column.

## [1.2.1] - 2026-10-27

### Fixed

- The detail sidebar stopped following the scroll, leaving an empty column on the right. `position:
  sticky` was applied directly to the grid item, which some WebView2 builds ignore; it now lives on
  an inner wrapper while the grid item stretches to full row height.
- When the sidebar has no visible cards, the content column now takes the full width instead of
  reserving an empty 300px column.

## [1.2.0] - 2026-10-27

### Changed

- The detail view now uses the same content width as the list view (`--content-max: 1500px`).
  It was capped at 1120px, which left a 200px empty band on each side of a wide window and made
  the layout jump when opening a project.

## [1.1.1] - 2026-10-27

### Fixed

- Wide tables in a README no longer widen the detail drawer. A README with a multi-column
  link table used to expand the content to ~1,600px inside a ~750px column, which produced a
  horizontal scrollbar and clipped text. Tables now scroll inside their own box, and long URLs
  wrap instead of pushing the layout.

## [1.1.0] - 2026-10-27

### Added

- **Cache expiry.** Translation and AI summary entries that have not been opened for 30 days are
  removed on the next launch. "Opened" means visiting that project's detail page, so projects you
  actually use are never evicted. Cleanup runs at most once per day.

### Changed

- Cached translations now record a last-access time; the description cache stores
  `{ zh, t }` instead of a bare string (old entries are still read correctly).

## [1.0.0] - 2026-10-27

First public release.

### Added

- **Boards** — trending, new projects, categories, DeepSeek plugin ecosystem, and a personal
  watchlist, plus a daily brief that renews itself each morning.
- **Watchlist change alerts** — star deltas, new commits, issue spikes and stale repositories,
  computed from already-fetched data with zero extra API calls.
- **Bilingual README** — original / side-by-side / Chinese only, aligned per block.
- **AI summary card** — combines README text with stars, forks, open issues, last push and
  license. Configurable model (`deepseek-flash` / `deepseek-v4-pro`) and thinking mode.
- **One-click download** — release assets or source ZIP, native folder picker, live progress,
  automatic unpacking, no overwriting of existing folders.
- **Local-first storage** — WebView2 profile by default, `./data` in portable mode. No account,
  no telemetry.
- **Multiple API keys** — store and switch between up to eight DeepSeek keys.
- **Interface** — light and dark themes, design tokens for radius / type / spacing / motion,
  keyboard reachable rows, contrast-checked dark mode.

### Known issues

- Windows only.
- No automated tests or CI.
- Binary is not code-signed, so SmartScreen warns on first run.

[Unreleased]: https://github.com/Tiany-ii/github-hotboard/compare/v1.2.3...HEAD
[1.2.3]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.2.3
[1.2.2]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.2.2
[1.2.1]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.2.1
[1.2.0]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.2.0
[1.1.1]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.1.1
[1.1.0]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.1.0
[1.0.0]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.0.0
