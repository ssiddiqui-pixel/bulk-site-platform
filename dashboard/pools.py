"""Differentiator pools for auto-assigning a batch manifest.
The dashboard rotates through these (checked against state/registry.json) so every
site in a batch differs in palette, fonts, layout, voice, story, games and testimonials."""

# 12 palettes — each with a distinct primary hue (primary, secondary, accent, background)
PALETTES = [
    {"primary":"#6C4AB6","secondary":"#8D72E1","accent":"#B9E0FF","background":"#F5F3FF"},  # violet
    {"primary":"#E2571E","secondary":"#F2A007","accent":"#2B2D42","background":"#FFF6EC"},  # ember
    {"primary":"#0E7C86","secondary":"#16C2A3","accent":"#FFD166","background":"#ECFBF9"},  # teal
    {"primary":"#C0392B","secondary":"#E67E22","accent":"#2C3E50","background":"#FDF3F0"},  # crimson
    {"primary":"#2E86DE","secondary":"#54A0FF","accent":"#FECA57","background":"#EEF6FF"},  # sky blue
    {"primary":"#27AE60","secondary":"#2ECC71","accent":"#F1C40F","background":"#EEFBF2"},  # green
    {"primary":"#8E44AD","secondary":"#B06AD6","accent":"#F5B7D0","background":"#F8F0FC"},  # purple-pink
    {"primary":"#D81B60","secondary":"#F06292","accent":"#26C6DA","background":"#FFF0F5"},  # magenta
    {"primary":"#16A085","secondary":"#1ABC9C","accent":"#F39C12","background":"#ECFAF6"},  # jade
    {"primary":"#34495E","secondary":"#5D6D7E","accent":"#E74C3C","background":"#F2F4F6"},  # slate
    {"primary":"#B7791F","secondary":"#D69E2E","accent":"#2D3748","background":"#FFFBF0"},  # gold
    {"primary":"#5B21B6","secondary":"#7C3AED","accent":"#22D3EE","background":"#F5F3FF"},  # indigo
]

# font pairings must match keys in scripts/build_rich.py FONTS
FONT_PAIRS = [
    "Montserrat + Merriweather", "Nunito + Bitter", "Poppins + Lora",
    "Work Sans + Source Serif 4", "Rubik + Zilla Slab", "Space Grotesk + Inter",
    "Oswald + Lora", "Fraunces + Inter",
]

# layouts implemented in build_rich.py (css + index_page)
LAYOUTS = ["cards-grid-first", "single-scroll-anchor", "centered-minimal", "hero-split"]

# 10 voices / 10 story angles (from CLAUDE.md) — unique per site in a 10-batch
VOICES = ["arcade-retro","cozy-lounge","esports-energy","minimalist-zen","playful-cartoon",
          "premium-noir","tropical-breeze","sci-fi-neon","rustic-boardgame","urban-street"]
STORIES = ["founded-by-friends","remote-team-worldwide","indie-studio-passion","community-first-origin",
           "design-led-studio","accessibility-mission","nostalgia-revival","campus-project-grown",
           "family-hobby-turned-studio","weekend-jam-origin"]

# testimonial pool (CLAUDE.md): first names x last initials
TESTI_FIRST = ["Ayla","Remi","Kian","Suki","Noor","Teo","Mira","Joss","Leif","Zara"]
TESTI_INIT  = ["B","D","F","H","K","M","P","R","T","W"]

# invented team names (first names NOT in the testimonial pool)
TEAM_FIRST = ["Harriet","Desmond","Priya","Marco","Lena","Ravi","Nina","Tobias","Amara","Elias",
              "Sofia","Malik","Freya","Diego","Hana","Omar","Ingrid","Cyrus","Talia","Bram",
              "Yuki","Rafael","Esme","Kofi","Lucia"]
TEAM_LAST = ["Vale","Okafor","Nair","Ferreira","Sundqvist","Chandra","Alvarez","Berg","Diallo","Rossi",
             "Bianchi","Haddad","Larsen","Moreno","Tanaka","Ali","Novak","Reyes","Kaur","Fischer"]

THEME_ADJ = ["Aurora","Ember","Tidal","Midnight","Golden","Neon","Velvet","Crimson","Frost","Lush",
             "Solar","Copper","Cobalt","Jade","Dusk","Coral","Onyx","Ivory","Cinder","Mirage"]
THEME_NOUN = ["Lounge","Summit","Bay","Arcade","Harbour","Grove","Deck","Parlour","Atrium","Terrace",
              "Hollow","Quarter","Gallery","Court","Haven","Loft","Meadow","Nook","Studio","Reef"]
