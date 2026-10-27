# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/Tiany-ii/github-hotboard/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.1.0
[1.0.0]: https://github.com/Tiany-ii/github-hotboard/releases/tag/v1.0.0
