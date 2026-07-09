# Bulk Site Builder — Dashboard

A local web app: paste up to **10 domains**, it builds **10 unique free-to-play social-gaming sites**, then hands you **one ZIP** with all of them.

## What it does
For each domain you enter:
1. Derives the **brand name** from the domain (`echo-arcade.com` → "Echo Arcade").
2. Auto-assigns a **unique** theme, palette, font pairing, layout, brand voice, story angle, 6 games, testimonials and team — checked against `state/registry.json` so nothing repeats across batches.
3. **Stamps the real domain** into every page's `canonical`, `og:url`, `sitemap.xml`, and `robots.txt`.
4. Calls the **Claude API** to write all the unique copy in that site's voice (banned-word-safe, 21+).
5. Builds the full site (`scripts/build_rich.py`) — home, games, 6 game pages, about, contact, FAQ, responsible-play, privacy, terms — with games opening in an on-site **iframe modal**.
6. Runs the **QA gate** across the batch (banned words, 21+, one iframe per game page, cross-site uniqueness).
7. Bundles every site into a single downloadable **ZIP**.

## Setup (once)
1. Get a Claude API key at <https://console.anthropic.com> (pay-as-you-go).
2. From the platform root:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-... ./dashboard/run.sh
   ```
   (First run creates the venv and installs Flask + the Anthropic SDK.)
3. Open <http://localhost:5001>.

## Use
- Paste up to 10 domains (one per line) → **Build sites**.
- Watch per-site progress; when finished, click **Download ZIP**.
- Each site in the ZIP is a folder deployable at its own domain root (see the top-level deploy repo's README).

## Config
- `ANTHROPIC_API_KEY` (required) — your Claude key.
- `DASHBOARD_MODEL` (optional) — model id, default `claude-sonnet-4-6`. Use `claude-opus-4-8` for max quality (higher cost).
- `PORT` (optional) — default `5001`.

## Cost (rough)
Each site ≈ one Claude call (~4–8k output tokens). A 10-site batch on Sonnet is typically well under ~$1; Opus is a few times that. Exact cost depends on current pricing.

## Notes
- Runs locally; your API key and game data never leave your machine.
- Games load from Play'n Go's servers (third-party iframes) — they may show blank on `localhost` but render on a real deployed domain.
- Built sites land in `../builds/<slug>/`; ZIPs in `./output/`.
- To host this for teammates later, put `app.py` behind a production WSGI server (gunicorn) with the API key as a server secret and add auth.
