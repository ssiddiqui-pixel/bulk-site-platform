# /bulksite — Build a batch of unique social gaming sites

Arguments: $ARGUMENTS (either a comma-separated list of brand names, or `sheet` to read from `config/site-names.csv`)

Follow these steps exactly. Do not skip the manifest.

## Step 1 — Load names
- If argument is `sheet`, read `config/site-names.csv` (one brand name per row, first column). Take all rows with status column empty or "pending".
- Otherwise parse the comma-separated names from the arguments.
- Confirm the list back before proceeding (count + names).

## Step 2 — Generate the batch manifest
- Read `state/registry.json`. Note every theme, palette hex, voice, story angle, layout, and testimonial combo already used.
- Read `assets/games-data/game-data.csv` and list available games.
- Create `state/batch-manifest.json` assigning each brand:
  - `theme`: unique evocative theme name (never used before)
  - `palette`: 4 hex values (primary, secondary, accent, background) — no primary hex shared with any other site in this batch or in the registry
  - `typography`: a Google Fonts pairing unique within the batch
  - `layout`: one layout variant from CLAUDE.md pools, unique within the batch
  - `voice`: one voice profile, unique within the batch
  - `story`: one story angle, unique within the batch
  - `games`: 6 games; no two sites in the batch share more than 2 games
  - `testimonials`: 3 name+initial combos, none repeated in batch or registry
  - `team`: 3 invented team member names (not from testimonial pool)
- Show me a summary table of the manifest and STOP for my confirmation before building.

## Step 3 — Build each site (sequential, phased)
For each site in the manifest, in order:
- Phase 1: builds/[site]/index.html, style.css (assigned palette + typography + layout), shared nav/footer, persistent 21+ age gate, games.html.
- Phase 2: 6 game pages with iframe embeds and 150+ words each (copy written in the assigned voice), about.html (400+ words, assigned story angle, team bios), contact.html.
- Phase 3: privacy.html (300+), terms.html (300+), sitemap.xml, robots.txt, schema.org JSON-LD on all pages, OG tags, canonical URLs.
- Update `state/sites.json` to "built" after Phase 3.
- Then move to the next site. Never interleave sites.

## Step 4 — Batch QA (hard gate)
Run these checks across the whole batch and report a pass/fail table:
- Banned-word grep (case-insensitive) across every HTML file, per CLAUDE.md list.
- "18+" must appear zero times; "21+" must appear on every page.
- Every game page contains exactly one iframe.
- sitemap.xml and robots.txt exist per site.
- Cross-site duplication: no sentence of 8+ words appears in more than one site; no shared primary hex; no repeated testimonial name+initial.
- Word count minimums met.
Fix any failures and re-run QA until clean.

## Step 5 — Commit state
- Append all used differentiators to `state/registry.json`.
- Set each site to "qa-passed" in `state/sites.json`.
- If names came from the sheet CSV, mark those rows "built".
- Report final summary: sites built, location, QA status.
