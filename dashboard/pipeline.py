"""Batch build pipeline for the dashboard.
domains -> auto-assigned manifest -> Claude-written copy -> build_rich -> QA -> zip."""
import os, sys, re, csv, json, zipfile, importlib, io

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
sys.path.insert(0, HERE)
import pools  # noqa

DEFAULT_MODEL = os.environ.get("DASHBOARD_MODEL", "claude-sonnet-4-6")
BANNED = ["casino","gambling","betting","bet","wager","real money","deposit","withdrawal","odds","slots",
          "payout","bonus","bonuses","rewards","jackpot","jackpots","win","wins","winnings"]

# ------------------------------------------------------------------ helpers
def derive_brand(domain):
    d = re.sub(r"^https?://", "", domain.strip().lower()).split("/")[0]
    d = re.sub(r"^www\.", "", d)
    core = d.rsplit(".", 1)[0] if "." in d else d          # drop TLD
    parts = re.split(r"[-_.]+", core)
    if len(parts) == 1:  # split camelCase-ish or leave as one word, title-cased
        parts = re.findall(r"[a-z]+|[0-9]+", parts[0]) or [parts[0]]
    return " ".join(p.capitalize() for p in parts if p)

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def clean_games():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "assets/games-data/game-data.csv"))))
    out = []
    for r in rows:
        low = r["game_name"].lower()
        if not any(re.search(r"\b"+re.escape(b)+r"\b", low) for b in BANNED):
            out.append(r)
    return out

def _rot(seq, i):  # deterministic rotation without RNG
    return seq[i % len(seq)]

# ------------------------------------------------------------------ manifest
def assign_manifest(domains):
    reg = json.load(open(os.path.join(ROOT, "state/registry.json")))
    used_hex = set(h.lower() for h in reg.get("primary_hexes", []))
    used_theme = set(reg.get("themes", []))
    used_combo = set(c.lower() for c in reg.get("testimonial_combos", []))
    games = clean_games()

    palettes = [p for p in pools.PALETTES if p["primary"].lower() not in used_hex] or pools.PALETTES
    sites, combo_pool, gi, ti, ci = [], [], 0, 0, 0
    # build a fresh testimonial-combo pool (skip registry-used, skip in-batch dups)
    for f in pools.TESTI_FIRST:
        for ini in pools.TESTI_INIT:
            c = f"{f} {ini}."
            if c.lower() not in used_combo:
                combo_pool.append(c)

    for i, dom in enumerate(domains):
        brand = derive_brand(dom)
        slug = slugify(brand) or f"site-{i+1}"
        # unique theme
        while True:
            theme = f"{_rot(pools.THEME_ADJ, i+ti)} {_rot(pools.THEME_NOUN, i)}"
            if theme not in used_theme: break
            ti += 1
        used_theme.add(theme)
        # games: 6 disjoint per site (no cross-site overlap at all)
        gsel = games[gi:gi+6]; gi += 6
        if len(gsel) < 6:  # wrap around if we run low
            gsel = (games[gi-6:] + games)[:6]
        # testimonials: 3 fresh combos
        tsel = combo_pool[ci:ci+3]; ci += 3
        # team: 3 names, first names distinct from testimonial pool
        team = [f"{_rot(pools.TEAM_FIRST, i*3+k+i)} {_rot(pools.TEAM_LAST, i*3+k)}" for k in range(3)]
        sites.append({
            "brand": brand, "slug": slug,
            "domain": re.sub(r"^https?://","", dom.strip()).rstrip("/"),
            "theme": theme,
            "palette": palettes[i % len(palettes)],
            "typography": _rot(pools.FONT_PAIRS, i),
            "layout": _rot(pools.LAYOUTS, i),
            "voice": _rot(pools.VOICES, i),
            "story": _rot(pools.STORIES, i),
            "team": team,
            "testimonials": tsel,
            "games": [g["game_name"] for g in gsel],
            "games_resolved": [{"name":g["game_name"],"slug":g["slug"],"image":g["image"]} for g in gsel],
        })
    manifest = {"batch_id": f"dash-{len(os.listdir(os.path.join(ROOT,'builds'))) if os.path.isdir(os.path.join(ROOT,'builds')) else 0}",
                "sites": sites}
    json.dump(manifest, open(os.path.join(ROOT, "state/batch-manifest.json"), "w"), indent=2)
    return manifest

# ------------------------------------------------------------------ content (Claude)
def _content_prompt(site):
    gl = "\n".join(f"  {g['slug']} -> \"{g['name']}\"" for g in site["games_resolved"])
    return f"""You are a copywriter for a free-to-play SOCIAL gaming website. Return ONE JSON object (no prose, no code fences) with ALL keys below.

SITE: "{site['brand']}" — theme "{site['theme']}", brand voice {site['voice']}, brand story angle {site['story']}. Audience: adults 21+.
The 6 games (use EXACT slug keys and the exact names in prose):
{gl}
These are casual free reel/spinner arcade games, played for fun only.

HARD RULES (any violation = failure):
1. BANNED WORDS anywhere, any form (case-insensitive incl plurals/-ing): casino, gambling, gamble, betting, bet, wager, wagered, real money, deposit, withdrawal, odds, slots, slot, payout, bonus, bonuses, rewards, reward, jackpot, jackpots, win, wins, winner, winning, winnings, prize, cash, money. You MAY use "spin"/"spins". Say "reel games","spinners","feature rounds","free rounds","collecting symbols". Frame as free entertainment, nothing of monetary value at stake or to gain.
2. Never write "18+". Audience is 21+.
3. Fresh copy in the {site['voice']} voice, unique to this brand (checked for cross-site duplication — phrase in this brand's own words, avoid stock boilerplate sentences).
4. Word minimums: each game description >=160 words; about_story >=430; privacy >=330; terms >=330; index copy combined >=320; games_intro >=90; each privacy_section/terms_section body 45-80 words; each faq answer 40-70 words.

Return EXACTLY these keys:
{{
 "tagline","hero_headline","hero_intro","home_lead",
 "home_sections":[{{"heading","body"}} x3],
 "games_intro","games_intro_meta",
 "games":{{ "<slug>":{{"tagline","description","how_to_play"}} for all 6 }},
 "about_story","about_meta",
 "team":[{{"role","bio"}} x3 in order],
 "contact":{{"meta","intro","email","hours","community"}},
 "privacy","terms",
 "testimonials":[{{"text"}} x3 in order, first person, never name the brand],
 "topbar_parts":["x3 short"], "disclaimer":"80-110 words, no banned words",
 "stats":[{{"n","l"}} x4],
 "features":[{{"icon","title","desc"}} x4], "values":[{{"icon","title","desc"}} x3],
 "howto":[{{"title","desc"}} x3], "categories":[{{"title","desc"}} x3],
 "faq":[{{"q","a"}} x7], "responsible":[{{"title","body"}} x5],
 "game_features":["x4"],
 "game_meta":{{ "<slug>":{{"category","tags":["x3"],"tips":["x3"]}} for all 6 }},
 "privacy_sections":[{{"h","b"}} x11], "terms_sections":[{{"h","b"}} x11],
 "micro":{{"cta_h","cta_p","rp_hero","rp_callout","playwell","contact_before","contact_aside","faq_still","legal_callout"}}
}}
The "micro" object is short site-specific UI copy in this brand's own voice — each value a unique sentence (used across the site, so must NOT match other brands' phrasing): cta_h (3-5 word heading), cta_p (~25 words, invite to play free/no-cost/no-download), rp_hero (~20 words responsible-play intro), rp_callout (~35 words, free/21+/nothing of monetary value), playwell (~25 words shown beside each game), contact_before (3-4 word heading), contact_aside (~15 words pointing to the FAQ page, may include the text "FAQ page"), faq_still (~20 words pointing to the Contact page), legal_callout (~25 words, free social gaming 21+, nothing of monetary value on the site).
icon values must be from: bolt, star, shield, device, game, music, sun, globe, heart, users, sofa.
Use email like hello@{site['slug']}.example. Testimonial dates are handled separately."""

def _extract_json(text):
    t = text.strip()
    if t.startswith("```"):
        t = re.sub(r"^```[a-zA-Z]*\n?", "", t); t = re.sub(r"\n?```$", "", t)
    a, b = t.find("{"), t.rfind("}")
    return json.loads(t[a:b+1])

def gen_content(site, api_key, model=DEFAULT_MODEL):
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    last = None
    for attempt in range(2):
        msg = client.messages.create(
            model=model, max_tokens=8000,
            system="Return only a single valid JSON object. No markdown, no commentary.",
            messages=[{"role":"user","content":_content_prompt(site) + ("" if attempt==0 else "\n\nYour previous reply was not valid/complete JSON. Return the COMPLETE JSON object again.")}],
        )
        raw = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        try:
            data = _extract_json(raw)
            _require(data, site); return data
        except Exception as ex:
            last = ex
    raise RuntimeError(f"content generation failed for {site['slug']}: {last}")

def _require(d, site):
    need = ["tagline","hero_headline","hero_intro","home_lead","home_sections","games_intro","games_intro_meta",
            "games","about_story","about_meta","team","contact","privacy","terms","testimonials","topbar_parts",
            "disclaimer","stats","features","values","howto","categories","faq","responsible","game_features",
            "game_meta","privacy_sections","terms_sections","micro"]
    miss = [k for k in need if k not in d]
    if miss: raise ValueError(f"missing keys: {miss}")
    for g in site["games_resolved"]:
        if g["slug"] not in d["games"] or g["slug"] not in d["game_meta"]:
            raise ValueError(f"missing game {g['slug']}")

# ------------------------------------------------------------------ write content files build_rich expects
def write_content_files(site, data):
    dates = ["Jan 2026","Feb 2026","Feb 2026"]
    base = {
        "tagline":data["tagline"],"hero_headline":data["hero_headline"],"hero_intro":data["hero_intro"],
        "home_lead":data["home_lead"],"home_sections":data["home_sections"],
        "games_intro":data["games_intro"],"games_intro_meta":data["games_intro_meta"],
        "games":data["games"],
        "about":{"meta":data["about_meta"],"story":data["about_story"],
                 "team":[{"name":site["team"][k],"role":data["team"][k]["role"],"bio":data["team"][k]["bio"]} for k in range(3)]},
        "contact":data["contact"],"privacy":data["privacy"],"terms":data["terms"],
        "testimonials":[{"name":site["testimonials"][k],"date":dates[k],"text":data["testimonials"][k]["text"]} for k in range(3)],
    }
    rich = {k:data[k] for k in ["topbar_parts","disclaimer","stats","features","values","howto","categories",
                                "faq","responsible","game_features","game_meta","micro"]}
    rich["privacy_sections"]=data["privacy_sections"]; rich["terms_sections"]=data["terms_sections"]
    os.makedirs(os.path.join(ROOT,"state/content"), exist_ok=True)
    os.makedirs(os.path.join(ROOT,"state/content-rich"), exist_ok=True)
    json.dump(base, open(os.path.join(ROOT,"state/content",site["slug"]+".json"),"w"), indent=2)
    json.dump(rich, open(os.path.join(ROOT,"state/content-rich",site["slug"]+".json"),"w"), indent=2)

# ------------------------------------------------------------------ build + qa + zip
def build_site(slug):
    import build_rich
    importlib.reload(build_rich)
    build_rich.build(slug)

def run_qa():
    import qa; importlib.reload(qa)
    buf = io.StringIO(); old = sys.stdout; sys.stdout = buf
    try: code = qa.qa()
    finally: sys.stdout = old
    return code, buf.getvalue()

def zip_batch(slugs, out_path):
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        for slug in slugs:
            base = os.path.join(ROOT, "builds", slug)
            for root, _, files in os.walk(base):
                for f in files:
                    fp = os.path.join(root, f)
                    z.write(fp, os.path.join(slug, os.path.relpath(fp, base)))
    return out_path

def commit_registry(manifest):
    reg = json.load(open(os.path.join(ROOT,"state/registry.json")))
    for s in manifest["sites"]:
        reg["themes"].append(s["theme"]); reg["primary_hexes"].append(s["palette"]["primary"])
        reg["voices_used_by_batch"].append(s["voice"]); reg["story_angles_used_by_batch"].append(s["story"])
        reg["testimonial_combos"].extend(s["testimonials"])
    reg["batches"].append({"batch_id":manifest["batch_id"],"sites":[s["slug"] for s in manifest["sites"]]})
    json.dump(reg, open(os.path.join(ROOT,"state/registry.json"),"w"), indent=2)
