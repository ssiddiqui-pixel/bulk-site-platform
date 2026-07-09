#!/usr/bin/env python3
"""Cross-site QA gate. Enforces every rule from CLAUDE.md / .claude/commands/qa.md.
Exit 0 = clean. Prints a pass/fail table and detailed failures."""
import os, re, json, glob, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILDS = os.path.join(ROOT, "builds")

BANNED = ["casino","gambling","betting","bet","wager","real money","deposit","withdrawal",
          "odds","slots","payout","bonus","bonuses","rewards","jackpot","jackpots",
          "win","wins","winnings"]
REQUIRED = ["index.html","games.html","about.html","contact.html","privacy.html","terms.html",
            "sitemap.xml","robots.txt"]

class Stripper(HTMLParser):
    def __init__(self): super().__init__(); self.txt=[]; self.skip=0
    def handle_starttag(self,t,a):
        if t in ("script","style"): self.skip+=1
    def handle_endtag(self,t):
        if t in ("script","style") and self.skip: self.skip-=1
    def handle_data(self,d):
        if not self.skip: self.txt.append(d)
def visible_text(h):
    s=Stripper(); s.feed(h); return re.sub(r"\s+"," "," ".join(s.txt)).strip()
def wordcount(h): return len(visible_text(h).split())

def sentences(text):
    return [s.strip() for s in re.split(r"[.!?]+", text) if len(s.split())>=8]

def main_content(h):
    """Text inside <main> only — excludes shared chrome (nav/header/footer/age-gate)."""
    m = re.search(r"<main>(.*?)</main>", h, re.S|re.I)
    return visible_text(m.group(1)) if m else visible_text(h)

def language_text(h):
    """Everything a human reads or a crawler indexes as language: visible text + SEO
    metadata + alt/title/aria — but NOT functional attribute URLs (href/src), which
    may legitimately contain a third-party endpoint path we cannot alter."""
    parts = [visible_text(h)]
    for pat in [r'<title>(.*?)</title>',
                r'name="description"\s+content="([^"]*)"',
                r'property="og:[a-z]+"\s+content="([^"]*)"',
                r'\balt="([^"]*)"', r'\btitle="([^"]*)"', r'aria-label="([^"]*)"']:
        parts += re.findall(pat, h, re.S|re.I)
    return " ".join(parts).lower()

def qa():
    manifest=json.load(open(os.path.join(ROOT,"state/batch-manifest.json")))
    msites={s["slug"]:s for s in manifest["sites"]}
    # scope QA to the sites in the CURRENT batch manifest (builds/ may hold other batches)
    sites = sorted([d for d in glob.glob(os.path.join(BUILDS,"*"))
                    if os.path.isdir(d) and os.path.basename(d) in msites])
    fails=[]; rows=[]
    all_sentences={}   # sentence -> set(site)
    testi_combos={}    # combo -> set(site)

    # cross-site: shared primary hex
    prim={}
    for s in manifest["sites"]:
        prim.setdefault(s["palette"]["primary"].lower(), []).append(s["slug"])
    for hexv,slugs in prim.items():
        if len(slugs)>1: fails.append(f"[CROSS] shared primary hex {hexv}: {slugs}")

    for d in sites:
        slug=os.path.basename(d); f=[]
        htmls=glob.glob(os.path.join(d,"*.html"))
        names={os.path.basename(x) for x in htmls}
        # required files
        for r in REQUIRED:
            if not os.path.exists(os.path.join(d,r)): f.append(f"missing {r}")
        # game pages count == 6
        gamepages=[x for x in htmls if os.path.basename(x).startswith("game-")]
        if len(gamepages)!=6: f.append(f"expected 6 game pages, found {len(gamepages)}")

        for x in htmls:
            base=os.path.basename(x); h=open(x,encoding="utf-8").read()
            low=h.lower()
            # banned words — scan human-readable language (visible text + SEO metadata +
            # alt/title/aria), NOT functional third-party URLs in href/src attributes.
            lang=language_text(h)
            for b in BANNED:
                if re.search(r"\b"+re.escape(b)+r"\b", lang):
                    f.append(f"BANNED '{b}' in {base}")
            # age gate
            if "18+" in h: f.append(f"'18+' present in {base}")
            if "21+" not in h: f.append(f"'21+' missing in {base}")
            # SEO
            for tag,pat in [("title","<title>"),("meta description",'name="description"'),
                            ("canonical",'rel="canonical"'),("og:title",'property="og:title"')]:
                if pat not in h: f.append(f"{tag} missing in {base}")
            # per-game iframe count
            if base.startswith("game-"):
                n=len(re.findall(r"<iframe", low))
                if n!=1: f.append(f"{base} has {n} iframes (need exactly 1)")
                if 'target="_blank"' in low and "playngo" in low:
                    f.append(f"{base} external game link")
                wc=wordcount(h)
                if wc<150: f.append(f"{base} only {wc} words (<150)")
            # word counts main/legal
            if base=="about.html" and wordcount(h)<400: f.append(f"about {wordcount(h)}w (<400)")
            if base in ("privacy.html","terms.html") and wordcount(h)<300: f.append(f"{base} {wordcount(h)}w (<300)")
            if base in ("index.html","games.html") and wordcount(h)<300: f.append(f"{base} {wordcount(h)}w (<300)")
            # legal staging urls
            if base in ("privacy.html","terms.html") and re.search(r"cloudways|staging",low):
                f.append(f"{base} contains staging/cloudways url")
            # collect sentences for cross-site dup — MAIN CONTENT only, excluding
            # shared nav/footer/age-gate chrome (duplicate-content is about body copy).
            for sent in sentences(main_content(h)):
                key=re.sub(r"\s+"," ",sent.lower())
                all_sentences.setdefault(key,set()).add(slug)

        # testimonial combos from manifest
        for t in msites[slug]["testimonials"]:
            testi_combos.setdefault(t.lower().strip(), set()).add(slug)

        rows.append((slug, "FAIL" if f else "PASS", len(f)))
        fails += [f"[{slug}] "+x for x in f]

    # cross-site duplicate sentences
    for sent,slugs in all_sentences.items():
        if len(slugs)>1:
            fails.append(f"[CROSS] 8+word sentence shared by {sorted(slugs)}: \"{sent[:70]}...\"")
    # repeated testimonial combos across sites
    for combo,slugs in testi_combos.items():
        if len(slugs)>1:
            fails.append(f"[CROSS] testimonial '{combo}' repeated in {sorted(slugs)}")

    print("\n=== QA RESULTS ===")
    for slug,st,n in rows: print(f"  {slug:22} {st}  ({n} issues)")
    print(f"\nTOTAL FAILURES: {len(fails)}")
    for x in fails: print("  -",x)
    return 0 if not fails else 1

if __name__=="__main__":
    sys.exit(qa())
