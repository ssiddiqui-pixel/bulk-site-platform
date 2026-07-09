# Bulk Social Gaming Site Platform

You are the build engine for a bulk website generation platform. You build social gaming (free-to-play) websites in batches. Every rule in this file is permanent and non-negotiable.

## Tech rules
- HTML5 / CSS3 / vanilla JS only. No frameworks, no build step.
- Output to `builds/[site-name]/` (lowercase, hyphenated).
- Each site: index.html, games.html, 6 individual game pages, about.html (400+ words), contact.html, privacy.html (300+ words), terms.html (300+ words).
- Games come from `assets/games-data/game-data.csv`. Images (webp) from `assets/games-images/`. Every game embedded via iframe on its own page. Never external links to games.
- Games must OPEN IN AN IFRAME everywhere, on every build: clicking any game card (home, games list, related) launches the game in an on-site iframe modal/lightbox (with close + fullscreen), and each game's own page embeds it in an iframe. Never open a game in a new tab or navigate off-site to play. Keep exactly one iframe in each game page's static HTML (the modal is added on non-game pages only).
- Full SEO on every site: schema.org markup, OG tags, sitemap.xml, robots.txt, canonical URLs, E-E-A-T signals, responsive mobile-first.
- 300+ words on main pages, 150+ words per game page.
- No staging/Cloudways URLs anywhere in legal pages.

## Language rules (hard fail if violated)
- Allowed framing: social gaming, free-to-play, community, browser games, instant play.
- BANNED WORDS (case-insensitive, whole site): casino, gambling, betting, bet, wager, real money, deposit, withdrawal, odds, slots, payout, bonus, bonuses, rewards, jackpot, jackpots, win, wins, winnings. Never imply financial gain in any phrasing.
- Age gate: 21+ always. The string "18+" must never appear.

## Testimonial rules
- First person, never mention the brand name inside the testimonial text.
- Names from pool: Ayla, Remi, Kian, Suki, Noor, Teo, Mira, Joss, Leif, Zara + last initials B, D, F, H, K, M, P, R, T, W.
- Dates: Jan–Feb 2026.
- No name+initial combination may repeat within a batch. Check `state/registry.json` for combinations used in previous batches and avoid them until the pool is exhausted.

## Batch uniqueness rules (the core of this platform)
- NEVER build a site without a batch manifest. The manifest is generated first and locks in each site's differentiators.
- Each site in a batch must differ in ALL of: theme name, color palette (no shared primary hex), typography pairing, layout variant, brand voice, brand story angle, team bios, testimonial set, and game selection (minimize overlap; no two sites in a batch may share more than 2 games).
- Before generating a manifest, read `state/registry.json` and exclude everything already used in past batches.
- After a batch completes, append all used differentiators to `state/registry.json`.

## Available differentiator pools (extend registry as needed)
Layout variants: hero-fullbleed, hero-split, cards-grid-first, sidebar-nav, centered-minimal, magazine-rows, diagonal-sections, tabbed-showcase, single-scroll-anchor, mosaic-tiles.
Voice profiles: arcade-retro, cozy-lounge, esports-energy, minimalist-zen, playful-cartoon, premium-noir, tropical-breeze, sci-fi-neon, rustic-boardgame, urban-street.
Story angles: founded-by-friends, remote-team-worldwide, indie-studio-passion, community-first-origin, design-led-studio, accessibility-mission, nostalgia-revival, campus-project-grown, family-hobby-turned-studio, weekend-jam-origin.

## Build sequencing (per site)
Phase 1 — Foundation: index.html, base CSS with the assigned palette/typography, nav/footer shared markup, age gate (21+), games.html.
Phase 2 — Content depth: 6 game pages with iframes, about.html with assigned story angle and team bios, contact.html.
Phase 3 — Trust/legal: privacy.html, terms.html, sitemap.xml, robots.txt, schema markup pass.
Never attempt a full site in one pass. Complete each phase for a site before the next phase.

## State
- `state/sites.json`: per-site pipeline status (manifested / built / qa-passed / deployed / cert-approved / live).
- `state/registry.json`: permanent record of used themes, palettes, voices, story angles, testimonial combos.
- Update state files after every step. If a run is interrupted, resume from state — never rebuild finished sites.

## Content delivery style
Direct output, no filler. Every site's copy must be written fresh — never adapt another site's paragraph by swapping words.
