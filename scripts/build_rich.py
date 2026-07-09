#!/usr/bin/env python3
"""Parameterized rich builder for any site in the batch.
Reads:  state/content/<slug>.json         (base copy: games, about, testimonials, home, legal intros)
        state/content-rich/<slug>.json     (rich extras: features, faq, legal sections, tips, disclaimer, topbar)
        state/batch-manifest.json          (palette, typography, layout, brand)
Emits a full multi-page site into builds/<slug>/ with a layout that varies per site.
All structural QA rules preserved (21+/no-18+, one iframe per game page, SEO, sitemap/robots)."""
import csv, json, os, html, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAMES = {r["slug"]: r for r in csv.DictReader(open(os.path.join(ROOT, "assets/games-data/game-data.csv")))}
def load_manifest():
    return {s["slug"]: s for s in json.load(open(os.path.join(ROOT, "state/batch-manifest.json")))["sites"]}

def e(s): return html.escape(str(s), quote=True)
def paras(t): return "\n".join(f"<p>{e(p.strip())}</p>" for p in str(t).split("\n") if p.strip())
def initials(name): return "".join(w[0] for w in name.replace(".", "").split()[:2]).upper()

FONTS = {
    "Montserrat + Merriweather": ("Montserrat:wght@400;500;600;700;800", "Merriweather:wght@400;700",
                                   "'Montserrat',system-ui,sans-serif", "'Merriweather',Georgia,serif"),
    "Nunito + Bitter": ("Nunito:wght@400;600;700;800", "Bitter:wght@400;500;600",
                        "'Nunito',system-ui,sans-serif", "'Bitter',Georgia,serif"),
    "Poppins + Lora": ("Poppins:wght@400;500;600;700", "Lora:wght@400;500;600",
                       "'Poppins',system-ui,sans-serif", "'Lora',Georgia,serif"),
    "Work Sans + Source Serif 4": ("Work+Sans:wght@400;500;600;700", "Source+Serif+4:wght@400;600",
                       "'Work Sans',system-ui,sans-serif", "'Source Serif 4',Georgia,serif"),
    "Rubik + Zilla Slab": ("Rubik:wght@400;500;600;700", "Zilla+Slab:wght@400;500;600",
                       "'Rubik',system-ui,sans-serif", "'Zilla Slab',Georgia,serif"),
    "Space Grotesk + Inter": ("Space+Grotesk:wght@400;500;600;700", "Inter:wght@400;500",
                       "'Space Grotesk',system-ui,sans-serif", "'Inter',system-ui,sans-serif"),
    "Oswald + Lora": ("Oswald:wght@400;500;600;700", "Lora:wght@400;500",
                       "'Oswald',system-ui,sans-serif", "'Lora',Georgia,serif"),
    "Fraunces + Inter": ("Fraunces:opsz,wght@9..144,500;9..144,700", "Inter:wght@400;500",
                       "'Fraunces',Georgia,serif", "'Inter',system-ui,sans-serif"),
}

ICONS = {
 "bolt":'<path d="M13 2L3 14h7l-1 8 10-12h-7z"/>',
 "star":'<path d="M12 3l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 18.8 6.1 21l1.2-6.5L2.5 9.9 9.1 9z"/>',
 "shield":'<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
 "device":'<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M2 20h20"/>',
 "game":'<rect x="2" y="7" width="20" height="10" rx="5"/><path d="M7 11v2M6 12h2M15.5 11.5h.01M18 13.5h.01"/>',
 "music":'<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
 "sun":'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5L19 19M19 5l-1.5 1.5M6.5 17.5L5 19"/>',
 "globe":'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
 "heart":'<path d="M12 21s-7-4.5-9.5-9A5 5 0 0112 5a5 5 0 019.5 7c-2.5 4.5-9.5 9-9.5 9z"/>',
 "users":'<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0113 0"/><path d="M16 5.5a3.5 3.5 0 010 6M17 20a6.5 6.5 0 00-3-5.5"/>',
 "sofa":'<path d="M4 11V8a3 3 0 013-3h10a3 3 0 013 3v3M3 11a2 2 0 012 2v3h14v-3a2 2 0 012-2 2 2 0 012 2v5h-2v2h-2v-2H6v2H4v-2H2v-5a2 2 0 012-2z"/>',
}
def icon(n): return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS.get(n, ICONS["star"])}</svg>'

# ============================ CSS (themed + layout-specific) ============================
def css(S):
    p = S["palette"]; head, body = S["fam_head"], S["fam_body"]; layout = S["layout"]
    # layout-specific radius/hero personality
    radius = {"cards-grid-first":"12px", "single-scroll-anchor":"22px"}.get(layout, "16px")
    base = f""":root{{--primary:{p['primary']};--secondary:{p['secondary']};--accent:{p['accent']};--bg:{p['background']};
--ink:#1c1a24;--muted:#63607a;--line:#e9e6f2;--surface:#fff;--radius:{radius};--shadow:0 12px 34px rgba(20,16,40,.12);--shadow-sm:0 4px 16px rgba(20,16,40,.08)}}
*{{box-sizing:border-box;margin:0;padding:0}}html{{scroll-behavior:smooth}}
body{{font-family:{body};color:var(--ink);background:var(--bg);line-height:1.7;font-size:17px;-webkit-font-smoothing:antialiased}}
h1,h2,h3,h4,.brand,.btn,.eyebrow,nav a,.chip,.tag,.cat,.stats .n,.num{{font-family:{head}}}
h1{{font-size:clamp(2.1rem,4.6vw,3.4rem);line-height:1.08;letter-spacing:-.02em}}
h2{{font-size:clamp(1.6rem,3vw,2.25rem);line-height:1.15}}h3{{font-size:1.2rem}}
p{{margin:0 0 1em}}a{{color:var(--primary);text-decoration:none}}a:hover{{opacity:.85}}img{{max-width:100%;display:block}}
.container{{max-width:1140px;margin:0 auto;padding:0 22px}}
.eyebrow{{display:inline-block;text-transform:uppercase;letter-spacing:.16em;font-size:.72rem;font-weight:700;color:var(--secondary);margin-bottom:14px}}
.btn{{display:inline-flex;align-items:center;gap:8px;background:var(--primary);color:#fff;padding:13px 26px;border-radius:999px;font-weight:700;font-size:.95rem;border:none;cursor:pointer;transition:transform .15s,box-shadow .15s;box-shadow:var(--shadow-sm)}}
.btn:hover{{transform:translateY(-2px);color:#fff;box-shadow:var(--shadow)}}
.btn.ghost{{background:transparent;color:var(--primary);border:1.6px solid var(--line)}}
.btn.ghost:hover{{border-color:var(--primary);background:#fff}}
.btn.light{{background:#fff;color:var(--primary)}}
.topbanner{{background:var(--ink);color:#fff;font-size:.8rem;padding:9px 0;letter-spacing:.02em}}
.topbanner .container{{display:flex;justify-content:center;align-items:center;gap:16px;flex-wrap:wrap;text-align:center}}
.topbanner a{{color:var(--accent);font-weight:700}}.topbanner .sep{{opacity:.4}}
@media(max-width:640px){{.topbanner .hideSm{{display:none}}}}
.disclaimer{{background:#100d18;color:#8b849e;font-size:.8rem;line-height:1.65;padding:24px 0}}
.disclaimer .container{{max-width:1040px}}.disclaimer strong{{color:#b3aac9}}
.topbar{{position:sticky;top:0;z-index:60;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
.topbar .container{{display:flex;align-items:center;justify-content:space-between;height:70px}}
.brand{{font-size:1.35rem;font-weight:800;color:var(--primary);display:flex;align-items:center;gap:9px}}
.brand .dot{{width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,var(--primary),var(--secondary))}}
nav.main ul{{display:flex;gap:24px;list-style:none;align-items:center}}
nav.main a{{color:var(--ink);font-weight:600;font-size:.92rem}}nav.main a:hover,nav.main a[aria-current]{{color:var(--primary)}}
.navtoggle{{display:none;background:none;border:0;cursor:pointer;font-size:1.6rem;color:var(--ink)}}
section.block{{padding:76px 0}}section.alt{{background:linear-gradient(#fff,#fbfaff)}}
.sec-head{{max-width:640px;margin:0 auto 44px;text-align:center}}.sec-head p{{color:var(--muted)}}
.grid{{display:grid;gap:24px}}.g4{{grid-template-columns:repeat(4,1fr)}}.g3{{grid-template-columns:repeat(3,1fr)}}.g2{{grid-template-columns:repeat(2,1fr)}}
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow-sm);padding:30px}}
.stats .s{{text-align:center}}.stats .n{{font-size:2rem;font-weight:800;color:var(--primary)}}.stats .l{{color:var(--muted);font-size:.9rem}}
.feature{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:28px;box-shadow:var(--shadow-sm);transition:transform .15s,box-shadow .15s}}
.feature:hover{{transform:translateY(-4px);box-shadow:var(--shadow)}}
.feature .ic{{width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,var(--accent),#eef4ff);display:flex;align-items:center;justify-content:center;color:var(--primary);margin-bottom:16px}}
.feature .ic svg{{width:26px;height:26px}}.feature h3{{margin-bottom:8px}}.feature p{{color:var(--muted);margin:0;font-size:.96rem}}
.step{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:28px;box-shadow:var(--shadow-sm)}}
.step .num{{font-weight:800;color:#fff;background:var(--primary);width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:14px}}
.step h3{{margin-bottom:6px}}.step p{{color:var(--muted);margin:0;font-size:.96rem}}
.gcard{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow-sm);transition:transform .15s,box-shadow .15s;display:flex;flex-direction:column}}
.gcard:hover{{transform:translateY(-5px);box-shadow:var(--shadow)}}
.gcard .thumb{{position:relative}}.gcard img{{height:180px;width:100%;object-fit:cover}}
.gcard .cat{{position:absolute;top:12px;left:12px;background:rgba(20,16,36,.8);color:#fff;font-size:.7rem;font-weight:700;padding:5px 10px;border-radius:999px;letter-spacing:.04em}}
.gcard .body{{padding:18px 18px 20px;display:flex;flex-direction:column;gap:8px;flex:1}}
.gcard h3{{margin:0}}.gcard .tl{{color:var(--secondary);font-weight:700;font-size:.82rem}}.gcard p{{color:var(--muted);font-size:.92rem;margin:0}}
.gcard .foot{{margin-top:auto;padding-top:8px}}
.tags{{display:flex;gap:7px;flex-wrap:wrap}}.tag{{background:color-mix(in srgb,var(--primary) 10%,#fff);color:var(--primary);font-size:.72rem;font-weight:700;padding:4px 10px;border-radius:999px}}
.filters{{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:34px}}
.filters button{{font-weight:700;font-size:.85rem;border:1.6px solid var(--line);background:#fff;color:var(--muted);padding:9px 18px;border-radius:999px;cursor:pointer;transition:.15s}}
.filters button.active,.filters button:hover{{background:var(--primary);color:#fff;border-color:var(--primary)}}
.tcard{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:26px;box-shadow:var(--shadow-sm)}}
.tcard .stars{{color:#f4b740;letter-spacing:2px;margin-bottom:10px}}.tcard blockquote{{font-size:1.02rem;margin:0 0 16px}}
.tcard .who{{display:flex;align-items:center;gap:12px}}
.avatar{{width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800}}
.tcard .who .m{{font-weight:700;font-size:.92rem}}.tcard .who .d{{color:var(--muted);font-size:.82rem}}
.faq{{max-width:820px;margin:0 auto}}
.qa{{background:var(--surface);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;box-shadow:var(--shadow-sm);overflow:hidden}}
.qa button{{width:100%;text-align:left;background:none;border:0;padding:20px 22px;font-weight:700;font-size:1.02rem;color:var(--ink);cursor:pointer;display:flex;justify-content:space-between;gap:16px;align-items:center}}
.qa button .pm{{color:var(--primary);font-size:1.4rem;transition:transform .2s}}.qa.open button .pm{{transform:rotate(45deg)}}
.qa .ans{{max-height:0;overflow:hidden;transition:max-height .28s;padding:0 22px}}.qa.open .ans{{max-height:360px;padding-bottom:20px}}.qa .ans p{{color:var(--muted);margin:0}}
.ctaband{{background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;border-radius:24px;padding:52px;text-align:center;box-shadow:var(--shadow)}}
.ctaband h2{{color:#fff}}.ctaband p{{color:rgba(255,255,255,.9);max-width:52ch;margin:12px auto 26px}}
.newsletter{{display:flex;gap:10px;max-width:440px;margin:0 auto;flex-wrap:wrap;justify-content:center}}
.newsletter input{{flex:1;min-width:220px;border:0;border-radius:999px;padding:13px 20px;font-size:.95rem}}
.gameframe{{width:100%;aspect-ratio:16/10;min-height:440px;border:0;border-radius:18px;background:#0c0a14;box-shadow:var(--shadow)}}
.gwrap{{display:grid;grid-template-columns:1fr .42fr;gap:34px;align-items:start}}
.panel{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow-sm);margin-bottom:20px}}.panel h3{{margin-bottom:12px}}
.flist{{list-style:none;display:flex;flex-direction:column;gap:10px}}.flist li{{display:flex;gap:10px;align-items:flex-start;color:var(--muted);font-size:.95rem}}.flist li:before{{content:"✦";color:var(--secondary);margin-top:2px}}
.page-hero{{background:linear-gradient(150deg,var(--primary),var(--secondary));color:#fff;padding:64px 0}}.page-hero h1{{color:#fff}}.page-hero p{{color:rgba(255,255,255,.9);max-width:60ch;margin-top:10px}}
.prose{{max-width:820px;margin:0 auto}}.prose h2{{margin:1.6em 0 .5em;font-size:1.35rem;color:var(--primary)}}.prose p{{color:#3a3450}}
.toc{{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 22px;margin-bottom:34px;box-shadow:var(--shadow-sm)}}.toc h3{{font-size:.8rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-bottom:10px}}.toc ul{{list-style:none;columns:2;gap:14px}}.toc a{{font-size:.92rem}}
.callout{{background:color-mix(in srgb,var(--primary) 8%,#fff);border-left:4px solid var(--primary);border-radius:10px;padding:18px 20px;margin:24px 0;color:var(--ink)}}
footer.site{{background:#181425;color:#c6bfda;padding:60px 0 30px}}
footer.site .cols{{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:32px;margin-bottom:34px}}
footer.site h4{{color:#fff;font-size:.85rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:14px}}
footer.site a{{color:#c6bfda;display:block;padding:5px 0;font-size:.93rem}}footer.site a:hover{{color:#fff}}
footer .fbrand{{font-weight:800;color:#fff;font-size:1.2rem;margin-bottom:10px}}footer .fbrand small{{display:block;font-weight:400;color:#9c94b4;font-size:.9rem;margin-top:8px;line-height:1.5}}
footer .legalnote{{border-top:1px solid #352d4a;padding-top:22px;font-size:.82rem;color:#9c94b4;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}}
.age-badge{{display:inline-flex;align-items:center;gap:6px;background:#352d4a;color:#fff;font-weight:800;font-size:.75rem;padding:4px 10px;border-radius:8px}}
.agewrap{{position:fixed;inset:0;background:rgba(16,12,26,.93);backdrop-filter:blur(6px);z-index:999;display:flex;align-items:center;justify-content:center;padding:20px}}
.agebox{{background:#fff;max-width:460px;text-align:center;border-radius:22px;padding:40px 34px;box-shadow:0 30px 70px rgba(0,0,0,.4)}}
.agebox .dot{{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,var(--primary),var(--secondary));margin:0 auto 16px}}
.agebox h2{{color:var(--primary)}}.agebox p{{color:var(--muted);font-size:.96rem}}.agebox .row{{display:flex;gap:12px;justify-content:center;margin-top:22px;flex-wrap:wrap}}
#toTop{{position:fixed;right:22px;bottom:22px;width:46px;height:46px;border-radius:50%;background:var(--primary);color:#fff;border:0;cursor:pointer;font-size:1.2rem;opacity:0;pointer-events:none;transition:.25s;box-shadow:var(--shadow);z-index:70}}#toTop.show{{opacity:1;pointer-events:auto}}
/* play-in-iframe modal */
.playmodal{{position:fixed;inset:0;background:rgba(8,6,16,.9);backdrop-filter:blur(6px);z-index:200;display:none;align-items:center;justify-content:center;padding:16px}}
.playmodal.open{{display:flex}}
.pm-inner{{width:min(1040px,100%);background:#0b0912;border-radius:16px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.6);display:flex;flex-direction:column}}
.pm-bar{{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px;background:var(--ink);color:#fff}}
.pm-bar #pmTitle{{font-weight:800;font-size:.95rem}}
.pm-bar button{{background:rgba(255,255,255,.14);color:#fff;border:0;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;font-size:.82rem;margin-left:8px}}
.pm-bar button:hover{{background:rgba(255,255,255,.28)}}
.playmodal iframe{{width:100%;border:0;background:#000;height:min(70vh,620px)}}
.gcard[data-play]{{cursor:pointer}}
.playoverlay{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(16,12,32,.32);opacity:0;transition:.2s}}
.playoverlay span{{width:60px;height:60px;border-radius:50%;background:rgba(255,255,255,.94);color:var(--primary);display:flex;align-items:center;justify-content:center;font-size:1.4rem;padding-left:5px}}
.gcard:hover .playoverlay{{opacity:1}}
.gcard .foot{{display:flex;align-items:center;justify-content:space-between;gap:10px}}
.gcard .details{{font-weight:700;font-size:.8rem;white-space:nowrap}}
.hidden{{display:none!important}}
@media(max-width:920px){{.gwrap{{grid-template-columns:1fr}}footer.site .cols{{grid-template-columns:1fr 1fr}}}}
@media(max-width:760px){{nav.main{{position:fixed;inset:70px 0 auto 0;background:#fff;border-bottom:1px solid var(--line);transform:translateY(-140%);transition:.25s;box-shadow:var(--shadow)}}nav.main.open{{transform:translateY(0)}}nav.main ul{{flex-direction:column;padding:18px 22px;gap:6px}}nav.main a{{display:block;padding:10px 0}}.navtoggle{{display:block}}.g4,.g3,.g2,.stats{{grid-template-columns:1fr 1fr}}.toc ul{{columns:1}}}}
@media(max-width:520px){{.g4,.g3,.g2,.stats{{grid-template-columns:1fr}}.ctaband{{padding:34px 22px}}}}
"""
    # ---- layout-specific hero personalities ----
    if layout == "cards-grid-first":  # arcade: dark neon hero, bold
        base += """
.hero{background:radial-gradient(1000px 500px at 70% -20%,color-mix(in srgb,var(--secondary) 70%,#000),#100d18);color:#fff;padding:78px 0;position:relative;overflow:hidden;text-align:center}
.hero:before{content:"";position:absolute;inset:0;background-image:linear-gradient(color-mix(in srgb,var(--accent) 12%,transparent) 1px,transparent 1px),linear-gradient(90deg,color-mix(in srgb,var(--accent) 12%,transparent) 1px,transparent 1px);background-size:40px 40px;mask:radial-gradient(600px 300px at 50% 0,#000,transparent)}
.hero .container{position:relative}.hero h1{color:#fff;text-shadow:0 0 30px color-mix(in srgb,var(--secondary) 60%,transparent)}
.hero p.lead{color:rgba(255,255,255,.86);font-size:1.2rem;max-width:44ch;margin:18px auto 26px}
.hero .cta{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}.hero .chipset{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:24px}
.chip{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.28);color:#fff;padding:6px 14px;border-radius:999px;font-size:.8rem;font-weight:600}
.gcard{border:2px solid var(--line)}.gcard:hover{border-color:var(--secondary)}
.stats{background:#100d18;border-color:#2a2340;color:#fff;margin-top:-46px;position:relative;z-index:5}.stats .n{color:var(--accent)}.stats .l{color:#a99fc4}
"""
    elif layout == "single-scroll-anchor":  # tropical: airy full-bleed hero, wave divider, dot-nav
        base += """
.hero{background:linear-gradient(160deg,var(--primary),var(--secondary) 60%,var(--accent));color:#fff;padding:96px 0 120px;position:relative;overflow:hidden;text-align:center}
.hero:before{content:"";position:absolute;inset:0;background:radial-gradient(700px 340px at 15% 10%,rgba(255,255,255,.28),transparent),radial-gradient(600px 300px at 90% 90%,rgba(255,255,255,.18),transparent)}
.hero .container{position:relative}.hero h1{color:#fff}.hero p.lead{color:rgba(255,255,255,.95);font-size:1.25rem;max-width:46ch;margin:18px auto 28px}
.hero .cta{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}.hero .chipset{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:26px}
.chip{background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.32);color:#fff;padding:6px 14px;border-radius:999px;font-size:.8rem;font-weight:700}
.wave{position:absolute;bottom:-1px;left:0;width:100%;line-height:0}.wave svg{width:100%;height:70px;display:block}
.dotnav{position:fixed;right:20px;top:50%;transform:translateY(-50%);display:flex;flex-direction:column;gap:12px;z-index:55}
.dotnav a{width:11px;height:11px;border-radius:50%;background:color-mix(in srgb,var(--primary) 30%,#fff);border:1px solid var(--primary);display:block;transition:.2s}.dotnav a:hover{background:var(--primary);transform:scale(1.25)}
.stats{margin-top:36px}
@media(max-width:920px){.dotnav{display:none}}
"""
    elif layout == "centered-minimal":  # calm, editorial, lots of whitespace
        base += """
.hero{background:var(--bg);color:var(--ink);padding:100px 0 56px;text-align:center;border-bottom:1px solid var(--line)}
.hero .eyebrow{color:var(--secondary)}.hero h1{color:var(--ink);max-width:17ch;margin:0 auto}
.hero p.lead{color:var(--muted);font-size:1.25rem;max-width:46ch;margin:18px auto 28px}
.hero .cta{display:flex;gap:14px;justify-content:center;flex-wrap:wrap}
.hero .chipset{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:26px}
.chip{background:color-mix(in srgb,var(--primary) 8%,#fff);border:1px solid var(--line);color:var(--primary);padding:6px 14px;border-radius:999px;font-size:.8rem;font-weight:700}
.stats{margin-top:44px;box-shadow:none;background:transparent;border:0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);border-radius:0}
"""
    else:  # default split hero
        base += """
.hero{background:linear-gradient(150deg,var(--primary),var(--secondary));color:#fff;padding:84px 0}
.hero .container{display:grid;grid-template-columns:1.05fr .95fr;gap:44px;align-items:center}
.hero h1{color:#fff}.hero p.lead{font-size:1.2rem;max-width:34ch;color:#fff;opacity:.92;margin:18px 0 26px}
.hero .cta{display:flex;gap:14px;flex-wrap:wrap}.hero .chipset{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px}
.chip{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);color:#fff;padding:6px 14px;border-radius:999px;font-size:.8rem}
.heroart{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.25);border-radius:22px;padding:16px}.heroart .g{display:grid;grid-template-columns:1fr 1fr;gap:12px}.heroart img{border-radius:12px;height:120px;width:100%;object-fit:cover}
.stats{margin-top:-46px;position:relative;z-index:5}
@media(max-width:920px){.hero .container{grid-template-columns:1fr}}
"""
    return base

# ============================ shared markup ============================
def load(S):
    slug = S["slug"]
    S["base"] = json.load(open(os.path.join(ROOT, "state/content", slug + ".json")))
    S["rich"] = json.load(open(os.path.join(ROOT, "state/content-rich", slug + ".json")))
    m = load_manifest()[slug]
    S["brand"] = m["brand"]; S["palette"] = m["palette"]; S["layout"] = m["layout"]
    dom = m.get("domain")
    S["base_url"] = ("https://" + dom.replace("https://","").replace("http://","").rstrip("/")) if dom else f"https://{slug}.pages.dev"
    hf, bf, S["fam_head"], S["fam_body"] = FONTS[m["typography"]]
    S["gfonts"] = f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family={hf}&family={bf}&display=swap" rel="stylesheet">'
    S["games"] = list(S["base"]["games"].keys())
    S["micro"] = MICRO.get(slug) or S["rich"].get("micro") or DEFAULT_MICRO
    return S

# per-site voiced microcopy for lines the generator would otherwise repeat across sites
# (keeps the cross-site duplicate-sentence QA clean and every site genuinely distinct)
MICRO = {
 "cinderpeak-arcade": {
   "cta_h":"Insert coin and play",
   "cta_p":"Step into an adults-only arcade stacked with free reel games. Nothing to buy, nothing to download — just hit start and go.",
   "rp_hero":"Cinderpeak Arcade runs on high-energy, feel-good fun. Below is how we keep those good times healthy.",
   "rp_callout":"Cinderpeak Arcade is free social gaming for the 21-and-over crowd. It costs nothing and nothing of monetary value is ever on the line — but a few smart habits keep every session a blast.",
   "playwell":"Free social arcade fun for players 21+. Nothing of monetary value is on the line here — plug in and enjoy the ride.",
   "contact_before":"Before you shout",
   "contact_aside":'Plenty of quick answers are waiting on our <a href="/faq.html">FAQ page</a>.',
   "faq_still":'Not finding it? Hit the <a href="/contact.html">Contact page</a> and a real human from the crew will jump in.',
   "legal_callout":"Cinderpeak Arcade is a free social arcade for players 21+. Nothing is for sale and nothing of monetary value features anywhere on this site.",
 },
 "driftwave-games": {
   "cta_h":"Catch the next wave",
   "cta_p":"Drift into a sunny, adults-only bay of free reel games. No purchases, no downloads — simply press play and unwind.",
   "rp_hero":"Driftwave Games is made for breezy, laid-back fun. Here is the way we help keep it feeling that easy.",
   "rp_callout":"Driftwave Games is free social gaming for grown-ups aged 21 and up. There is never a cost and nothing of monetary value to chase — a little balance just keeps the tide gentle.",
   "playwell":"Easygoing social play for adults 21+. Nothing of monetary value is involved anywhere — kick back and enjoy the swell.",
   "contact_before":"Before you message",
   "contact_aside":'A good few quick answers are floating over on our <a href="/faq.html">FAQ page</a>.',
   "faq_still":'Still adrift? Drop by the <a href="/contact.html">Contact page</a> and our crew will help you find your feet.',
   "legal_callout":"Driftwave Games is a free social gaming shore for adults 21+. Nothing is for sale and nothing of monetary value appears anywhere on this site.",
 },
}
DEFAULT_MICRO = {
  "cta_h":"Ready to play?","cta_p":"Join a free, adults-only community of social games — no cost, no downloads, just play.",
  "rp_hero":"We are built for light, feel-good entertainment. Here is how we help keep it that way.",
  "rp_callout":"Free social gaming for adults 21+. It costs nothing and nothing of monetary value can be gained — good habits keep it fun.",
  "playwell":"Free social gaming for adults 21+. Nothing of monetary value is at stake — just relax and enjoy.",
  "contact_before":"Before you write","contact_aside":'Many quick answers live on our <a href="/faq.html">FAQ page</a>.',
  "faq_still":'Still stuck? Head to the <a href="/contact.html">Contact page</a> and our team will help.',
  "legal_callout":"A free social gaming site for adults 21+. There are no purchases and nothing of monetary value anywhere on this site.",
}

NAV = [("Home","/index.html"),("Games","/games.html"),("About","/about.html"),
       ("Responsible Play","/responsible-play.html"),("FAQ","/faq.html"),("Contact","/contact.html")]

def head(S, title, desc, canon, jsonld=""):
    b = S["base_url"]
    return f"""<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{b}{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{e(S['brand'])}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{b}{canon}"><meta property="og:image" content="{b}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
{S['gfonts']}<link rel="stylesheet" href="/style.css">{jsonld}
</head><body>"""

def topbanner(S):
    parts = S["rich"]["topbar_parts"]
    segs = f'<span><strong>{e(parts[0])}</strong></span>'
    for x in parts[1:]:
        segs += f'<span class="sep hideSm">·</span><span class="hideSm">{e(x)}</span>'
    segs += '<span class="sep hideSm">·</span><a class="hideSm" href="/games.html">Play free →</a>'
    return f'<div class="topbanner"><div class="container">{segs}</div></div>'

def header(S, active):
    def li(t,h):
        cur = ' aria-current="page"' if h==active else ''
        return f'<li><a href="{h}"{cur}>{e(t)}</a></li>'
    lis = "".join(li(t,h) for t,h in NAV)
    return f"""<header class="topbar"><div class="container">
<a class="brand" href="/index.html"><span class="dot"></span>{e(S['brand'])}</a>
<button class="navtoggle" aria-label="Menu" id="navToggle">&#9776;</button>
<nav class="main" id="mainNav"><ul>{lis}<li><a class="btn" href="/games.html">Play free</a></li></ul></nav>
</div></header>"""

def agegate(S):
    return f"""<div class="agewrap" id="ageGate" role="dialog" aria-modal="true" aria-labelledby="ageT">
<div class="agebox"><div class="dot"></div><h2 id="ageT">Are you 21 or older?</h2>
<p>{e(S['brand'])} is a free-to-play social gaming site for adults. You must be 21+ to enter. There are no purchases and nothing of monetary value is involved.</p>
<div class="row"><button class="btn" id="ageYes">I am 21 or older</button><button class="btn ghost" id="ageNo">Leave</button></div></div></div>"""

def footer(S):
    g = S["games"]
    flinks = "".join(f'<a href="/game-{s}.html">{e(GAMES[s]["game_name"])}</a>' for s in g[:4])
    return f"""<footer class="site"><div class="container"><div class="cols">
<div><div class="fbrand">{e(S['brand'])}<small>{e(S['base']['tagline'])}</small></div><span class="age-badge">21+ ONLY</span></div>
<div><h4>Explore</h4><a href="/games.html">All games</a><a href="/about.html">About us</a><a href="/faq.html">FAQ</a><a href="/contact.html">Contact</a></div>
<div><h4>Play well</h4><a href="/responsible-play.html">Responsible play</a><a href="/privacy.html">Privacy policy</a><a href="/terms.html">Terms of use</a></div>
<div><h4>Games</h4>{flinks}</div></div>
<div class="legalnote"><span>Strictly 21+. {e(S['brand'])} is a free social gaming site — entertainment only, nothing of monetary value.</span><span>&copy; 2026 {e(S['brand'])}.</span></div>
</div></footer>"""

def disclaimer(S):
    return f'<section class="disclaimer"><div class="container"><strong>Disclaimer:</strong> {e(S["rich"]["disclaimer"])}</div></section>'

SCRIPTS = """<button id="toTop" aria-label="Back to top">&#8593;</button><script>
(function(){var g=document.getElementById('ageGate');if(g){if(localStorage.getItem('age21ok')==='1')g.classList.add('hidden');
var y=document.getElementById('ageYes'),n=document.getElementById('ageNo');
if(y)y.onclick=function(){localStorage.setItem('age21ok','1');g.classList.add('hidden');};if(n)n.onclick=function(){location.href='https://www.google.com';};}
var t=document.getElementById('navToggle'),nav=document.getElementById('mainNav');if(t)t.onclick=function(){nav.classList.toggle('open');};
document.querySelectorAll('.qa button').forEach(function(b){b.onclick=function(){b.parentElement.classList.toggle('open');};});
document.querySelectorAll('.filters button').forEach(function(b){b.onclick=function(){document.querySelectorAll('.filters button').forEach(function(x){x.classList.remove('active');});b.classList.add('active');var f=b.getAttribute('data-f');document.querySelectorAll('.gcard').forEach(function(c){c.style.display=(f==='all'||c.getAttribute('data-cat')===f)?'':'none';});};});
var tt=document.getElementById('toTop');window.addEventListener('scroll',function(){if(window.scrollY>500)tt.classList.add('show');else tt.classList.remove('show');});tt.onclick=function(){window.scrollTo({top:0,behavior:'smooth'});};
})();</script></body></html>"""

MODAL_HTML = ('<div class="playmodal" id="playModal" role="dialog" aria-modal="true" aria-hidden="true">'
 '<div class="pm-inner"><div class="pm-bar"><span id="pmTitle">Now playing</span>'
 '<div><button id="pmFull" type="button">&#9974; Fullscreen</button>'
 '<button id="pmClose" type="button">&#10005; Close</button></div></div>'
 '<iframe id="pmFrame" title="Game player" allowfullscreen></iframe></div></div>')
MODAL_JS = ('<script>(function(){var pm=document.getElementById("playModal");if(!pm)return;'
 'var pf=document.getElementById("pmFrame"),pt=document.getElementById("pmTitle");'
 'function op(u,t){pf.src=u;pt.textContent=t||"Now playing";pm.classList.add("open");document.body.style.overflow="hidden";}'
 'function cl(){pm.classList.remove("open");pf.src="";document.body.style.overflow="";}'
 'document.querySelectorAll("[data-play]").forEach(function(el){function go(ev){if(ev.target.closest(".details"))return;'
 'ev.preventDefault();op(el.getAttribute("data-url"),el.getAttribute("data-title"));}'
 'el.addEventListener("click",go);el.addEventListener("keydown",function(e){if(e.key==="Enter"||e.key===" "){go(e);}});});'
 'document.getElementById("pmClose").onclick=cl;'
 'document.getElementById("pmFull").onclick=function(){if(pf.requestFullscreen)pf.requestFullscreen();};'
 'pm.addEventListener("click",function(e){if(e.target===pm)cl();});'
 'document.addEventListener("keydown",function(e){if(e.key==="Escape")cl();});})();</script>')

def shell(S, title, desc, canon, body, active, jsonld="", modal=False):
    m = (MODAL_HTML + MODAL_JS) if modal else ""
    return head(S,title,desc,canon,jsonld)+agegate(S)+topbanner(S)+header(S,active)+"<main>"+body+"</main>"+footer(S)+disclaimer(S)+m+SCRIPTS

def stars(): return '<span class="stars">★★★★★</span>'

def gcard(S, slug, tags=True, modal=True):
    g = GAMES[slug]; gc = S["base"]["games"][slug]; gm = S["rich"]["game_meta"][slug]
    tg = "".join(f'<span class="tag">{e(t)}</span>' for t in gm["tags"]) if tags else ""
    thumb = (f'<div class="thumb"><img src="/assets/games-images/{e(g["image"])}" alt="{e(g["game_name"])} cover" loading="lazy">'
             f'<span class="cat">{e(gm["category"])}</span>')
    body = (f'<div class="body"><h3>{e(g["game_name"])}</h3><div class="tl">{e(gc["tagline"])}</div>'
            f'<p>{e(" ".join(gc["description"].split()[:24]))}…</p>')
    if modal:
        # whole card launches the game in the on-site iframe modal; "Details" link goes to the full page
        return (f'<div class="gcard" data-play data-url="{e(g["iframe_url"])}" data-title="{e(g["game_name"])}" '
                f'role="button" tabindex="0" data-cat="{e(gm["category"])}" aria-label="Play {e(g["game_name"])}">'
                f'{thumb}<span class="playoverlay"><span>&#9654;</span></span></div>'
                f'{body}<div class="foot"><div class="tags">{tg}</div>'
                f'<a class="details" href="/game-{slug}.html">Details &rarr;</a></div></div></div>')
    return (f'<a class="gcard" href="/game-{slug}.html" data-cat="{e(gm["category"])}">'
            f'{thumb}</div>{body}<div class="foot"><div class="tags">{tg}</div></div></div></a>')

def org_ld(S):
    return f'<script type="application/ld+json">{json.dumps({"@context":"https://schema.org","@type":"Organization","name":S["brand"],"url":S["base_url"],"description":S["base"]["tagline"]})}</script>'

# ============================ section fragments ============================
def s_stats(S):
    return '<div class="container"><div class="stats">'+"".join(f'<div class="s"><div class="n">{e(x["n"])}</div><div class="l">{e(x["l"])}</div></div>' for x in S["rich"]["stats"])+'</div></div>'
def s_features(S, cls="g4"):
    fs = "".join(f'<div class="feature"><div class="ic">{icon(x["icon"])}</div><h3>{e(x["title"])}</h3><p>{e(x["desc"])}</p></div>' for x in S["rich"]["features"])
    return f'<div class="sec-head"><span class="eyebrow">Why {e(S["brand"])}</span><h2>Made for easy play</h2></div><div class="grid {cls}">{fs}</div>'
def s_howto(S):
    st = "".join(f'<div class="step"><div class="num">{i}</div><h3>{e(x["title"])}</h3><p>{e(x["desc"])}</p></div>' for i,x in enumerate(S["rich"]["howto"],1))
    return f'<div class="sec-head"><span class="eyebrow">How it works</span><h2>Up and playing in seconds</h2></div><div class="grid g3">{st}</div>'
def s_categories(S):
    cs = "".join(f'<div class="feature"><h3>{e(x["title"])}</h3><p>{e(x["desc"])}</p></div>' for x in S["rich"]["categories"])
    return f'<div class="sec-head"><span class="eyebrow">Find your mood</span><h2>Browse by category</h2></div><div class="grid g3">{cs}</div>'
def s_games(S, cls="g3"):
    return f'<div class="sec-head"><span class="eyebrow">The library</span><h2>Featured games</h2></div><div class="grid {cls}">'+"".join(gcard(S,s) for s in S["games"])+f'</div><div style="text-align:center;margin-top:36px"><a class="btn" href="/games.html">See all games</a></div>'
def s_testi(S):
    ts = "".join(f'<div class="tcard">{stars()}<blockquote>“{e(t["text"])}”</blockquote><div class="who"><div class="avatar">{e(initials(t["name"]))}</div><div><div class="m">{e(t["name"])}</div><div class="d">{e(t["date"])}</div></div></div></div>' for t in S["base"]["testimonials"])
    return f'<div class="sec-head"><span class="eyebrow">From the community</span><h2>What our members say</h2></div><div class="grid g3">{ts}</div>'
def s_faq(S, n=5):
    qs = "".join(f'<div class="qa"><button>{e(q["q"])}<span class="pm">+</span></button><div class="ans"><p>{e(q["a"])}</p></div></div>' for q in S["rich"]["faq"][:n])
    return f'<div class="sec-head"><span class="eyebrow">Good to know</span><h2>Frequently asked</h2></div><div class="faq">{qs}</div><div style="text-align:center;margin-top:26px"><a class="btn ghost" href="/faq.html">All questions</a></div>'
def s_cta(S):
    m = S["micro"]
    return f'<div class="ctaband"><h2>{e(m["cta_h"])}</h2><p>{e(m["cta_p"])}</p><a class="btn light" href="/games.html">Enter now</a><form class="newsletter" style="margin-top:24px" onsubmit="return false"><input type="email" placeholder="Your email for new-game updates" aria-label="Email"><button class="btn light" type="submit">Keep me posted</button></form></div>'

# ============================ homepage per layout ============================
def index_page(S):
    b = S["base"]; hero_chips = '<span class="chip">No downloads</span><span class="chip">No purchases</span><span class="chip">Instant play</span>'
    layout = S["layout"]
    if layout == "cards-grid-first":
        hero = f'''<section class="hero"><div class="container"><span class="eyebrow" style="color:var(--accent)">Free-to-play · 21+ · Social arcade</span>
<h1>{e(b['hero_headline'])}</h1><p class="lead">{e(b['hero_intro'])}</p>
<div class="cta"><a class="btn light" href="/games.html">Enter the arcade</a><a class="btn ghost" style="color:#fff;border-color:rgba(255,255,255,.5)" href="/about.html">Our story</a></div>
<div class="chipset">{hero_chips}</div></div></section>'''
        body = hero + s_stats(S)
        body += f'<section class="block"><div class="container">{s_games(S,"g3")}</div></section>'
        body += f'<section class="block alt"><div class="container">{s_features(S,"g4")}</div></section>'
        body += f'<section class="block"><div class="container">{s_howto(S)}</div></section>'
        body += f'<section class="block alt"><div class="container">{s_categories(S)}</div></section>'
        body += f'<section class="block"><div class="container">{s_testi(S)}</div></section>'
        body += f'<section class="block alt"><div class="container">{s_faq(S)}</div></section>'
        body += f'<section class="block"><div class="container">{s_cta(S)}</div></section>'
    elif layout == "single-scroll-anchor":
        wave = '<div class="wave"><svg viewBox="0 0 1200 70" preserveAspectRatio="none"><path d="M0 40 C200 70 400 10 600 35 C800 60 1000 15 1200 40 L1200 70 L0 70 Z" fill="var(--bg)"/></svg></div>'
        dots = '<nav class="dotnav">'+"".join(f'<a href="#{i}" aria-label="{i}"></a>' for i in ["top","play","features","games","community","faq"])+'</nav>'
        hero = f'''<section class="hero" id="top"><div class="container"><span class="eyebrow" style="color:#fff">Free-to-play · 21+ · Social gaming</span>
<h1>{e(b['hero_headline'])}</h1><p class="lead">{e(b['hero_intro'])}</p>
<div class="cta"><a class="btn light" href="/games.html">Dive in</a><a class="btn ghost" style="color:#fff;border-color:rgba(255,255,255,.55)" href="#games">Browse games</a></div>
<div class="chipset">{hero_chips}</div></div>{wave}</section>'''
        body = dots + hero
        body += f'<section class="block" id="play"><div class="container" style="max-width:820px;text-align:center">{paras(b["home_lead"])}</div></section>'
        body += s_stats(S)
        body += f'<section class="block" id="features"><div class="container">{s_features(S,"g2")}</div></section>'
        body += f'<section class="block alt"><div class="container">{s_howto(S)}</div></section>'
        body += f'<section class="block" id="games"><div class="container">{s_games(S,"g3")}</div></section>'
        body += f'<section class="block alt"><div class="container">{s_categories(S)}</div></section>'
        body += f'<section class="block" id="community"><div class="container">{s_testi(S)}</div></section>'
        body += f'<section class="block alt" id="faq">>><div class="container">{s_faq(S)}</div></section>'.replace(">>","")
        body += f'<section class="block"><div class="container">{s_cta(S)}</div></section>'
    elif layout == "centered-minimal":
        hero = f'''<section class="hero"><div class="container"><span class="eyebrow">Free-to-play · 21+ · Social gaming</span>
<h1>{e(b['hero_headline'])}</h1><p class="lead">{e(b['hero_intro'])}</p>
<div class="cta"><a class="btn" href="/games.html">Browse games</a><a class="btn ghost" href="/about.html">Our story</a></div>
<div class="chipset">{hero_chips}</div></div></section>'''
        body = hero + s_stats(S)
        for sec,alt in [(s_features(S,"g4"),1),(s_games(S,"g3"),0),(s_howto(S),1),(s_categories(S),0),(s_testi(S),1),(s_faq(S),0),(s_cta(S),1)]:
            body += f'<section class="block{" alt" if alt else ""}"><div class="container">{sec}</div></section>'
    else:  # split hero default
        hero_imgs = "".join(f'<img src="/assets/games-images/{e(GAMES[s]["image"])}" alt="{e(GAMES[s]["game_name"])} cover" loading="lazy">' for s in S["games"][:4])
        hero = f'''<section class="hero"><div class="container"><div><span class="eyebrow" style="color:#fff">Free-to-play · 21+ · Social gaming</span>
<h1>{e(b['hero_headline'])}</h1><p class="lead">{e(b['hero_intro'])}</p>
<div class="cta"><a class="btn light" href="/games.html">Browse games</a><a class="btn ghost" style="color:#fff;border-color:rgba(255,255,255,.5)" href="/about.html">Our story</a></div>
<div class="chipset">{hero_chips}</div></div><div class="heroart"><div class="g">{hero_imgs}</div></div></div></section>'''
        body = hero + s_stats(S)
        for sec,alt in [(s_features(S,"g4"),0),(s_howto(S),1),(s_categories(S),0),(s_games(S,"g3"),1),(s_testi(S),0),(s_faq(S),1),(s_cta(S),0)]:
            body += f'<section class="block{" alt" if alt else ""}"><div class="container">{sec}</div></section>'
    return shell(S, f"{S['brand']} — Free Social Gaming", b["tagline"], "/index.html", body, "/index.html", org_ld(S), modal=True)

# ============================ inner pages ============================
def build_inner(S):
    b = S["base"]; out = S["out"]
    # games listing
    cats = sorted({S["rich"]["game_meta"][s]["category"] for s in S["games"]})
    filt = '<button class="active" data-f="all">All</button>'+"".join(f'<button data-f="{e(c)}">{e(c)}</button>' for c in cats)
    allg = "".join(gcard(S,s) for s in S["games"])
    gbody = f'<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#fff">The library</span><h1>Our Games</h1><p>{e(b["games_intro"])}</p></div></section><section class="block"><div class="container"><div class="filters">{filt}</div><div class="grid g3">{allg}</div></div></section>'
    open(os.path.join(out,"games.html"),"w").write(shell(S,f"Games — {S['brand']}",b["games_intro_meta"],"/games.html",gbody,"/games.html",modal=True))

    # game detail pages
    gfeat = "".join(f"<li>{e(x)}</li>" for x in S["rich"]["game_features"])
    for slug in S["games"]:
        g = GAMES[slug]; gc = b["games"][slug]; gm = S["rich"]["game_meta"][slug]
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in gm["tags"])
        tips = "".join(f"<li>{e(x)}</li>" for x in gm["tips"])
        related = "".join(gcard(S,s,tags=False,modal=False) for s in S["games"] if s!=slug)
        ld = json.dumps({"@context":"https://schema.org","@type":"VideoGame","name":g["game_name"],"url":f"{S['base_url']}/game-{slug}.html","genre":"Social casual game","gamePlatform":"Web browser","applicationCategory":"Game","operatingSystem":"Web","publisher":{"@type":"Organization","name":S["brand"]},"offers":{"@type":"Offer","price":"0","priceCurrency":"USD"}})
        body = f'''<section class="block" style="padding-top:44px"><div class="container">
<div style="margin-bottom:18px"><a href="/games.html" style="font-weight:700;font-size:.9rem">← Back to all games</a></div>
<div style="margin-bottom:22px"><span class="cat" style="position:static;display:inline-block;width:max-content;background:var(--primary);color:#fff;padding:5px 12px;border-radius:999px;font-size:.72rem;font-weight:700">{e(gm["category"])}</span>
<h1 style="margin-top:10px">{e(g["game_name"])}</h1><p style="color:var(--secondary);font-weight:700;margin:0">{e(gc["tagline"])}</p><div class="tags" style="margin-top:10px">{tags}</div></div>
<div class="gwrap"><div><iframe class="gameframe" src="{e(g["iframe_url"])}" title="Play {e(g["game_name"])} free" allowfullscreen loading="lazy"></iframe>
<div style="margin-top:24px">{paras(gc["description"])}<h2 style="font-size:1.3rem;color:var(--primary);margin:1.2em 0 .4em">How it plays</h2>{paras(gc["how_to_play"])}</div></div>
<aside><div class="panel"><h3>Game features</h3><ul class="flist">{gfeat}</ul></div><div class="panel"><h3>Tips for a good session</h3><ul class="flist">{tips}</ul></div>
<div class="panel" style="background:color-mix(in srgb,var(--primary) 8%,#fff)"><h3>Play well</h3><p style="color:var(--muted);font-size:.92rem;margin:0">{e(S["micro"]["playwell"])}</p></div></aside></div></div></section>
<section class="block alt"><div class="container"><div class="sec-head"><span class="eyebrow">Keep playing</span><h2>More games to try</h2></div><div class="grid g3">{related}</div></div></section>'''
        open(os.path.join(out,f"game-{slug}.html"),"w").write(shell(S,f"{g['game_name']} — Play Free at {S['brand']}",gc["tagline"],f"/game-{slug}.html",body,"/games.html",f'<script type="application/ld+json">{ld}</script>'))

    # about
    team = "".join(f'<div class="feature"><div class="avatar" style="width:56px;height:56px;font-size:1.1rem;margin-bottom:14px">{e(initials(m["name"]))}</div><h3>{e(m["name"])}</h3><div class="tl" style="color:var(--secondary);font-weight:700;font-size:.85rem;margin-bottom:8px">{e(m["role"])}</div><p style="color:var(--muted);font-size:.95rem">{e(m["bio"])}</p></div>' for m in b["about"]["team"])
    vals = "".join(f'<div class="feature"><div class="ic">{icon(v["icon"])}</div><h3>{e(v["title"])}</h3><p>{e(v["desc"])}</p></div>' for v in S["rich"]["values"])
    abody = f'<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#fff">Our story</span><h1>About {e(S["brand"])}</h1><p>{e(b["about"]["meta"])}</p></div></section><section class="block"><div class="container prose">{paras(b["about"]["story"])}</div></section><section class="block alt"><div class="container"><div class="sec-head"><span class="eyebrow">What we value</span><h2>What we stand for</h2></div><div class="grid g3">{vals}</div></div></section><section class="block"><div class="container"><div class="sec-head"><span class="eyebrow">The team</span><h2>Meet the crew</h2></div><div class="grid g3">{team}</div></div></section>'
    open(os.path.join(out,"about.html"),"w").write(shell(S,f"About — {S['brand']}",b["about"]["meta"],"/about.html",abody,"/about.html",org_ld(S)))

    # contact
    c = b["contact"]
    cbody = f'''<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#fff">Say hello</span><h1>Contact {e(S["brand"])}</h1><p>{e(c["meta"])}</p></div></section>
<section class="block"><div class="container gwrap"><div>{paras(c["intro"])}<form class="panel" onsubmit="return false"><h3>Send us a message</h3>
<input style="width:100%;border:1.6px solid var(--line);border-radius:10px;padding:11px 14px;margin-bottom:14px" placeholder="Your name"><input style="width:100%;border:1.6px solid var(--line);border-radius:10px;padding:11px 14px;margin-bottom:14px" placeholder="you@example.com"><textarea style="width:100%;border:1.6px solid var(--line);border-radius:10px;padding:11px 14px;margin-bottom:16px;min-height:120px" placeholder="How can we help?"></textarea><button class="btn" type="submit">Send message</button></form></div>
<aside><div class="panel"><h3>Reach us directly</h3><ul class="flist"><li>Email: {e(c["email"])}</li><li>Support hours: {e(c["hours"])}</li><li>Community: {e(c["community"])}</li></ul></div>
<div class="panel" style="background:color-mix(in srgb,var(--primary) 8%,#fff)"><h3>{e(S["micro"]["contact_before"])}</h3><p style="color:var(--muted);font-size:.92rem;margin:0">{S["micro"]["contact_aside"]}</p></div></aside></div></section>'''
    open(os.path.join(out,"contact.html"),"w").write(shell(S,f"Contact — {S['brand']}",c["meta"],"/contact.html",cbody,"/contact.html"))

    # faq
    qs = "".join(f'<div class="qa"><button>{e(q["q"])}<span class="pm">+</span></button><div class="ans"><p>{e(q["a"])}</p></div></div>' for q in S["rich"]["faq"])
    fbody = f'<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#fff">Help centre</span><h1>Frequently asked questions</h1><p>Everything you might want to know about playing at {e(S["brand"])}.</p></div></section><section class="block"><div class="container"><div class="faq">{qs}</div><div class="callout" style="max-width:820px;margin:30px auto 0">{S["micro"]["faq_still"]}</div></div></section>'
    open(os.path.join(out,"faq.html"),"w").write(shell(S,f"FAQ — {S['brand']}",f"Answers to common questions about free social gaming at {S['brand']}.","/faq.html",fbody,"/faq.html"))

    # responsible play
    rp = "".join(f'<div class="panel"><h3>{e(x["title"])}</h3><p style="color:var(--muted);margin:0">{e(x["body"])}</p></div>' for x in S["rich"]["responsible"])
    rbody = f'<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#fff">Play well</span><h1>Responsible Play</h1><p>{e(S["micro"]["rp_hero"])}</p></div></section><section class="block"><div class="container prose"><div class="callout">{e(S["micro"]["rp_callout"])}</div>{rp}</div></section>'
    open(os.path.join(out,"responsible-play.html"),"w").write(shell(S,f"Responsible Play — {S['brand']}",f"How {S['brand']} supports healthy, balanced free social gaming for adults 21+.","/responsible-play.html",rbody,"/responsible-play.html"))

    # legal
    def slugify(t): return t.lower().replace(" ","-").replace("&","and").replace(",","")
    def legal(title, intro, sections, meta, canon):
        secs_all = [(title.split()[0]+" overview" if False else "Overview", intro)] + [(x["h"],x["b"]) for x in sections]
        toc = "".join(f'<li><a href="#{slugify(h)}">{e(h)}</a></li>' for h,_ in secs_all)
        body_secs = "".join(f'<h2 id="{slugify(h)}">{e(h)}</h2>{paras(bd)}' for h,bd in secs_all)
        pg = f'<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#fff">Legal</span><h1>{e(title)}</h1><p>Last updated: 9 July 2026</p></div></section><section class="block"><div class="container prose"><div class="toc"><h3>On this page</h3><ul>{toc}</ul></div>{body_secs}<div class="callout" style="margin-top:34px">{e(S["micro"]["legal_callout"])}</div></div></section>'
        open(os.path.join(out,canon.strip("/")),"w").write(shell(S,f"{title} — {S['brand']}",meta,canon,pg,canon))
    legal("Privacy Policy", b["privacy"], S["rich"]["privacy_sections"], f"How {S['brand']} collects, uses and protects your information.", "/privacy.html")
    legal("Terms of Use", b["terms"], S["rich"]["terms_sections"], f"The terms that govern your use of the free social games at {S['brand']}.", "/terms.html")

    # sitemap / robots
    urls = ["/index.html","/games.html","/about.html","/contact.html","/faq.html","/responsible-play.html","/privacy.html","/terms.html"]+[f"/game-{s}.html" for s in S["games"]]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"  <url><loc>{S['base_url']}{u}</loc><changefreq>weekly</changefreq></url>\n" for u in urls)+"</urlset>\n"
    open(os.path.join(out,"sitemap.xml"),"w").write(sm)
    open(os.path.join(out,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\nSitemap: {S['base_url']}/sitemap.xml\n")

    # images
    imgdir = os.path.join(out,"assets","games-images"); os.makedirs(imgdir,exist_ok=True)
    for s in S["games"]:
        src = os.path.join(ROOT,"assets/games-images",GAMES[s]["image"])
        if os.path.exists(src): shutil.copy2(src, os.path.join(imgdir, GAMES[s]["image"]))

def build(slug):
    S = {"slug":slug}
    load(S)
    S["out"] = os.path.join(ROOT,"builds",slug); os.makedirs(S["out"],exist_ok=True)
    open(os.path.join(S["out"],"style.css"),"w").write(css(S))
    open(os.path.join(S["out"],"index.html"),"w").write(index_page(S))
    build_inner(S)
    n = len([f for f in os.listdir(S["out"]) if f.endswith(".html")])
    print(f"built {slug} ({S['layout']}) — {n} HTML pages")

if __name__ == "__main__":
    for slug in (sys.argv[1:] or ["cinderpeak-arcade","driftwave-games"]):
        build(slug)
