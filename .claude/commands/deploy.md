# /deploy — Deploy site(s) to Cloudflare Pages

Arguments: $ARGUMENTS (a site name, or `batch` for all qa-passed sites in the current batch)

Requires env vars: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID (check they exist first; if missing, tell me and stop).

For each target site:
1. Verify `state/sites.json` shows "qa-passed". If not, refuse and say to run /qa first. Never deploy an un-QA'd site.
2. Create the Pages project if it doesn't exist:
   `npx wrangler pages project create [site-name] --production-branch=main`
3. Deploy:
   `npx wrangler pages deploy builds/[site-name] --project-name=[site-name]`
4. If a custom domain is listed for the site in `state/sites.json` under `domain`, attach it via the Cloudflare API (Pages project custom domains endpoint) and report the DNS records I need to confirm.
5. Update `state/sites.json`: status "deployed", store the pages.dev URL.
6. Report a table: site → live URL → custom domain status.

Deploy sites one at a time. If a deploy fails, diagnose from the wrangler error output, fix, retry — do not move on with a site in a broken state.
