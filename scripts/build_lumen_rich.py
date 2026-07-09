#!/usr/bin/env python3
"""Rich, full-depth build for a single showcase site: Lumen Play.
Reuses copy from state/content/lumen-play.json and layers on extra content
(features, how-it-works, categories, FAQ, responsible-play, expanded legal) plus
a polished design with interactive elements. Structural QA rules preserved:
21+ everywhere / no 18+, one iframe per game page, SEO tags, sitemap/robots,
no banned words in human-readable language."""
import csv, json, os, html, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "builds", "lumen-play")
GAMES = {r["slug"]: r for r in csv.DictReader(open(os.path.join(ROOT, "assets/games-data/game-data.csv")))}
C = json.load(open(os.path.join(ROOT, "state/content/lumen-play.json")))
BRAND = "Lumen Play"
BASE = "https://lumen-play.pages.dev"

def e(s): return html.escape(str(s), quote=True)
def paras(t): return "\n".join(f"<p>{e(p.strip())}</p>" for p in t.split("\n") if p.strip())

# ---------- extra authored content (cozy-lounge voice, zero banned words) ----------
GAME_ORDER = ["24k-dragon","athena-ascending","banana-rock","bell-of-fortune","boat-bonanza","bugs-party"]
CATEGORY = {
    "24k-dragon":"Adventure reels","athena-ascending":"Mythic reels","banana-rock":"Feel-good reels",
    "bell-of-fortune":"Classic spinners","boat-bonanza":"Feel-good reels","bugs-party":"Feel-good reels",
}
GAME_TAGS = {
    "24k-dragon":["Adventure","High-energy","Dragons"],
    "athena-ascending":["Mythology","Cascading reels","Epic"],
    "banana-rock":["Music","Playful","Retro fun"],
    "bell-of-fortune":["Classic","Fruit reels","Easy-going"],
    "boat-bonanza":["Coastal","Relaxing","Bright"],
    "bugs-party":["Cute","Colourful","Cluster fun"],
}
GAME_TIPS = {
    "24k-dragon":["Settle into a comfy autoplay pace and watch the dragon meter climb.","There is no cost and nothing of monetary value at stake — enjoy the ride.","Try a longer session to see the feature round appear."],
    "athena-ascending":["Cascading symbols can chain together, so watch a single spin unfold fully.","Play in fullscreen for the best view of the temple backdrop.","It is purely for fun, so take your time between spins."],
    "banana-rock":["Turn the sound on — the soundtrack is half the charm.","Look for the band symbols lining up across the reels.","Great for a short, cheerful break."],
    "bell-of-fortune":["A gentle classic — perfect for winding down.","Keep an eye on the lucky bell symbol.","No downloads and no purchases, ever."],
    "boat-bonanza":["The fishing theme suits a relaxed, unhurried pace.","Bright visuals make it easy on the eyes for longer sessions.","Everything here is free social play."],
    "bugs-party":["Symbols pay in clusters rather than lines, so watch the whole grid.","The colourful bugs make it a cheerful pick-me-up.","Play instantly in your browser, on any device."],
}
GAME_FEATURES = ["Instant browser play — no download","Free forever, no purchases","Feature rounds & free spins","Playable on mobile, tablet & desktop"]

FEATURES = [
    ("bolt","Instant play","Every game runs straight in your browser. No downloads, no installs, no waiting — press play and you are in."),
    ("heart","Free, always","There is nothing to buy and nothing of monetary value at stake. Lumen Play is free social gaming, start to finish."),
    ("sofa","A cosy library","We hand-pick relaxed, good-looking games and arrange them like a comfortable lounge you can drop into any time."),
    ("device","Any device","Curl up with your phone or settle in at your desk — the whole lounge scales neatly to whatever screen you are on."),
]
HOWTO = [
    ("Confirm you are 21+","A quick age check keeps our lounge a space for adults. Confirm once and you are set."),
    ("Wander the lounge","Browse the shelves, filter by mood, and pick a game that suits the evening."),
    ("Press play","The game loads instantly in your browser. Stay as long as you like — it is always free."),
]
STATS = [("40+","free games in the lounge"),("21+","adults-only community"),("$0","to play, forever"),("100%","browser-based")]
CATEGORIES = [
    ("Adventure reels","Big, bold journeys with dragons, temples and treasure to explore at your own pace."),
    ("Classic spinners","Easy-going fruit and bell reels for when you just want to unwind."),
    ("Feel-good reels","Bright, cheerful games with music, animals and a warm sense of play."),
]
FAQ = [
    ("Is Lumen Play really free?","Yes, completely. There is nothing to purchase and no account fees. Every game in the lounge is free social play, and it always will be."),
    ("Can I earn money by playing?","No. Lumen Play is purely for entertainment. Nothing of monetary value is at stake and nothing of monetary value can be gained. It is social gaming, made to relax with."),
    ("Do I need to download anything?","Not at all. Every game runs instantly inside your web browser on any modern phone, tablet or computer. There is nothing to install."),
    ("Who can play?","Lumen Play is strictly for adults aged 21 and over. We show an age check the first time you visit to keep the lounge an adults-only space."),
    ("How often do new games arrive?","We add fresh games to the lounge regularly, choosing titles that match our calm, cosy mood. Pop back now and then to see what is new."),
    ("Is my information safe?","We keep data collection to a minimum and never sell your information. Our Privacy Policy explains exactly what we collect and how it is handled."),
    ("How do I get help?","Drop us a line any time through our Contact page. A real person from our small team will get back to you."),
]
RESPONSIBLE = [
    ("Play for fun, nothing more","Lumen Play exists for relaxation and enjoyment. Because there is no cost and nothing of monetary value involved, the only thing to gain here is a good time. Keep it that way by treating every session as light entertainment."),
    ("Keep an eye on the clock","Games are designed to be moreish, so it is easy to lose track of time. Set yourself a gentle limit before you start, and take regular breaks to stretch, hydrate and rest your eyes."),
    ("Make space for the rest of life","Gaming is best as one part of a balanced day. If a session ever starts to feel like a chore rather than a treat, that is a good moment to step away and come back another time."),
    ("It is a lounge, not a race","There are no streaks to protect and nothing to chase. Play at whatever pace feels comfortable, and never feel you have to keep going."),
    ("Adults only, 21+","Our community is for grown-ups. Please keep your devices secure so younger household members cannot access adult social gaming, and never share access with anyone under 21."),
]

# expanded legal — reuse the base intro then add proper sections
PRIVACY_SECTIONS = [
    ("Introduction", C["privacy"]),
    ("Information we collect","We aim to collect as little as possible. When you visit Lumen Play we may receive standard technical data such as your browser type, device type, general region and the pages you view. If you contact us, we receive the details you choose to send, such as your name and email address. We do not ask for financial details because there is nothing to purchase on this site."),
    ("Cookies and analytics","We use a small number of cookies to remember that you have confirmed your age and to understand, in aggregate, how the lounge is used. Analytics data is anonymised wherever possible and is only used to improve the games and pages we offer. You can clear or block cookies in your browser at any time, though the age confirmation may then reappear on each visit."),
    ("How we use information","We use the limited information we hold to operate and improve the site, to respond to your messages, to keep the lounge secure, and to understand which games our community enjoys most. We never use your data to imply or offer anything of monetary value."),
    ("Legal bases","Where data protection law applies, we rely on our legitimate interest in running a safe, functional website, on your consent for optional cookies, and on the need to respond to requests you send us."),
    ("Sharing your information","We do not sell your personal information. We share data only with trusted service providers who help us host the site and measure traffic, and only to the extent they need it to perform that work. Third-party games are provided by their own studios under their own privacy practices."),
    ("Data retention","We keep personal information only for as long as it is needed for the purpose it was collected, after which it is deleted or anonymised. Contact messages are kept for a reasonable period so we can follow up with you."),
    ("Your rights","Depending on where you live, you may have the right to access, correct, delete or restrict the use of your personal information, and to object to certain processing. To exercise any of these rights, contact us and we will respond within the time frame the law allows."),
    ("Adults only","Lumen Play is intended solely for adults aged 21 and over. We do not knowingly collect information from anyone under that age. If you believe a minor has provided us information, please contact us so we can remove it."),
    ("Security","We use reasonable technical and organisational measures to protect the information we hold. No online service can be completely secure, but we work to keep your data safe and to limit who can access it."),
    ("Changes to this policy","We may update this policy from time to time. When we do, we will revise the date at the foot of the page and, where appropriate, highlight significant changes on the site."),
    ("Contact us","If you have any questions about this Privacy Policy or how your information is handled, please reach us through the Contact page and we will be glad to help."),
]
TERMS_SECTIONS = [
    ("Acceptance of these terms", C["terms"]),
    ("Eligibility","Lumen Play is available only to adults aged 21 and over. By using the site you confirm that you meet this age requirement. We may ask you to confirm your age and may restrict access if we believe this requirement is not met."),
    ("Nature of the service","Lumen Play provides free-to-play social games for entertainment only. There is nothing to purchase, nothing of monetary value is at stake, and nothing of monetary value can be gained through play. The games are provided purely for enjoyment."),
    ("Acceptable use","You agree to use the site lawfully and respectfully. You must not attempt to disrupt the service, interfere with other visitors, reverse engineer the games, or use automated tools to access the site in a way that harms its operation."),
    ("Intellectual property","The Lumen Play name, design, text and arrangement of the lounge are owned by us or our licensors. The individual games remain the property of the studios that created them. You may enjoy the content for personal, non-commercial use but may not copy or redistribute it."),
    ("Third-party games","Games on Lumen Play are embedded from third-party studios. While we curate the lounge with care, we do not control those games and are not responsible for their content or availability. Their use may be subject to the studio's own terms."),
    ("Disclaimers","The site is provided on an “as is” and “as available” basis. We do not guarantee that the lounge will always be uninterrupted, error-free or that every game will load in every region, as some studios apply their own restrictions."),
    ("Limitation of liability","To the fullest extent permitted by law, Lumen Play and its team will not be liable for any indirect or consequential loss arising from your use of the site. Because the service is free and involves nothing of monetary value, your use is entirely at your own discretion."),
    ("Changes to the service","We may add, change or remove games and features at any time as we tend the lounge. We may also update these terms; continued use of the site after changes means you accept the revised terms."),
    ("Termination","We may suspend or withdraw access to the site, in whole or in part, if these terms are broken or if we need to for technical or legal reasons."),
    ("Governing law","These terms are governed by the laws of the jurisdiction in which Lumen Play operates, without regard to conflict-of-law principles."),
    ("Contact us","If you have questions about these Terms of Use, please get in touch through the Contact page."),
]

ICONS = {
 "bolt":'<path d="M13 2L3 14h7l-1 8 10-12h-7z"/>',
 "heart":'<path d="M12 21s-7-4.5-9.5-9A5 5 0 0112 5a5 5 0 019.5 7c-2.5 4.5-9.5 9-9.5 9z"/>',
 "sofa":'<path d="M4 11V8a3 3 0 013-3h10a3 3 0 013 3v3M3 11a2 2 0 012 2v3h14v-3a2 2 0 012-2 2 2 0 012 2v5h-2v2h-2v-2H6v2H4v-2H2v-5a2 2 0 012-2z"/>',
 "device":'<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M2 20h20"/>',
}
def icon(name):
    return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'

# ---------------------------- design (CSS) ----------------------------
CSS = """:root{--primary:#6C4AB6;--primary-d:#553796;--secondary:#8D72E1;--accent:#B9E0FF;--bg:#F5F3FF;--surface:#ffffff;--ink:#241f33;--muted:#6b6480;--line:#e7e1f7;--radius:16px;--shadow:0 10px 30px rgba(76,52,120,.10);--shadow-sm:0 4px 14px rgba(76,52,120,.08)}
*{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth}
body{font-family:'Lora',Georgia,serif;color:var(--ink);background:var(--bg);line-height:1.7;font-size:17px;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4,.brand,.btn,.eyebrow,nav a,.chip{font-family:'Poppins',system-ui,sans-serif}
h1{font-size:clamp(2.1rem,4.5vw,3.3rem);line-height:1.1;letter-spacing:-.02em}
h2{font-size:clamp(1.6rem,3vw,2.2rem);line-height:1.15;color:var(--ink)}
h3{font-size:1.2rem}
p{margin:0 0 1em}a{color:var(--primary);text-decoration:none}a:hover{color:var(--primary-d)}
img{max-width:100%;display:block}
.container{max-width:1140px;margin:0 auto;padding:0 22px}
.eyebrow{display:inline-block;text-transform:uppercase;letter-spacing:.14em;font-size:.72rem;font-weight:700;color:var(--secondary);margin-bottom:14px}
.btn{display:inline-flex;align-items:center;gap:8px;background:var(--primary);color:#fff;padding:13px 26px;border-radius:999px;font-weight:600;font-size:.95rem;border:none;cursor:pointer;transition:transform .15s,box-shadow .15s;box-shadow:var(--shadow-sm)}
.btn:hover{transform:translateY(-2px);color:#fff;box-shadow:var(--shadow)}
.btn.ghost{background:transparent;color:var(--primary);box-shadow:none;border:1.5px solid var(--line)}
.btn.ghost:hover{border-color:var(--primary);background:#fff}
.btn.light{background:#fff;color:var(--primary)}
/* top announcement bar */
.topbanner{background:#1f1a2e;color:#e6dbff;font-family:'Poppins',sans-serif;font-size:.8rem;padding:9px 0;letter-spacing:.01em}
.topbanner .container{display:flex;justify-content:center;align-items:center;gap:16px;flex-wrap:wrap;text-align:center}
.topbanner strong{color:#fff}.topbanner a{color:var(--accent);font-weight:600}.topbanner .sep{opacity:.35}
@media(max-width:640px){.topbanner .hideSm{display:none}}
/* bottom disclaimer */
.disclaimer{background:#15101f;color:#8b839f;font-size:.8rem;line-height:1.65;padding:24px 0}
.disclaimer .container{max-width:1040px}.disclaimer strong{color:#b3aac9}
/* header */
.topbar{position:sticky;top:0;z-index:60;background:rgba(245,243,255,.85);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.topbar .container{display:flex;align-items:center;justify-content:space-between;height:70px}
.brand{font-size:1.35rem;font-weight:700;color:var(--primary);display:flex;align-items:center;gap:9px}
.brand .dot{width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,var(--primary),var(--secondary));display:inline-block}
nav.main ul{display:flex;gap:26px;list-style:none;align-items:center}
nav.main a{color:var(--ink);font-weight:500;font-size:.95rem}
nav.main a:hover,nav.main a[aria-current]{color:var(--primary)}
.navtoggle{display:none;background:none;border:0;cursor:pointer;font-size:1.6rem;color:var(--ink)}
/* hero */
.hero{position:relative;overflow:hidden;background:linear-gradient(150deg,var(--primary),var(--secondary));color:#fff;padding:84px 0 92px}
.hero:before{content:"";position:absolute;inset:0;background:radial-gradient(600px 300px at 80% -10%,rgba(185,224,255,.5),transparent),radial-gradient(500px 260px at 5% 110%,rgba(255,255,255,.18),transparent)}
.hero .container{position:relative;display:grid;grid-template-columns:1.05fr .95fr;gap:44px;align-items:center}
.hero h1{color:#fff}.hero p.lead{font-size:1.2rem;max-width:34ch;color:#f3edff;margin:18px 0 26px}
.hero .cta{display:flex;gap:14px;flex-wrap:wrap}
.hero .chipset{display:flex;gap:10px;flex-wrap:wrap;margin-top:26px}
.chip{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);color:#fff;padding:6px 14px;border-radius:999px;font-size:.8rem;font-weight:500}
.heroart{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.25);border-radius:22px;padding:16px;box-shadow:0 20px 50px rgba(40,20,80,.35)}
.heroart .g{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.heroart img{border-radius:12px;height:120px;width:100%;object-fit:cover}
/* sections */
section.block{padding:76px 0}
section.alt{background:linear-gradient(#fff,#fbfaff)}
.sec-head{text-align:center;max-width:640px;margin:0 auto 46px}
.sec-head p{color:var(--muted)}
.grid{display:grid;gap:24px}
.g4{grid-template-columns:repeat(4,1fr)}.g3{grid-template-columns:repeat(3,1fr)}.g2{grid-template-columns:repeat(2,1fr)}
/* stat band */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow-sm);padding:30px;margin-top:-46px;position:relative;z-index:5}
.stats .s{text-align:center}.stats .n{font-family:'Poppins';font-size:2rem;font-weight:700;color:var(--primary)}.stats .l{color:var(--muted);font-size:.9rem}
/* feature cards */
.feature{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:28px;box-shadow:var(--shadow-sm);transition:transform .15s,box-shadow .15s}
.feature:hover{transform:translateY(-4px);box-shadow:var(--shadow)}
.feature .ic{width:52px;height:52px;border-radius:14px;background:linear-gradient(135deg,var(--accent),#e9f4ff);display:flex;align-items:center;justify-content:center;color:var(--primary);margin-bottom:16px}
.feature .ic svg{width:26px;height:26px}
.feature h3{margin-bottom:8px}.feature p{color:var(--muted);margin:0;font-size:.96rem}
/* steps */
.step{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:28px;box-shadow:var(--shadow-sm);position:relative}
.step .num{font-family:'Poppins';font-weight:700;color:#fff;background:var(--primary);width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:14px}
.step h3{margin-bottom:6px}.step p{color:var(--muted);margin:0;font-size:.96rem}
/* game cards */
.gcard{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;box-shadow:var(--shadow-sm);transition:transform .15s,box-shadow .15s;display:flex;flex-direction:column}
.gcard:hover{transform:translateY(-5px);box-shadow:var(--shadow)}
.gcard .thumb{position:relative}.gcard img{height:180px;width:100%;object-fit:cover}
.gcard .cat{position:absolute;top:12px;left:12px;background:rgba(36,31,51,.78);color:#fff;font-family:'Poppins';font-size:.7rem;font-weight:600;padding:5px 10px;border-radius:999px;letter-spacing:.03em}
.gcard .body{padding:18px 18px 20px;display:flex;flex-direction:column;gap:8px;flex:1}
.gcard h3{margin:0}.gcard .tl{color:var(--secondary);font-family:'Poppins';font-size:.82rem;font-weight:600}
.gcard p{color:var(--muted);font-size:.92rem;margin:0}
.gcard .foot{margin-top:auto;padding-top:8px}
.tags{display:flex;gap:7px;flex-wrap:wrap}.tag{background:#f0ecfb;color:var(--primary);font-family:'Poppins';font-size:.72rem;font-weight:600;padding:4px 10px;border-radius:999px}
/* filter bar */
.filters{display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-bottom:34px}
.filters button{font-family:'Poppins';font-weight:600;font-size:.85rem;border:1.5px solid var(--line);background:#fff;color:var(--muted);padding:9px 18px;border-radius:999px;cursor:pointer;transition:.15s}
.filters button.active,.filters button:hover{background:var(--primary);color:#fff;border-color:var(--primary)}
/* testimonials */
.tcard{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:26px;box-shadow:var(--shadow-sm)}
.tcard .stars{color:#f4b740;letter-spacing:2px;margin-bottom:10px}
.tcard blockquote{font-size:1.02rem;margin:0 0 16px}
.tcard .who{display:flex;align-items:center;gap:12px}
.avatar{width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;display:flex;align-items:center;justify-content:center;font-family:'Poppins';font-weight:700}
.tcard .who .m{font-family:'Poppins';font-weight:600;font-size:.92rem}.tcard .who .d{color:var(--muted);font-size:.82rem}
/* faq accordion */
.faq{max-width:820px;margin:0 auto}
.qa{background:var(--surface);border:1px solid var(--line);border-radius:14px;margin-bottom:14px;box-shadow:var(--shadow-sm);overflow:hidden}
.qa button{width:100%;text-align:left;background:none;border:0;padding:20px 22px;font-family:'Poppins';font-weight:600;font-size:1.02rem;color:var(--ink);cursor:pointer;display:flex;justify-content:space-between;gap:16px;align-items:center}
.qa button .pm{color:var(--primary);font-size:1.4rem;transition:transform .2s}
.qa.open button .pm{transform:rotate(45deg)}
.qa .ans{max-height:0;overflow:hidden;transition:max-height .28s ease;padding:0 22px}
.qa.open .ans{max-height:340px;padding-bottom:20px}
.qa .ans p{color:var(--muted);margin:0}
/* cta band */
.ctaband{background:linear-gradient(135deg,var(--primary),var(--secondary));color:#fff;border-radius:24px;padding:52px;text-align:center;box-shadow:var(--shadow)}
.ctaband h2{color:#fff}.ctaband p{color:#efe9ff;max-width:52ch;margin:12px auto 26px}
.newsletter{display:flex;gap:10px;max-width:440px;margin:0 auto;flex-wrap:wrap;justify-content:center}
.newsletter input{flex:1;min-width:220px;border:0;border-radius:999px;padding:13px 20px;font-family:'Poppins';font-size:.95rem}
/* game detail */
.gamehead{display:grid;grid-template-columns:1fr;gap:10px;margin-bottom:22px}
.gameframe{width:100%;aspect-ratio:16/10;min-height:440px;border:0;border-radius:18px;background:#0c0a14;box-shadow:var(--shadow)}
.gwrap{display:grid;grid-template-columns:1fr .42fr;gap:34px;align-items:start}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:22px;box-shadow:var(--shadow-sm);margin-bottom:20px}
.panel h3{margin-bottom:12px}
.flist{list-style:none;display:flex;flex-direction:column;gap:10px}
.flist li{display:flex;gap:10px;align-items:flex-start;color:var(--muted);font-size:.95rem}
.flist li:before{content:"✦";color:var(--secondary);font-size:.9rem;margin-top:2px}
/* legal / content pages */
.page-hero{background:linear-gradient(150deg,var(--primary),var(--secondary));color:#fff;padding:64px 0}
.page-hero h1{color:#fff}.page-hero p{color:#efe9ff;max-width:60ch;margin-top:10px}
.prose{max-width:820px;margin:0 auto}.prose h2{margin:1.6em 0 .5em;font-size:1.35rem;color:var(--primary)}
.prose p{color:#3a3450}.toc{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 22px;margin-bottom:34px;box-shadow:var(--shadow-sm)}
.toc h3{font-size:.8rem;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-bottom:10px}
.toc ul{list-style:none;columns:2;gap:14px}.toc a{font-size:.92rem}
.callout{background:#f0ecfb;border-left:4px solid var(--primary);border-radius:10px;padding:18px 20px;margin:24px 0;color:var(--ink)}
/* footer */
footer.site{background:#1f1a2e;color:#c7c0da;padding:60px 0 30px;margin-top:0}
footer.site .cols{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr;gap:32px;margin-bottom:34px}
footer.site h4{color:#fff;font-size:.85rem;text-transform:uppercase;letter-spacing:.1em;margin-bottom:14px}
footer.site a{color:#c7c0da;display:block;padding:5px 0;font-size:.93rem}footer.site a:hover{color:#fff}
footer .fbrand{font-family:'Poppins';font-weight:700;color:#fff;font-size:1.2rem;margin-bottom:10px}
footer .fbrand small{display:block;font-weight:400;color:#9d95b5;font-size:.9rem;margin-top:8px;line-height:1.5}
footer .legalnote{border-top:1px solid #352d4a;padding-top:22px;font-size:.82rem;color:#9d95b5;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap}
.age-badge{display:inline-flex;align-items:center;gap:6px;background:#352d4a;color:#fff;font-family:'Poppins';font-weight:700;font-size:.75rem;padding:4px 10px;border-radius:8px}
/* age gate */
.agewrap{position:fixed;inset:0;background:rgba(24,18,38,.92);backdrop-filter:blur(6px);z-index:999;display:flex;align-items:center;justify-content:center;padding:20px}
.agebox{background:#fff;max-width:460px;text-align:center;border-radius:22px;padding:40px 34px;box-shadow:0 30px 70px rgba(0,0,0,.4)}
.agebox .dot{width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,var(--primary),var(--secondary));margin:0 auto 16px}
.agebox h2{color:var(--primary)}.agebox p{color:var(--muted);font-size:.96rem}
.agebox .row{display:flex;gap:12px;justify-content:center;margin-top:22px;flex-wrap:wrap}
/* back to top */
#toTop{position:fixed;right:22px;bottom:22px;width:46px;height:46px;border-radius:50%;background:var(--primary);color:#fff;border:0;cursor:pointer;font-size:1.2rem;opacity:0;pointer-events:none;transition:.25s;box-shadow:var(--shadow);z-index:70}
#toTop.show{opacity:1;pointer-events:auto}
/* play-in-iframe modal */
.playmodal{position:fixed;inset:0;background:rgba(8,6,16,.9);backdrop-filter:blur(6px);z-index:200;display:none;align-items:center;justify-content:center;padding:16px}
.playmodal.open{display:flex}
.pm-inner{width:min(1040px,100%);background:#0b0912;border-radius:16px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.6);display:flex;flex-direction:column}
.pm-bar{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 16px;background:var(--ink);color:#fff}
.pm-bar #pmTitle{font-family:'Poppins';font-weight:700;font-size:.95rem}
.pm-bar button{background:rgba(255,255,255,.14);color:#fff;border:0;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;font-size:.82rem;margin-left:8px;font-family:'Poppins'}
.pm-bar button:hover{background:rgba(255,255,255,.28)}
.playmodal iframe{width:100%;border:0;background:#000;height:min(70vh,620px)}
.gcard[data-play]{cursor:pointer}
.playoverlay{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(16,12,32,.32);opacity:0;transition:.2s}
.playoverlay span{width:60px;height:60px;border-radius:50%;background:rgba(255,255,255,.94);color:var(--primary);display:flex;align-items:center;justify-content:center;font-size:1.4rem;padding-left:5px}
.gcard:hover .playoverlay{opacity:1}
.gcard .foot{display:flex;align-items:center;justify-content:space-between;gap:10px}
.gcard .details{font-weight:700;font-size:.8rem;white-space:nowrap;font-family:'Poppins'}
.hidden{display:none!important}
@media(max-width:920px){.hero .container{grid-template-columns:1fr}.gwrap{grid-template-columns:1fr}.footer .cols,footer.site .cols{grid-template-columns:1fr 1fr}}
@media(max-width:760px){
 nav.main{position:fixed;inset:70px 0 auto 0;background:#fff;border-bottom:1px solid var(--line);transform:translateY(-140%);transition:.25s;box-shadow:var(--shadow)}
 nav.main.open{transform:translateY(0)}nav.main ul{flex-direction:column;padding:18px 22px;gap:6px}nav.main a{display:block;padding:10px 0}
 .navtoggle{display:block}
 .g4,.g3,.g2,.stats{grid-template-columns:1fr 1fr}.toc ul{columns:1}footer.site .cols{grid-template-columns:1fr 1fr}
}
@media(max-width:520px){.g4,.g3,.g2,.stats{grid-template-columns:1fr}.ctaband{padding:34px 22px}.hero{padding:60px 0 70px}}
"""

# ---------------------------- shared HTML ----------------------------
NAV_LINKS = [("Home","/index.html"),("Games","/games.html"),("About","/about.html"),
             ("Responsible Play","/responsible-play.html"),("FAQ","/faq.html"),("Contact","/contact.html")]

def head(title, desc, canon_path, jsonld=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{BASE}{canon_path}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{BASE}{canon_path}"><meta property="og:image" content="{BASE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&family=Lora:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/style.css">{jsonld}
</head><body>"""

TOPBAR_MSG = ("<span><strong>21+ only</strong> · Free-to-play social gaming lounge</span>"
              "<span class='sep hideSm'>|</span><span class='hideSm'>No purchases · nothing of monetary value</span>"
              "<span class='sep hideSm'>|</span><a class='hideSm' href='/games.html'>Fresh games added monthly →</a>")
DISCLAIMER = ("<strong>Disclaimer:</strong> Lumen Play is a free-to-play social gaming lounge intended purely for "
    "entertainment. All games are played for fun only and carry no monetary value of any kind. There is nothing to "
    "purchase, nothing to stake, and nothing of monetary value to gain. Practising or doing well in these social games "
    "has no bearing on any activity involving real-world currency, and this site is not a substitute for such activities. "
    "Lumen Play is strictly for adults aged 21 and over. Games are provided by third-party studios and may be unavailable "
    "in some regions. Please play responsibly, set your own limits, and take regular breaks.")

def topbanner():
    return f'<div class="topbanner"><div class="container">{TOPBAR_MSG}</div></div>'

def disclaimer():
    return f'<section class="disclaimer"><div class="container">{DISCLAIMER}</div></section>'

def header(active):
    def li(t,h):
        cur = ' aria-current="page"' if h==active else ''
        return f'<li><a href="{h}"{cur}>{e(t)}</a></li>'
    lis = "".join(li(t,h) for t,h in NAV_LINKS)
    return f"""<header class="topbar"><div class="container">
<a class="brand" href="/index.html"><span class="dot"></span>{BRAND}</a>
<button class="navtoggle" aria-label="Menu" id="navToggle">&#9776;</button>
<nav class="main" id="mainNav"><ul>{lis}<li><a class="btn" href="/games.html">Play free</a></li></ul></nav>
</div></header>"""

def agegate():
    return f"""<div class="agewrap" id="ageGate" role="dialog" aria-modal="true" aria-labelledby="ageTitle">
<div class="agebox"><div class="dot"></div><h2 id="ageTitle">Are you 21 or older?</h2>
<p>{BRAND} is a free-to-play social gaming lounge for adults. You must be 21+ to enter. There are no purchases and nothing of monetary value is involved.</p>
<div class="row"><button class="btn" id="ageYes">I am 21 or older</button><button class="btn ghost" id="ageNo">Leave</button></div>
</div></div>"""

def footer():
    cols = f"""<div><div class="fbrand">{BRAND}<small>{e(CHROME_TAG)}</small></div><span class="age-badge">21+ ONLY</span></div>
<div><h4>Explore</h4><a href="/games.html">All games</a><a href="/about.html">About us</a><a href="/faq.html">FAQ</a><a href="/contact.html">Contact</a></div>
<div><h4>Play well</h4><a href="/responsible-play.html">Responsible play</a><a href="/privacy.html">Privacy policy</a><a href="/terms.html">Terms of use</a></div>
<div><h4>Games</h4>{"".join(f'<a href="/game-{s}.html">{e(GAMES[s]["game_name"])}</a>' for s in GAME_ORDER[:4])}</div>"""
    return f"""<footer class="site"><div class="container">
<div class="cols">{cols}</div>
<div class="legalnote"><span>{e(CHROME_NOTE)}</span><span>&copy; 2026 {BRAND}. For entertainment only.</span></div>
</div></footer>"""

SCRIPTS = """<button id="toTop" aria-label="Back to top">&#8593;</button>
<script>
(function(){var g=document.getElementById('ageGate');if(g){if(localStorage.getItem('age21ok')==='1')g.classList.add('hidden');
 var y=document.getElementById('ageYes'),n=document.getElementById('ageNo');
 if(y)y.onclick=function(){localStorage.setItem('age21ok','1');g.classList.add('hidden');};
 if(n)n.onclick=function(){location.href='https://www.google.com';};}
 var t=document.getElementById('navToggle'),nav=document.getElementById('mainNav');
 if(t)t.onclick=function(){nav.classList.toggle('open');};
 document.querySelectorAll('.qa button').forEach(function(b){b.onclick=function(){b.parentElement.classList.toggle('open');};});
 document.querySelectorAll('.filters button').forEach(function(b){b.onclick=function(){
   document.querySelectorAll('.filters button').forEach(function(x){x.classList.remove('active');});b.classList.add('active');
   var f=b.getAttribute('data-f');document.querySelectorAll('.gcard').forEach(function(c){
     c.style.display=(f==='all'||c.getAttribute('data-cat')===f)?'':'none';});};});
 var tt=document.getElementById('toTop');window.addEventListener('scroll',function(){
   if(window.scrollY>500)tt.classList.add('show');else tt.classList.remove('show');});
 tt.onclick=function(){window.scrollTo({top:0,behavior:'smooth'});};
})();
</script></body></html>"""

CHROME_TAG = "A cosy corner of free-to-play games, made by friends for friends."
CHROME_NOTE = "Strictly 21+. Lumen Play is a free social gaming lounge — every game is purely for fun, with no purchases and nothing of monetary value at stake."

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

def shell(title, desc, canon, body, active, jsonld="", modal=False):
    m = (MODAL_HTML + MODAL_JS) if modal else ""
    return head(title, desc, canon, jsonld) + agegate() + topbanner() + header(active) + "<main>" + body + "</main>" + footer() + disclaimer() + m + SCRIPTS

def stars(): return '<span class="stars">★★★★★</span>'
def initials(name): return "".join(w[0] for w in name.replace(".","").split()[:2]).upper()

def gcard(slug, with_tags=True, modal=True):
    g = GAMES[slug]; gc = C["games"][slug]
    tags = "".join(f'<span class="tag">{e(t)}</span>' for t in GAME_TAGS[slug]) if with_tags else ""
    thumb = (f'<div class="thumb"><img src="/assets/games-images/{e(g["image"])}" alt="{e(g["game_name"])} cover" loading="lazy">'
             f'<span class="cat">{e(CATEGORY[slug])}</span>')
    body = (f'<div class="body"><h3>{e(g["game_name"])}</h3><div class="tl">{e(gc["tagline"])}</div>'
            f'<p>{e(" ".join(gc["description"].split()[:24]))}…</p>')
    if modal:
        return (f'<div class="gcard" data-play data-url="{e(g["iframe_url"])}" data-title="{e(g["game_name"])}" '
                f'role="button" tabindex="0" data-cat="{e(CATEGORY[slug])}" aria-label="Play {e(g["game_name"])}">'
                f'{thumb}<span class="playoverlay"><span>&#9654;</span></span></div>'
                f'{body}<div class="foot"><div class="tags">{tags}</div>'
                f'<a class="details" href="/game-{slug}.html">Details &rarr;</a></div></div></div>')
    return (f'<a class="gcard" href="/game-{slug}.html" data-cat="{e(CATEGORY[slug])}">'
            f'{thumb}</div>{body}<div class="foot"><div class="tags">{tags}</div></div></div></a>')

# ---------------------------- pages ----------------------------
def build():
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT,"style.css"),"w").write(CSS)

    # ---------- INDEX ----------
    hero_imgs = "".join(f'<img src="/assets/games-images/{e(GAMES[s]["image"])}" alt="{e(GAMES[s]["game_name"])} cover" loading="lazy">' for s in GAME_ORDER[:4])
    feats = "".join(f'<div class="feature"><div class="ic">{icon(i)}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i,t,d in FEATURES)
    steps = "".join(f'<div class="step"><div class="num">{n}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for n,(t,d) in enumerate(HOWTO,1))
    stats = "".join(f'<div class="s"><div class="n">{e(n)}</div><div class="l">{e(l)}</div></div>' for n,l in STATS)
    cats = "".join(f'<div class="feature"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t,d in CATEGORIES)
    fg = "".join(gcard(s) for s in GAME_ORDER)
    tests = "".join(f"""<div class="tcard">{stars()}<blockquote>“{e(t['text'])}”</blockquote>
<div class="who"><div class="avatar">{e(initials(t['name']))}</div><div><div class="m">{e(t['name'])}</div><div class="d">{e(t['date'])}</div></div></div></div>""" for t in C["testimonials"])
    faqs = "".join(f'<div class="qa"><button>{e(q)}<span class="pm">+</span></button><div class="ans"><p>{e(a)}</p></div></div>' for q,a in FAQ[:5])
    org_ld = json.dumps({"@context":"https://schema.org","@type":"Organization","name":BRAND,"url":BASE,"description":C["tagline"]})
    body = f"""
<section class="hero"><div class="container">
<div><span class="eyebrow" style="color:#e6dbff">Free-to-play · 21+ · Social gaming</span>
<h1>{e(C['hero_headline'])}</h1><p class="lead">{e(C['hero_intro'])}</p>
<div class="cta"><a class="btn light" href="/games.html">Browse the lounge</a><a class="btn ghost" style="color:#fff;border-color:rgba(255,255,255,.5)" href="/about.html">Our story</a></div>
<div class="chipset"><span class="chip">No downloads</span><span class="chip">No purchases</span><span class="chip">Instant browser play</span></div></div>
<div class="heroart"><div class="g">{hero_imgs}</div></div>
</div></section>
<div class="container"><div class="stats">{stats}</div></div>
<section class="block"><div class="container"><div class="sec-head"><span class="eyebrow">Why Lumen Play</span><h2>A calmer way to play</h2><p>Everything about the lounge is built for easy, unhurried fun — no pressure, no cost, no catch.</p></div>
<div class="grid g4">{feats}</div></div></section>
<section class="block alt"><div class="container">{paras(C['home_lead'])}
<div class="sec-head" style="margin-top:20px"><span class="eyebrow">How it works</span><h2>Three steps to settle in</h2></div>
<div class="grid g3">{steps}</div></div></section>
<section class="block"><div class="container"><div class="sec-head"><span class="eyebrow">Find your mood</span><h2>Browse by category</h2><p>{e(C['home_sections'][0]['body'].split(chr(10))[0])}</p></div>
<div class="grid g3">{cats}</div></div></section>
<section class="block alt"><div class="container"><div class="sec-head"><span class="eyebrow">The shelves</span><h2>Featured games</h2><p>{e(C['games_intro'].split('.')[0])}.</p></div>
<div class="grid g3">{fg}</div><div style="text-align:center;margin-top:36px"><a class="btn" href="/games.html">See all games</a></div></div></section>
<section class="block"><div class="container"><div class="sec-head"><span class="eyebrow">From the community</span><h2>What our members say</h2></div>
<div class="grid g3">{tests}</div></div></section>
<section class="block alt"><div class="container"><div class="sec-head"><span class="eyebrow">Good to know</span><h2>Frequently asked</h2></div>
<div class="faq">{faqs}</div><div style="text-align:center;margin-top:26px"><a class="btn ghost" href="/faq.html">All questions</a></div></div></section>
<section class="block"><div class="container"><div class="ctaband"><h2>Pull up a comfy seat</h2><p>Join a friendly, adults-only lounge of free social games. No cost, no downloads — just press play.</p>
<a class="btn light" href="/games.html">Enter the lounge</a>
<form class="newsletter" style="margin-top:24px" onsubmit="return false"><input type="email" placeholder="Your email for new-game updates" aria-label="Email"><button class="btn light" type="submit">Keep me posted</button></form></div></div></section>
"""
    open(os.path.join(OUT,"index.html"),"w").write(shell(f"{BRAND} — Free Social Gaming Lounge", C["tagline"], "/index.html", body, "/index.html", f'<script type="application/ld+json">{org_ld}</script>', modal=True))

    # ---------- GAMES ----------
    filt = ['<button class="active" data-f="all">All games</button>'] + [f'<button data-f="{e(c)}">{e(c)}</button>' for c in sorted(set(CATEGORY.values()))]
    allg = "".join(gcard(s) for s in GAME_ORDER)
    gbody = f"""<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#e6dbff">The lounge</span><h1>Our Games</h1><p>{e(C['games_intro'])}</p></div></section>
<section class="block"><div class="container"><div class="filters">{''.join(filt)}</div><div class="grid g3">{allg}</div></div></section>"""
    open(os.path.join(OUT,"games.html"),"w").write(shell(f"Games — {BRAND}", C["games_intro_meta"], "/games.html", gbody, "/games.html", modal=True))

    # ---------- GAME DETAIL PAGES ----------
    for slug in GAME_ORDER:
        g = GAMES[slug]; gc = C["games"][slug]
        tags = "".join(f'<span class="tag">{e(t)}</span>' for t in GAME_TAGS[slug])
        feats = "".join(f"<li>{e(x)}</li>" for x in GAME_FEATURES)
        tips = "".join(f"<li>{e(x)}</li>" for x in GAME_TIPS[slug])
        related = "".join(gcard(s, with_tags=False, modal=False) for s in GAME_ORDER if s!=slug)
        ld = json.dumps({"@context":"https://schema.org","@type":"VideoGame","name":g["game_name"],
            "url":f"{BASE}/game-{slug}.html","genre":"Social casual game","gamePlatform":"Web browser",
            "applicationCategory":"Game","operatingSystem":"Web","publisher":{"@type":"Organization","name":BRAND},
            "offers":{"@type":"Offer","price":"0","priceCurrency":"USD"}})
        body = f"""<section class="block" style="padding-top:44px"><div class="container">
<div style="margin-bottom:18px"><a href="/games.html" style="font-family:Poppins;font-weight:600;font-size:.9rem">← Back to all games</a></div>
<div class="gamehead"><span class="cat" style="position:static;display:inline-block;width:max-content;background:var(--primary);margin-bottom:8px">{e(CATEGORY[slug])}</span>
<h1>{e(g['game_name'])}</h1><p style="color:var(--secondary);font-family:Poppins;font-weight:600;margin:0">{e(gc['tagline'])}</p>
<div class="tags" style="margin-top:10px">{tags}</div></div>
<div class="gwrap">
<div><iframe class="gameframe" src="{e(g['iframe_url'])}" title="Play {e(g['game_name'])} free" allowfullscreen loading="lazy"></iframe>
<div style="margin-top:24px">{paras(gc['description'])}<h2 style="font-family:Poppins;font-size:1.3rem;color:var(--primary);margin:1.2em 0 .4em">How it plays</h2>{paras(gc['how_to_play'])}</div></div>
<aside><div class="panel"><h3>Game features</h3><ul class="flist">{feats}</ul></div>
<div class="panel"><h3>Tips for a good session</h3><ul class="flist">{tips}</ul></div>
<div class="panel" style="background:#f0ecfb"><h3>Play well</h3><p style="color:var(--muted);font-size:.92rem;margin:0">This is free social gaming for adults 21+. Nothing of monetary value is at stake — just relax and have fun.</p></div></aside>
</div></div></section>
<section class="block alt"><div class="container"><div class="sec-head"><span class="eyebrow">Keep playing</span><h2>More games to try</h2></div><div class="grid g3">{related}</div></div></section>"""
        open(os.path.join(OUT,f"game-{slug}.html"),"w").write(shell(f"{g['game_name']} — Play Free at {BRAND}", gc["tagline"], f"/game-{slug}.html", body, "/games.html", f'<script type="application/ld+json">{ld}</script>'))

    # ---------- ABOUT ----------
    team = "".join(f"""<div class="feature"><div class="avatar" style="width:56px;height:56px;font-size:1.1rem;margin-bottom:14px">{e(initials(m['name']))}</div>
<h3>{e(m['name'])}</h3><div class="tl" style="color:var(--secondary);font-family:Poppins;font-weight:600;font-size:.85rem;margin-bottom:8px">{e(m['role'])}</div><p>{e(m['bio'])}</p></div>""" for m in C["about"]["team"])
    values = "".join(f'<div class="feature"><div class="ic">{icon(i)}</div><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i,t,d in
                     [("heart","Warmth first","We would rather be cosy than loud. Every choice we make starts with how it feels to sit down and play."),
                      ("sofa","Calm by design","No pressure, no noise, no chasing. The lounge is a place to slow down for a while."),
                      ("bolt","Free and open","No cost, no downloads, no strings — social gaming that anyone 21+ can simply enjoy.")])
    abody = f"""<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#e6dbff">Our story</span><h1>About {BRAND}</h1><p>{e(C['about']['meta'])}</p></div></section>
<section class="block"><div class="container prose">{paras(C['about']['story'])}</div></section>
<section class="block alt"><div class="container"><div class="sec-head"><span class="eyebrow">What we value</span><h2>The spirit of the lounge</h2></div><div class="grid g3">{values}</div></div></section>
<section class="block"><div class="container"><div class="sec-head"><span class="eyebrow">The friends behind it</span><h2>Meet the team</h2></div><div class="grid g3">{team}</div></div></section>"""
    open(os.path.join(OUT,"about.html"),"w").write(shell(f"About — {BRAND}", C["about"]["meta"], "/about.html", abody, "/about.html", f'<script type="application/ld+json">{org_ld}</script>'))

    # ---------- CONTACT ----------
    c = C["contact"]
    cbody = f"""<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#e6dbff">Say hello</span><h1>Contact {BRAND}</h1><p>{e(c['meta'])}</p></div></section>
<section class="block"><div class="container gwrap">
<div>{paras(c['intro'])}<form class="panel" onsubmit="return false" style="margin-top:8px">
<h3>Send us a message</h3>
<p style="margin:0 0 6px;font-family:Poppins;font-weight:600;font-size:.85rem;color:var(--muted)">Your name</p><input style="width:100%;border:1.5px solid var(--line);border-radius:10px;padding:11px 14px;margin-bottom:14px;font-family:Poppins" placeholder="Jane Doe">
<p style="margin:0 0 6px;font-family:Poppins;font-weight:600;font-size:.85rem;color:var(--muted)">Email</p><input style="width:100%;border:1.5px solid var(--line);border-radius:10px;padding:11px 14px;margin-bottom:14px;font-family:Poppins" placeholder="you@example.com">
<p style="margin:0 0 6px;font-family:Poppins;font-weight:600;font-size:.85rem;color:var(--muted)">Message</p><textarea style="width:100%;border:1.5px solid var(--line);border-radius:10px;padding:11px 14px;margin-bottom:16px;font-family:Poppins;min-height:120px" placeholder="How can we help?"></textarea>
<button class="btn" type="submit">Send message</button></form></div>
<aside><div class="panel"><h3>Reach us directly</h3><ul class="flist"><li>Email: {e(c['email'])}</li><li>Support hours: {e(c['hours'])}</li><li>Community: {e(c['community'])}</li></ul></div>
<div class="panel" style="background:#f0ecfb"><h3>Before you write</h3><p style="color:var(--muted);font-size:.92rem;margin:0">Many quick questions are answered on our <a href="/faq.html">FAQ page</a> — it is the fastest way to get help.</p></div></aside>
</div></section>"""
    open(os.path.join(OUT,"contact.html"),"w").write(shell(f"Contact — {BRAND}", c["meta"], "/contact.html", cbody, "/contact.html"))

    # ---------- FAQ ----------
    qas = "".join(f'<div class="qa"><button>{e(q)}<span class="pm">+</span></button><div class="ans"><p>{e(a)}</p></div></div>' for q,a in FAQ)
    fbody = f"""<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#e6dbff">Help centre</span><h1>Frequently asked questions</h1><p>Everything you might want to know about playing in the {BRAND} lounge.</p></div></section>
<section class="block"><div class="container"><div class="faq">{qas}</div>
<div class="callout" style="max-width:820px;margin:30px auto 0">Still stuck? Our small team is happy to help — head to the <a href="/contact.html">Contact page</a> and drop us a line.</div></div></section>"""
    open(os.path.join(OUT,"faq.html"),"w").write(shell(f"FAQ — {BRAND}", f"Answers to common questions about free social gaming at {BRAND}.", "/faq.html", fbody, "/faq.html"))

    # ---------- RESPONSIBLE PLAY ----------
    rp = "".join(f'<div class="panel"><h3>{e(t)}</h3><p style="color:var(--muted);margin:0">{e(d)}</p></div>' for t,d in RESPONSIBLE)
    rbody = f"""<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#e6dbff">Play well</span><h1>Responsible Play</h1><p>{BRAND} is built for light, feel-good entertainment. Here is how we help keep it that way.</p></div></section>
<section class="block"><div class="container prose"><div class="callout">Lumen Play is free social gaming for adults 21 and over. There is no cost to play and nothing of monetary value can be gained. Even so, healthy habits keep the fun feeling good.</div>{rp}</div></section>"""
    open(os.path.join(OUT,"responsible-play.html"),"w").write(shell(f"Responsible Play — {BRAND}", f"How {BRAND} supports healthy, balanced free social gaming for adults 21+.", "/responsible-play.html", rbody, "/responsible-play.html"))

    # ---------- PRIVACY & TERMS (multi-section + TOC) ----------
    def slugify(t): return t.lower().replace(" ","-").replace("&","and")
    def legal_page(title, sections, meta, canon):
        toc = "".join(f'<li><a href="#{slugify(t)}">{e(t)}</a></li>' for t,_ in sections)
        secs = "".join(f'<h2 id="{slugify(t)}">{e(t)}</h2>{paras(b)}' for t,b in sections)
        body = f"""<section class="page-hero"><div class="container"><span class="eyebrow" style="color:#e6dbff">Legal</span><h1>{e(title)}</h1><p>Last updated: 9 July 2026</p></div></section>
<section class="block"><div class="container prose"><div class="toc"><h3>On this page</h3><ul>{toc}</ul></div>{secs}
<div class="callout" style="margin-top:34px">{BRAND} is a free social gaming site for adults 21+. There are no purchases and nothing of monetary value is involved anywhere on this site.</div></div></section>"""
        open(os.path.join(OUT,canon.strip("/")),"w").write(shell(f"{title} — {BRAND}", meta, canon, body, canon))
    legal_page("Privacy Policy", PRIVACY_SECTIONS, f"How {BRAND} collects, uses and protects your information.", "/privacy.html")
    legal_page("Terms of Use", TERMS_SECTIONS, f"The terms that govern your use of the free social games at {BRAND}.", "/terms.html")

    # ---------- sitemap / robots ----------
    urls = ["/index.html","/games.html","/about.html","/contact.html","/faq.html","/responsible-play.html","/privacy.html","/terms.html"] + [f"/game-{s}.html" for s in GAME_ORDER]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{BASE}{u}</loc><changefreq>weekly</changefreq></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(OUT,"sitemap.xml"),"w").write(sm)
    open(os.path.join(OUT,"robots.txt"),"w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

    # ---------- images ----------
    imgdir = os.path.join(OUT,"assets","games-images"); os.makedirs(imgdir, exist_ok=True)
    for s in GAME_ORDER:
        src = os.path.join(ROOT,"assets/games-images",GAMES[s]["image"])
        if os.path.exists(src): shutil.copy2(src, os.path.join(imgdir, GAMES[s]["image"]))
    print("Rich Lumen Play built:", len([f for f in os.listdir(OUT) if f.endswith('.html')]), "HTML pages")

if __name__ == "__main__":
    build()
