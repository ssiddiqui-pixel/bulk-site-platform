# Bulk Social Gaming Site Platform

Batch-builds unique social gaming websites via Claude Code. 10 sites per batch, zero repetition, enforced by manifest + registry + cross-site QA.

## Setup (once)
1. Unzip this folder anywhere, e.g. `~/pipeline/`.
2. Copy your assets in:
   - `~/websites/assets/games-data/game-data.csv` → `assets/games-data/`
   - `~/websites/assets/games-images/*` → `assets/games-images/`
3. For deploys, export env vars in your shell profile:
   ```
   export CLOUDFLARE_API_TOKEN=...
   export CLOUDFLARE_ACCOUNT_ID=...
   ```
4. Open the folder in Claude Code: `cd ~/pipeline && claude`

## Usage

Build a batch by pasting names:
```
/bulksite Echo Arcade, Playwave Studio, Pixel Grove, Lumen Play, Fable Deck, Nimbus Games, Cinder Loop, Aurora Playhouse, Driftwood Play, Quartz Arcade
```

Or from the sheet — export your Google Sheet as CSV, save it to `config/site-names.csv` (columns: brand_name, status), then:
```
/bulksite sheet
```

Claude will show you the batch manifest (theme, palette, voice, layout, games, testimonials per site) and wait for your confirmation before building anything.

Re-audit anytime:
```
/qa batch
/qa pixel-grove
```

Deploy:
```
/deploy batch
/deploy pixel-grove
```

## How uniqueness is guaranteed
- `state/batch-manifest.json` locks every differentiator per site BEFORE any HTML is written.
- `state/registry.json` permanently records everything used, so future batches can't repeat past ones.
- Batch QA diff-scans all sites against each other: shared sentences, shared palette hexes, and repeated testimonial names are hard failures.

## Pipeline states (state/sites.json)
manifested → built → qa-passed → deployed → cert-approved → live

---

## Dashboard — build 10 sites from domains, download a ZIP
A local web app that turns a list of domains into finished sites and bundles them for download.
```
ANTHROPIC_API_KEY=sk-ant-... ./dashboard/run.sh      # then open http://localhost:5001
```
Paste up to 10 domains → it derives each brand, auto-assigns a unique theme/palette/font/layout/voice/games
(checked against `state/registry.json`), stamps the real domain into SEO, has Claude write the copy, builds each
site, runs QA, and produces one ZIP. See `dashboard/README.md`.

## Generators & scripts
- `scripts/build_rich.py` — the rich multi-page generator (home, games, 6 game pages, about, contact, FAQ,
  responsible-play, privacy, terms). Per-site layouts; games open in an on-site iframe modal. Build any site:
  `python3 scripts/build_rich.py <slug>`.
- `scripts/build_lumen_rich.py` — dedicated rich build for the Lumen Play example.
- `scripts/qa.py` — the QA gate (banned words, 21+, one iframe per game page, cross-site uniqueness). Scoped to
  the current `state/batch-manifest.json`.

## Requirements
- Python 3.9+ (the dashboard installs Flask + the Anthropic SDK into `dashboard/.venv` on first run).
- A Claude API key for the dashboard (`ANTHROPIC_API_KEY`).
- The `.venv`, `builds/`, and `dashboard/output/` are gitignored — clone, then run `./dashboard/run.sh`.

## Deploy the built sites
Each built site is static and must be hosted at its **own domain root** (absolute paths). Deploy to Cloudflare
Pages (the `/deploy` command), Netlify, or any static host — one site per domain.
