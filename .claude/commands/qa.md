# /qa — Audit one site or a whole batch

Arguments: $ARGUMENTS (a site name, or `batch` for all sites in the current batch manifest)

Run every check and output a pass/fail table. Fix failures automatically, then re-run until clean.

1. Banned words (case-insensitive, all HTML files): casino, gambling, betting, bet, wager, real money, deposit, withdrawal, odds, slots, payout, bonus, bonuses, rewards, jackpot, jackpots, win, wins, winnings. Use grep with word boundaries; report file + line for each hit.
2. Age gate: "18+" appears zero times anywhere. "21+" appears on every HTML page.
3. Structure: index.html, games.html, exactly 6 game pages, about.html, contact.html, privacy.html, terms.html, sitemap.xml, robots.txt all present.
4. Iframes: each game page has exactly one iframe; no external game links (no target="_blank" hrefs pointing at game providers).
5. Word counts: about 400+, privacy/terms 300+, main pages 300+, game pages 150+.
6. SEO: every page has title, meta description, canonical, OG tags; JSON-LD present on index and about.
7. Legal pages contain no staging/Cloudways URLs.
8. If `batch`: cross-site duplication scan — flag any 8+ word sentence appearing in 2+ sites, any shared primary palette hex, any repeated testimonial name+initial.

After a clean pass, update `state/sites.json` to "qa-passed" for the audited site(s).
