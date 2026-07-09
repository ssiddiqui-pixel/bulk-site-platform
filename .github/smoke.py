#!/usr/bin/env python3
"""CI smoke test: exercises manifest assignment -> build_rich -> QA with STUB copy
(no Claude API). Proves the generator + QA gate work on every push. Exits non-zero on failure."""
import sys, os, shutil, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "dashboard"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import pipeline

def words(b, th, n, k0=0):
    s, i, wc = [], k0, 0
    while wc < n:
        s.append(f"{b} entry {i}: this welcoming free social {th} space invites adults to relax with gentle reel games and easygoing play today.")
        wc += 20; i += 1
    return " ".join(s)

def stub(site):
    b, th = site["brand"], site["theme"]; games, gm = {}, {}
    for g in site["games_resolved"]:
        nm = g["name"]
        games[g["slug"]] = {"tagline": f"{nm} — a free {th} reel game",
                            "description": words(b, th, 170) + f" {nm} is a lounge highlight.",
                            "how_to_play": words(b, th, 45)}
        gm[g["slug"]] = {"category": "Reels", "tags": ["Free", "Fun", "Reels"],
                         "tips": [f"{b} tip one for {nm} here.", f"{b} tip two for {nm} here.", f"{b} tip three for {nm} here."]}
    return {
        "tagline": f"{b} — free social {th} gaming for adults 21+", "hero_headline": f"Welcome to {b}",
        "hero_intro": words(b, th, 40), "home_lead": words(b, th, 60),
        "home_sections": [{"heading": f"About {b} part {i}", "body": words(b, th, 80, i*10)} for i in range(3)],
        "games_intro": words(b, th, 95), "games_intro_meta": f"Browse free {th} reel games at {b}.", "games": games,
        "about_story": words(b, th, 440), "about_meta": f"The story of {b}, a free social {th} lounge.",
        "team": [{"role": f"{th} lead {k}", "bio": words(b, th, 25, k)} for k in range(3)],
        "contact": {"meta": f"Contact {b}.", "intro": words(b, th, 60), "email": f"hello@{site['slug']}.example",
                    "hours": "Mon-Fri 9am-6pm", "community": f"Join the {b} community."},
        "privacy": words(b, th, 340, 7), "terms": words(b, th, 340, 11),
        "testimonials": [{"text": words(b, th, 30, k*3)} for k in range(3)],
        "topbar_parts": ["21+ only", "Free to play", "New games monthly"], "disclaimer": words(b, th, 90),
        "stats": [{"n": "40+", "l": "games"}, {"n": "21+", "l": "adults"}, {"n": "$0", "l": "cost"}, {"n": "100%", "l": "web"}],
        "features": [{"icon": "bolt", "title": f"Feature {k}", "desc": words(b, th, 22, k)} for k in range(4)],
        "values": [{"icon": "heart", "title": f"Value {k}", "desc": words(b, th, 22, k)} for k in range(3)],
        "howto": [{"title": f"Step {k}", "desc": words(b, th, 20, k)} for k in range(3)],
        "categories": [{"title": f"Category {k}", "desc": words(b, th, 20, k)} for k in range(3)],
        "faq": [{"q": f"Question {k} about {b}?", "a": words(b, th, 45, k)} for k in range(7)],
        "responsible": [{"title": f"Play well {k}", "body": words(b, th, 40, k)} for k in range(5)],
        "game_features": ["Instant browser play", "Free forever", "Feature rounds", "Any device"], "game_meta": gm,
        "privacy_sections": [{"h": h, "b": words(b, th, 55, i)} for i, h in enumerate(
            ["Information we collect", "Cookies and analytics", "How we use information", "Legal bases",
             "Sharing your information", "Data retention", "Your rights", "Adults only", "Security",
             "Changes to this policy", "Contact us"])],
        "terms_sections": [{"h": h, "b": words(b, th, 55, i)} for i, h in enumerate(
            ["Eligibility", "Nature of the service", "Acceptable use", "Intellectual property", "Third-party games",
             "Disclaimers", "Limitation of liability", "Changes to the service", "Termination", "Governing law", "Contact us"])],
        "micro": {"cta_h": f"Play at {b}", "cta_p": words(b, th, 25), "rp_hero": words(b, th, 20),
                  "rp_callout": words(b, th, 35), "playwell": words(b, th, 25), "contact_before": "Before you write",
                  "contact_aside": f"{b} keeps quick answers on our FAQ page for common questions today.",
                  "faq_still": f"{b} team waits on the Contact page to help you further right now.",
                  "legal_callout": words(b, th, 25)},
    }

def main():
    domains = ["ci-alpha-arcade.com", "ci-bravo-games.net"]
    man = pipeline.assign_manifest(domains); slugs = [s["slug"] for s in man["sites"]]
    for s in man["sites"]:
        data = stub(s); pipeline._require(data, s)
        pipeline.write_content_files(s, data); pipeline.build_site(s["slug"])
    code, out = pipeline.run_qa()
    print(out[out.find("=== QA RESULTS"):][:400])
    for s in slugs:
        shutil.rmtree(os.path.join(ROOT, "builds", s), ignore_errors=True)
    if code != 0:
        print("SMOKE TEST FAILED: QA reported issues"); sys.exit(1)
    print("SMOKE TEST PASSED")

if __name__ == "__main__":
    main()
