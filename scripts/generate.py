#!/usr/bin/env python3
"""Deterministic static-site generator for the bulk social-gaming platform.
Reads state/batch-manifest.json + state/content/<slug>.json + assets/games-data/game-data.csv
and emits builds/<slug>/ with full structure, SEO, 21+ age gate, and per-game iframe pages.
All structural QA rules are enforced here so agent-authored copy only supplies prose.
"""
import csv, json, os, html, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDS = os.path.join(ROOT, "builds")
GAMES = {r["slug"]: r for r in csv.DictReader(open(os.path.join(ROOT, "assets/games-data/game-data.csv")))}

def e(s): return html.escape(str(s), quote=True)

def base_url(slug): return f"https://{slug}.pages.dev"

FONT_MAP = {
    "Poppins + Lora": ("Poppins:wght@400;600;700", "Lora:wght@400;500", "'Poppins',sans-serif", "'Lora',serif"),
    "Montserrat + Merriweather": ("Montserrat:wght@500;700;800", "Merriweather:wght@400;700", "'Montserrat',sans-serif", "'Merriweather',serif"),
    "Nunito + Bitter": ("Nunito:wght@400;600;800", "Bitter:wght@400;600", "'Nunito',sans-serif", "'Bitter',serif"),
}

def google_fonts_link(typ):
    h1font, bodyfont, _, _ = FONT_MAP[typ]
    return (f'<link rel="preconnect" href="https://fonts.googleapis.com">'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            f'<link href="https://fonts.googleapis.com/css2?family={h1font}&family={bodyfont}&display=swap" rel="stylesheet">')

def css(site):
    p = site["palette"]
    _, _, headfam, bodyfam = FONT_MAP[site["typography"]]
    layout = site["layout"]
    return f""":root{{--primary:{p['primary']};--secondary:{p['secondary']};--accent:{p['accent']};--bg:{p['background']};--ink:#1a1a22;--muted:#5a5a6a}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:{bodyfam};color:var(--ink);background:var(--bg);line-height:1.65;font-size:17px}}
h1,h2,h3,.brand{{font-family:{headfam};line-height:1.2;color:var(--primary)}}
h1{{font-size:2.4rem;margin-bottom:.5em}}h2{{font-size:1.7rem;margin:1.2em 0 .5em}}h3{{font-size:1.2rem}}
a{{color:var(--primary);text-decoration:none}}a:hover{{text-decoration:underline}}
p{{margin:0 0 1em}}
.container{{max-width:1080px;margin:0 auto;padding:0 20px}}
header.nav{{position:sticky;top:0;z-index:50;background:var(--bg);border-bottom:2px solid var(--secondary);padding:14px 0}}
.nav .container{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}}
.brand{{font-size:1.4rem;font-weight:800;color:var(--primary)}}
nav ul{{list-style:none;display:flex;gap:20px;flex-wrap:wrap}}
nav a{{font-weight:600}}
.btn{{display:inline-block;background:var(--primary);color:#fff;padding:12px 22px;border-radius:8px;font-weight:700;border:none;cursor:pointer}}
.btn.secondary{{background:var(--secondary)}}
.btn:hover{{text-decoration:none;opacity:.92}}
.hero{{padding:64px 0;background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff}}
.hero h1{{color:#fff;font-size:2.8rem}}.hero p{{font-size:1.15rem;max-width:640px}}
.hero .accentchip{{display:inline-block;background:var(--accent);color:var(--ink);padding:4px 12px;border-radius:20px;font-size:.85rem;font-weight:700;margin-bottom:14px}}
section{{padding:40px 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:22px}}
.card{{background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 4px 18px rgba(0,0,0,.08);transition:transform .15s}}
.card:hover{{transform:translateY(-4px)}}
.card img{{width:100%;height:170px;object-fit:cover;display:block;background:#eee}}
.card .body{{padding:16px}}.card h3{{margin-bottom:6px}}
.gameframe{{width:100%;aspect-ratio:16/10;border:0;border-radius:12px;background:#000;min-height:420px}}
.split{{display:grid;grid-template-columns:1.1fr .9fr;gap:36px;align-items:center}}
.tgrow{{background:#fff;border-radius:14px;padding:22px;box-shadow:0 4px 18px rgba(0,0,0,.06)}}
.testi{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px}}
.testi blockquote{{background:#fff;border-left:4px solid var(--accent);border-radius:10px;padding:18px;box-shadow:0 3px 12px rgba(0,0,0,.06)}}
.testi cite{{display:block;margin-top:10px;font-weight:700;color:var(--secondary);font-style:normal}}
.teamgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px}}
.teamgrid .m{{background:#fff;border-radius:12px;padding:18px;box-shadow:0 3px 12px rgba(0,0,0,.06)}}
.teamgrid .role{{color:var(--secondary);font-weight:700;font-size:.9rem}}
.legal{{max-width:760px}}.legal h2{{margin-top:1.4em}}
footer.site{{background:var(--ink);color:#d8d8e0;padding:40px 0;margin-top:40px}}
footer.site a{{color:var(--accent)}}
footer .cols{{display:flex;justify-content:space-between;flex-wrap:wrap;gap:24px}}
footer .agegate-note{{margin-top:18px;font-weight:700;color:#fff;border-top:1px solid #333;padding-top:14px}}
.agewrap{{position:fixed;inset:0;background:rgba(10,10,18,.92);z-index:999;display:flex;align-items:center;justify-content:center;padding:20px}}
.agebox{{background:#fff;max-width:440px;text-align:center;border-radius:16px;padding:34px}}
.agebox h2{{color:var(--primary);margin-top:0}}
.agebox .row{{display:flex;gap:12px;justify-content:center;margin-top:18px;flex-wrap:wrap}}
.hidden{{display:none!important}}
@media(max-width:760px){{.split{{grid-template-columns:1fr}}.hero h1{{font-size:2rem}}h1{{font-size:1.9rem}}}}
"""

# ---- shared fragments -------------------------------------------------------
def head(site, page_title, desc, canonical_path, extra_jsonld=None):
    slug = site["slug"]; b = base_url(slug)
    canon = b + canonical_path
    jsonld = extra_jsonld or ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(page_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(site['brand'])}">
<meta property="og:title" content="{e(page_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{b}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
{google_fonts_link(site['typography'])}
<link rel="stylesheet" href="/style.css">
{jsonld}
</head>
<body class="layout-{site['layout']}">
"""

def agegate(site):
    return f"""<div class="agewrap" id="ageGate" role="dialog" aria-modal="true" aria-labelledby="ageTitle">
  <div class="agebox">
    <h2 id="ageTitle">Are you 21 or older?</h2>
    <p>{e(site['brand'])} offers free-to-play social games for adults. You must be 21+ to enter. No purchases, and nothing of monetary value can be won.</p>
    <div class="row">
      <button class="btn" id="ageYes">I am 21 or older</button>
      <button class="btn secondary" id="ageNo">Exit</button>
    </div>
  </div>
</div>
<script>
(function(){{
  var g=document.getElementById('ageGate');
  if(localStorage.getItem('age21ok')==='1'){{g.classList.add('hidden');}}
  document.getElementById('ageYes').onclick=function(){{localStorage.setItem('age21ok','1');g.classList.add('hidden');}};
  document.getElementById('ageNo').onclick=function(){{window.location.href='https://www.google.com';}};
}})();
</script>
"""

def nav(site):
    return f"""<header class="nav"><div class="container">
  <a class="brand" href="/index.html">{e(site['brand'])}</a>
  <nav><ul>
    <li><a href="/index.html">Home</a></li>
    <li><a href="/games.html">Games</a></li>
    <li><a href="/about.html">About</a></li>
    <li><a href="/contact.html">Contact</a></li>
  </ul></nav>
</div></header>
"""

# per-site chrome microcopy so brands read as genuinely independent (no shared footer boilerplate)
CHROME = {
    "lumen-play": {"tag":"A cosy corner of free-to-play games, made by friends for friends.",
                   "note":"Strictly 21+. Lumen Play is a free social gaming lounge — every game is just for fun, with no purchases and never anything of monetary value at stake."},
    "cinderpeak-arcade": {"tag":"Neon-lit free-to-play reels from an indie arcade studio that never grew up.",
                          "note":"You must be 21 or older to play here. Cinderpeak Arcade is a free social arcade — play purely for the thrill, with no purchases and nothing of monetary value ever on the line."},
    "driftwave-games": {"tag":"Breezy free-to-play games from a crew scattered across the world's coastlines.",
                        "note":"Adults 21 and up only. Driftwave Games is a free social gaming shore — everything here is relaxed entertainment, with no purchases and nothing of monetary value to chase."},
}

def footer(site):
    c = CHROME.get(site["slug"], {"tag":"Free-to-play social gaming for the community.",
                                  "note":f"21+ only. {site['brand']} is a free social gaming site for entertainment; no purchases and nothing of monetary value is involved."})
    return f"""<footer class="site"><div class="container">
  <div class="cols">
    <div><strong>{e(site['brand'])}.</strong><br>{e(c['tag'])}</div>
    <div><a href="/about.html">About</a> · <a href="/contact.html">Contact</a> · <a href="/games.html">Games</a></div>
    <div><a href="/privacy.html">Privacy Policy</a> · <a href="/terms.html">Terms of Use</a></div>
  </div>
  <div class="agegate-note">{e(c['note'])}</div>
</div></footer>
</body></html>
"""

def page(site, title, desc, canon, body, jsonld=None):
    return head(site, title, desc, canon, jsonld) + agegate(site) + nav(site) + "<main>" + body + "</main>" + footer(site)

def paras(text):
    return "\n".join(f"<p>{e(p.strip())}</p>" for p in text.split("\n") if p.strip())

def org_jsonld(site):
    b = base_url(site["slug"])
    data = {"@context":"https://schema.org","@type":"Organization","name":site["brand"],
            "url":b,"description":site.get("_desc",f"{site['brand']} free-to-play social gaming"),
            "foundingDate":"2026"}
    return f'<script type="application/ld+json">{json.dumps(data)}</script>'

def game_jsonld(site, g, gm):
    b = base_url(site["slug"])
    data = {"@context":"https://schema.org","@type":"VideoGame","name":gm["game_name"],
            "url":f"{b}/game-{gm['slug']}.html","genre":"Social casual game",
            "gamePlatform":"Web browser","applicationCategory":"Game",
            "operatingSystem":"Web","offers":{"@type":"Offer","price":"0","priceCurrency":"USD"},
            "publisher":{"@type":"Organization","name":site["brand"]}}
    return f'<script type="application/ld+json">{json.dumps(data)}</script>'

# ---- page builders ----------------------------------------------------------
def build_site(site, content):
    slug = site["slug"]; b = base_url(slug)
    site["_desc"] = content["tagline"]
    out = os.path.join(BUILDS, slug)
    os.makedirs(out, exist_ok=True)
    # style
    open(os.path.join(out, "style.css"), "w").write(css(site))

    games = [dict(GAMES[g["slug"]]) for g in site["games_resolved"]]

    # -------- index --------
    home_sections = "".join(
        f'<section class="container"><h2>{e(s["heading"])}</h2>{paras(s["body"])}</section>'
        for s in content["home_sections"])
    featured = "".join(
        f'<a class="card" href="/game-{gm["slug"]}.html"><img src="/assets/games-images/{e(gm["image"])}" '
        f'alt="{e(gm["game_name"])} cover" loading="lazy"><div class="body"><h3>{e(gm["game_name"])}</h3>'
        f'<p>{e(content["games"][gm["slug"]]["tagline"])}</p></div></a>'
        for gm in games)
    testis = "".join(
        f'<blockquote>{paras(t["text"])}<cite>— {e(t["name"])}, {e(t["date"])}</cite></blockquote>'
        for t in content["testimonials"])
    idx_body = f"""
<div class="hero"><div class="container">
  <span class="accentchip">Free-to-play · 21+ · Social gaming</span>
  <h1>{e(content['hero_headline'])}</h1>
  <p>{e(content['hero_intro'])}</p>
  <p><a class="btn" href="/games.html">Browse the games</a></p>
</div></div>
<section class="container">{paras(content['home_lead'])}</section>
{home_sections}
<section class="container"><h2>Featured games</h2><div class="grid">{featured}</div></section>
<section class="container"><h2>What our community says</h2><div class="testi">{testis}</div></section>
"""
    open(os.path.join(out, "index.html"), "w").write(
        page(site, f"{site['brand']} — Free Social Gaming", content["tagline"], "/index.html",
             idx_body, org_jsonld(site)))

    # -------- games.html --------
    def excerpt(txt, n=42):
        w = txt.split()
        return " ".join(w[:n]) + ("…" if len(w) > n else "")
    allcards = "".join(
        f'<a class="card" href="/game-{gm["slug"]}.html"><img src="/assets/games-images/{e(gm["image"])}" '
        f'alt="{e(gm["game_name"])} cover" loading="lazy"><div class="body"><h3>{e(gm["game_name"])}</h3>'
        f'<p><strong>{e(content["games"][gm["slug"]]["tagline"])}</strong></p>'
        f'<p>{e(excerpt(content["games"][gm["slug"]]["description"]))}</p>'
        f'<p><span class="btn secondary">Play free →</span></p></div></a>'
        for gm in games)
    games_body = f"""
<section class="container"><h1>Our Games</h1>{paras(content['games_intro'])}
<div class="grid">{allcards}</div></section>
"""
    open(os.path.join(out, "games.html"), "w").write(
        page(site, f"Games — {site['brand']}", content["games_intro_meta"], "/games.html", games_body))

    # -------- per-game pages (exactly ONE iframe each) --------
    for gm in games:
        gc = content["games"][gm["slug"]]
        others = "".join(
            f'<a class="card" href="/game-{o["slug"]}.html"><img src="/assets/games-images/{e(o["image"])}" '
            f'alt="{e(o["game_name"])} cover" loading="lazy"><div class="body"><h3>{e(o["game_name"])}</h3></div></a>'
            for o in games if o["slug"] != gm["slug"])[:9999]
        gbody = f"""
<section class="container">
  <h1>{e(gm['game_name'])}</h1>
  <p><em>{e(gc['tagline'])}</em></p>
  <iframe class="gameframe" src="{e(gm['iframe_url'])}" title="Play {e(gm['game_name'])}" allowfullscreen loading="lazy"></iframe>
  {paras(gc['description'])}
  <h2>How it plays</h2>{paras(gc['how_to_play'])}
</section>
<section class="container"><h2>More games to try</h2><div class="grid">{others}</div></section>
"""
        open(os.path.join(out, f"game-{gm['slug']}.html"), "w").write(
            page(site, f"{gm['game_name']} — Play Free at {site['brand']}", gc["tagline"],
                 f"/game-{gm['slug']}.html", gbody, game_jsonld(site, gm, gm)))

    # -------- about.html --------
    team = "".join(
        f'<div class="m"><h3>{e(m["name"])}</h3><div class="role">{e(m["role"])}</div>{paras(m["bio"])}</div>'
        for m in content["about"]["team"])
    about_body = f"""
<section class="container">
  <h1>About {e(site['brand'])}</h1>
  {paras(content['about']['story'])}
  <h2>Meet the team</h2><div class="teamgrid">{team}</div>
</section>
"""
    open(os.path.join(out, "about.html"), "w").write(
        page(site, f"About — {site['brand']}", content["about"]["meta"], "/about.html", about_body,
             org_jsonld(site)))

    # -------- contact.html --------
    c = content["contact"]
    contact_body = f"""
<section class="container">
  <h1>Contact {e(site['brand'])}</h1>
  {paras(c['intro'])}
  <div class="tgrow">
  <p><strong>Email:</strong> <a href="mailto:{e(c['email'])}">{e(c['email'])}</a></p>
  <p><strong>Support hours:</strong> {e(c['hours'])}</p>
  <p><strong>Community:</strong> {e(c['community'])}</p>
  </div>
</section>
"""
    open(os.path.join(out, "contact.html"), "w").write(
        page(site, f"Contact — {site['brand']}", c["meta"], "/contact.html", contact_body))

    # -------- privacy.html / terms.html --------
    open(os.path.join(out, "privacy.html"), "w").write(
        page(site, f"Privacy Policy — {site['brand']}", "Privacy policy for " + site["brand"],
             "/privacy.html", f'<section class="container legal"><h1>Privacy Policy</h1>{paras(content["privacy"])}</section>'))
    open(os.path.join(out, "terms.html"), "w").write(
        page(site, f"Terms of Use — {site['brand']}", "Terms of use for " + site["brand"],
             "/terms.html", f'<section class="container legal"><h1>Terms of Use</h1>{paras(content["terms"])}</section>'))

    # -------- sitemap.xml / robots.txt --------
    urls = ["/index.html","/games.html","/about.html","/contact.html","/privacy.html","/terms.html"] + \
           [f"/game-{gm['slug']}.html" for gm in games]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + \
         "".join(f"  <url><loc>{b}{u}</loc><changefreq>weekly</changefreq></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(out, "sitemap.xml"), "w").write(sm)
    open(os.path.join(out, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {b}/sitemap.xml\n")

    # -------- copy shared image assets into build --------
    import shutil
    imgdir = os.path.join(out, "assets", "games-images")
    os.makedirs(imgdir, exist_ok=True)
    for gm in games:
        src = os.path.join(ROOT, "assets/games-images", gm["image"])
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(imgdir, gm["image"]))
    return out

if __name__ == "__main__":
    manifest = json.load(open(os.path.join(ROOT, "state/batch-manifest.json")))
    targets = sys.argv[1:] or [s["slug"] for s in manifest["sites"]]
    for site in manifest["sites"]:
        if site["slug"] not in targets: continue
        cpath = os.path.join(ROOT, "state/content", site["slug"] + ".json")
        if not os.path.exists(cpath):
            print(f"SKIP {site['slug']}: no content json at {cpath}"); continue
        content = json.load(open(cpath))
        out = build_site(site, content)
        print(f"built {site['slug']} -> {out}")
