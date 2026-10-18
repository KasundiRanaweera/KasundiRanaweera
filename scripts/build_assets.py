"""Generate the hand-made animated SVG assets for the profile README.

usage: python build_assets.py <assets dir> [--galaxy-only]
needs: internet access (tech logos are fetched and embedded at build time); GITHUB_TOKEN recommended

The tech galaxy also picks up new languages and repo topics automatically (see detect_new_tech).

Project cards for new repositories are generated separately by update_projects.py.
"""
import base64, math, os, re, sys, urllib.request
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from theme import *  # noqa: E402,F403

OUT = sys.argv[1]


def out(name, content):
    write(os.path.join(OUT, name), content)


PETAL = "M0,-10 C7,-10 10,-2 0,10 C-10,-2 -7,-10 0,-10Z"
SPARK = "M0,-9 L2,-2 L9,0 L2,2 L0,9 L-2,2 L-9,0 L-2,-2Z"


def petals(n, w, h, seed=7, x_min=380):
    import random
    rnd = random.Random(seed)
    shapes, css = [], []
    colors = [SKY, AZURE, INDIGO, CYAN, ICE]
    for i in range(n):
        x = rnd.randint(x_min, w - 20)
        dur = rnd.uniform(11, 19)
        delay = -rnd.uniform(0, dur)
        drift = rnd.randint(-90, 60)
        spin = rnd.choice([1, -1]) * rnd.randint(200, 420)
        scale = rnd.uniform(0.55, 1.15)
        op = rnd.uniform(0.3, 0.75)
        shape = PETAL if i % 3 else SPARK
        css.append(f".pt{i}{{animation:fall{i} {dur:.1f}s linear {delay:.1f}s infinite}}"
                   f"@keyframes fall{i}{{from{{transform:translate(0,-30px) rotate(0deg) scale({scale:.2f})}}"
                   f"to{{transform:translate({drift}px,{h + 40}px) rotate({spin}deg) scale({scale:.2f})}}}}")
        shapes.append(f'<g transform="translate({x},0)"><g class="pt{i} petal">'
                      f'<path d="{shape}" fill="{rnd.choice(colors)}" opacity="{op:.2f}"/></g></g>')
    return "\n".join(shapes), "".join(css)


# =====================================================================================
# HERO — greeting, name, roles, intro and an "at a glance" panel
# =====================================================================================
TAGLINE = [("🎓", "Computer Science Undergraduate", CYAN),
           ("💻", "Full-Stack Developer", AZURE),
           ("🤖", "AI/ML & Data Science Enthusiast", INDIGO)]
# intro paragraph: list of lines, each a list of (text, bold)
INTRO = [
    [("I'm a ", False), ("BSc (Hons) Computer Science", True), (" undergraduate at ", False), ("NSBM Green University", True), (",", False)],
    [("affiliated with the ", False), ("University of Plymouth", True), (". I'm passionate about building meaningful", False)],
    [("digital experiences and turning ideas into reality through technology.", False)],
]
CLOSING = ("✨", "Building, learning, and innovating")

# line icons drawn on a 24×24 grid (Lucide-style strokes)
ICONS = {
    "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/><line x1="14" y1="4" x2="10" y2="20"/>',
    "wrench": '<path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94z"/>',
    "flask": '<path d="M9 3h6"/><path d="M10 3v6.5L4.6 18.8A1.5 1.5 0 0 0 5.9 21h12.2a1.5 1.5 0 0 0 1.3-2.2L14 9.5V3"/><path d="M7.5 15h9"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
}
# (icon, label, accent, chips or sentence)
GLANCE = [
    ("code", "Interests", CYAN, ["Full-Stack Development", "Data Analytics", "Machine Learning", "AI & LLMs"]),
    ("wrench", "Learning", SKY, ["System Design", "Software Architecture", "Automated Testing", "CI/CD"]),
    ("flask", "Research Interests", AZURE, ["NLP", "AI for Low-Resource Languages"]),
    ("target", "Goal", BLUE, "Building impactful software solutions and continuously growing as a developer."),
    ("briefcase", "Open to", INDIGO, ["Software Engineering", "Data Analytics", "Machine Learning Internships"]),
]


def hero():
    W = 1200
    ST = base64.b64encode(open(os.path.join(OUT, "avatar-sticker.png"), "rb").read()).decode()
    sx, sy, sh = 54, 24, 286                  # die-cut sticker of the 3D avatar, on the left
    sw = round(333 * sh / 440)
    scx, scy = sx + sw / 2, sy + sh / 2
    tx = 318                                  # text column beside the sticker
    pill_y = 254
    px, pw = 40, 1120                         # node grid
    hgap, vgap, card_h = 60, 22, 64           # gaps hold the connector lines
    cw = (pw - hgap) // 2
    panel_top = 316
    strip_top = panel_top + card_h * 2 + vgap + 16
    H = strip_top + 30 + 28 + 22
    SOFT, NODE = "#c7dbff", "#0b1d5c"

    # ---- role pills, in the text column right under the paragraph ----
    fs, gap = 13.5, 10
    widths = [tw(t, fs) * 1.08 + fs + 38 for _, t, _ in TAGLINE]
    x = tx
    pills = []
    for i, ((emo, t, c), w) in enumerate(zip(TAGLINE, widths)):
        pills.append(
            f'<g class="pop" style="animation-delay:{1.15 + i * .12:.2f}s">'
            f'<rect class="glowpill" style="animation-delay:{i * 1.3:.1f}s" x="{x:.0f}" y="{pill_y}" width="{w:.0f}" height="34" rx="17" '
            f'fill="{NODE}" fill-opacity=".85" stroke="{c}" stroke-opacity=".7" stroke-width="1.3"/>'
            f'<text x="{x + 16:.0f}" y="{pill_y + 22}" font-family="{SANS}" font-size="{fs}" fill="{TEXT}">'
            f'<tspan>{emo}</tspan><tspan dx="7" font-weight="600">{escape(t)}</tspan></text></g>')
        x += w + gap

    # ---- intro paragraph, each line wipes in like it's being typed ----
    bold = ' font-weight="700" fill="#ffffff"'
    intro = []
    for i, line in enumerate(INTRO):
        spans = "".join(f'<tspan{bold if b else ""}>{escape(t)}</tspan>' for t, b in line)
        intro.append(f'<text class="type" style="animation-delay:{0.9 + i * .45:.2f}s" x="{tx}" y="{192 + i * 26}" '
                     f'font-family="{SANS}" font-size="17" fill="{SOFT}">{spans}</text>')

    # ---- the four points as nodes joined by animated lines (like the reference's diagram) ----
    spots = {"Interests": (0, 0), "Learning": (1, 0), "Research Interests": (0, 1), "Open to": (1, 1)}
    rows, links = [], []
    for i, (icon, label, c, value) in enumerate(GLANCE):
        if label == "Goal":                              # written as a normal sentence, in a slim strip
            gw = tw(f"🎯 Goal: {value}", 16) * .96 + 56
            rows.append(f'<g class="rise" style="animation-delay:{1.7 + i * .12:.2f}s">'
                        f'<rect x="{600 - gw / 2:.0f}" y="{strip_top}" width="{gw:.0f}" height="30" rx="15" fill="{NODE}" fill-opacity=".8" '
                        f'stroke="{CYAN}" stroke-opacity=".55" stroke-width="1.3"/>'
                        f'<text x="600" y="{strip_top + 20.5}" font-family="{SANS}" font-size="16" font-weight="700" fill="{TEXT}" text-anchor="middle">'
                        f'<tspan>🎯</tspan> Goal: {escape(value)}</text></g>')
            continue
        col, rw = spots[label]
        x0 = px + col * (cw + hgap)
        y0 = panel_top + rw * (card_h + vgap)
        d = 1.5 + i * .12
        parts = [f'<g class="slide" style="animation-delay:{d:.2f}s">',
                 f'<rect class="node" style="animation-delay:{i * .9:.1f}s" x="{x0}" y="{y0}" width="{cw}" height="{card_h}" rx="16" '
                 f'fill="{NODE}" fill-opacity=".88" stroke="{c}" stroke-opacity=".75" stroke-width="1.5"/>',
                 f'<g class="icon" style="animation-delay:{d + .15:.2f}s">'
                 f'<rect x="{x0 + 16}" y="{y0 + 9}" width="24" height="24" rx="8" fill="{c}" fill-opacity=".16" stroke="{c}" stroke-opacity=".5"/>'
                 f'<g transform="translate({x0 + 22},{y0 + 15}) scale(.5)" fill="none" stroke="{c}" stroke-width="2.4" '
                 f'stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g></g>',
                 f'<text x="{x0 + 50}" y="{y0 + 25.5}" font-family="{MONO}" font-size="11.5" font-weight="700" fill="{c}" '
                 f'letter-spacing="1.3">{escape(label.upper())}</text>']
        vx = x0 + 16
        for k, chip in enumerate(value):
            cwid = tw(chip, 12.5) * 1.08 + 16
            parts.append(f'<g class="pop" style="animation-delay:{d + .2 + k * .07:.2f}s">'
                         f'<rect x="{vx:.0f}" y="{y0 + 38}" width="{cwid:.0f}" height="22" rx="11" fill="{c}" fill-opacity=".12" stroke="{c}" stroke-opacity=".4"/>'
                         f'<text x="{vx + cwid / 2:.0f}" y="{y0 + 53.5}" font-family="{SANS}" font-size="12.5" fill="{TEXT}" text-anchor="middle">{escape(chip)}</text></g>')
            vx += cwid + 6
        parts.append("</g>")
        rows.append("".join(parts))

    # connectors: left <-> right on both rows, top <-> bottom on both columns
    for rw in (0, 1):
        y = panel_top + rw * (card_h + vgap) + card_h / 2
        links.append(f'<line x1="{px + cw}" y1="{y}" x2="{px + cw + hgap}" y2="{y}"/>')
    for col in (0, 1):
        x = px + col * (cw + hgap) + cw / 2
        links.append(f'<line x1="{x}" y1="{panel_top + card_h}" x2="{x}" y2="{panel_top + card_h + vgap}"/>')

    style = f"""
@keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
.rise {{ animation: fadeUp .8s {EASE} both; }}
.pop {{ transform-box: fill-box; transform-origin: center; animation: pop .6s {EASE} both; }}
@keyframes pop {{ from {{ opacity: 0; transform: scale(.85); }} to {{ opacity: 1; transform: none; }} }}
.slide {{ animation: slide .7s {EASE} both; }}
@keyframes slide {{ from {{ opacity: 0; transform: translateX(-24px); }} to {{ opacity: 1; transform: none; }} }}
.icon {{ transform-box: fill-box; transform-origin: center; animation: spinIn .8s {EASE} both; }}
@keyframes spinIn {{ from {{ opacity: 0; transform: rotate(-90deg) scale(.5); }} to {{ opacity: 1; transform: none; }} }}
.type {{ animation: type 1.1s steps(40, end) both; }}
@keyframes type {{ from {{ clip-path: inset(0 100% 0 0); }} to {{ clip-path: inset(0 0 0 0); }} }}
.reveal {{ animation: reveal 1.1s {EASE} .25s both; }}
@keyframes reveal {{ from {{ clip-path: inset(0 100% 0 0); opacity: .3; }} to {{ clip-path: inset(0 0 0 0); opacity: 1; }} }}

.aur {{ transform-box: fill-box; transform-origin: center; }}
.a1 {{ animation: drift1 16s ease-in-out infinite alternate; }}
.a2 {{ animation: drift2 19s ease-in-out infinite alternate; }}
.a3 {{ animation: drift1 23s ease-in-out infinite alternate-reverse; }}
@keyframes drift1 {{ to {{ transform: translate(-80px, 50px) scale(1.15); }} }}
@keyframes drift2 {{ to {{ transform: translate(90px, -40px) scale(.9); }} }}
.gridglow {{ animation: gridglow 6s ease-in-out infinite alternate; }}
@keyframes gridglow {{ from {{ opacity: .45; }} to {{ opacity: 1; }} }}

.flow {{ stroke-dasharray: 18 26; animation: flow 1.5s linear 2s infinite; }}
@keyframes flow {{ to {{ stroke-dashoffset: -44; }} }}
.node {{ animation: node 5s ease-in-out 2.5s infinite; }}
@keyframes node {{ 0%, 80%, 100% {{ stroke-opacity: .75; }} 90% {{ stroke-opacity: 1; }} }}

.stick {{ transform-box: view-box; transform-origin: {scx}px {scy}px; animation: slap .9s cubic-bezier(.34, 1.56, .64, 1) .15s both; }}
@keyframes slap {{ from {{ opacity: 0; transform: scale(1.25) rotate(-16deg); }} to {{ opacity: 1; transform: rotate(-3deg); }} }}
.bob {{ transform-box: view-box; transform-origin: {scx}px {sy + sh}px; animation: bob 6s ease-in-out 1.2s infinite; }}
@keyframes bob {{ 0%, 100% {{ transform: translateY(0) rotate(0deg); }} 50% {{ transform: translateY(-7px) rotate(1.4deg); }} }}
.twk {{ transform-box: fill-box; transform-origin: center; animation: twk 2.8s ease-in-out infinite; }}
@keyframes twk {{ 0%, 100% {{ opacity: .25; transform: scale(.6) rotate(0deg); }} 50% {{ opacity: 1; transform: scale(1) rotate(45deg); }} }}

.wave {{ transform-box: fill-box; transform-origin: 70% 80%; animation: wave 2.6s ease-in-out 1s infinite; }}
@keyframes wave {{ 0%, 60%, 100% {{ transform: rotate(0); }} 10%, 30% {{ transform: rotate(16deg); }} 20%, 40% {{ transform: rotate(-8deg); }} }}
.shine {{ animation: shine 6s ease-in-out 1.6s infinite; }}
@keyframes shine {{ 0% {{ transform: translateX(-220px); }} 45%, 100% {{ transform: translateX(900px); }} }}
.bar {{ transform-box: fill-box; transform-origin: left center; animation: grow 1s {EASE} .7s both; }}
@keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: none; }} }}
.glowpill {{ animation: glow 4s ease-in-out 2s infinite; }}
@keyframes glow {{ 0%, 70%, 100% {{ stroke-opacity: .7; }} 85% {{ stroke-opacity: 1; }} }}
.sparkle {{ transform-box: fill-box; transform-origin: center; animation: sparkle 2.4s ease-in-out infinite; }}
@keyframes sparkle {{ 0%, 100% {{ transform: scale(1) rotate(0); }} 50% {{ transform: scale(1.25) rotate(20deg); }} }}

@media (prefers-reduced-motion: reduce) {{ .stick {{ transform: rotate(-3deg); }} }}"""

    name = f'x="{tx - 2}" y="132" font-family="{SANS}" font-size="74" font-weight="800" letter-spacing="-2"'
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{stops(["#050914", "#0d1a3d", "#0a1230"])}</linearGradient>
  <radialGradient id="gA"><stop offset="0" stop-color="{AZURE}" stop-opacity=".5"/><stop offset="1" stop-color="{AZURE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gC"><stop offset="0" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gI"><stop offset="0" stop-color="#6366f1" stop-opacity=".5"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset=".7" stop-color="#e3eeff"/><stop offset="1" stop-color="#b9d6ff"/></linearGradient>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="12" stdDeviation="10" flood-color="#020617" flood-opacity=".55"/></filter>
  <linearGradient id="shineG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".7"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="lineL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7dd3fc" stop-opacity="0"/><stop offset="1" stop-color="#7dd3fc" stop-opacity=".85"/></linearGradient>
  <linearGradient id="lineR" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7dd3fc" stop-opacity=".85"/><stop offset="1" stop-color="#7dd3fc" stop-opacity="0"/></linearGradient>
  <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#8ec5ff" stroke-opacity=".06" stroke-width="1"/></pattern>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <mask id="nameMask"><text {name} fill="#fff">Kasundi Ranaweera</text></mask>
</defs>

<!-- background: blue gradient, faint grid, soft glows -->
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#grid)"/>
  <circle class="aur a1" cx="1040" cy="40" r="330" fill="url(#gA)"/>
  <circle class="aur a2" cx="160" cy="{H * .55:.0f}" r="300" fill="url(#gC)"/>
  <circle class="aur a3" cx="720" cy="{H - 30}" r="300" fill="url(#gI)"/>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="27.5" fill="none" stroke="{SKY}" stroke-opacity=".12"/>

<!-- name + intro, left aligned -->
<g class="rise" style="animation-delay:.2s">
  <text x="{tx}" y="64" font-family="{SANS}" font-size="26" font-weight="600" fill="#8ec9ff"><tspan class="wave">👋</tspan> Hi, I'm</text>
</g>
<g class="reveal">
  <text {name} fill="url(#name)">Kasundi Ranaweera</text>
  <g mask="url(#nameMask)" opacity=".5"><rect class="shine" x="{tx - 40}" y="60" width="150" height="90" fill="url(#shineG)" transform="translate(-220,0)"/></g>
</g>
<rect class="bar" x="{tx}" y="152" width="84" height="4" rx="2" fill="#22d3ee"/>
{''.join(intro)}
{''.join(pills)}

<!-- the 3D avatar as a die-cut sticker -->
<g class="stick"><g class="bob">
  <image href="data:image/png;base64,{ST}" x="{sx}" y="{sy}" width="{sw}" height="{sh}" filter="url(#shadow)"/>
</g></g>
<path class="twk" d="M0,-9 L2,-2 L9,0 L2,2 L0,9 L-2,2 L-9,0 L-2,-2Z" fill="#7dd3fc" transform="translate({sx + sw + 6},{sy + 30})"/>
<path class="twk" style="animation-delay:1.3s" d="M0,-9 L2,-2 L9,0 L2,2 L0,9 L-2,2 L-9,0 L-2,-2Z" fill="#c4b5fd" transform="translate({sx - 14},{sy + 120}) scale(.7)"/>

<!-- the four points: nodes joined by lines with moving dashes -->
<g stroke="#2f63d6" stroke-width="2" stroke-linecap="round" opacity=".9">{''.join(links)}</g>
<g class="flow" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round">{''.join(links)}</g>
{''.join(rows)}

<g class="rise" style="animation-delay:2.4s">
  <rect x="272" y="{strip_top + 30 + 20}" width="170" height="2" rx="1" fill="url(#lineL)"/>
  <rect x="758" y="{strip_top + 30 + 20}" width="170" height="2" rx="1" fill="url(#lineR)"/>
  <text x="600" y="{strip_top + 30 + 25}" font-family="{SANS}" font-size="16" font-weight="700" fill="{TEXT}" text-anchor="middle"><tspan class="sparkle">{CLOSING[0]}</tspan> {escape(CLOSING[1])}</text>
</g>
"""
    title = ("Hi, I'm Kasundi Ranaweera — Computer Science Undergraduate, Full-Stack Developer, AI/ML & Data Science Enthusiast. "
             + " ".join("".join(t for t, _ in line) for line in INTRO) + " "
             + " ".join(f"{label}: {v if isinstance(v, str) else ', '.join(v)}." for _, label, _, v in GLANCE)
             + f" {CLOSING[1]}.")
    out("hero.svg", svg(W, H, style, body, title))


# =====================================================================================
# TECH GALAXY — three orbits of real logos, with a legend
# =====================================================================================
def fetch(url):
    from gh import open_url
    return open_url(urllib.request.Request(url, headers={"User-Agent": "profile-build"}))


def skillicon(i):
    return fetch(f"https://skillicons.dev/icons?i={i}")


def simpleicon(slug, color):
    paths = "".join(re.findall(r'<path d="[^"]+"/>', fetch(f"https://cdn.jsdelivr.net/npm/simple-icons@13.21.0/icons/{slug}.svg")))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" rx="60" fill="#242938"/>'
            f'<g transform="translate(52,52) scale(6.33)" fill="{color}">{paths}</g></svg>')


def monogram(letters, color):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256"><rect width="256" height="256" rx="60" fill="#242938"/>'
            f'<text x="128" y="160" font-family="Segoe UI, Arial, sans-serif" font-size="100" font-weight="800" fill="{color}" text-anchor="middle">{letters}</text></svg>')


ORBITS = [  # (label, ring colour, radius, seconds per turn, [(name, icon source)])
    ("Languages", CYAN, 104, 50, [
        ("Java", "java"), ("Python", "py"), ("TypeScript", "ts"), ("JavaScript", "js"),
        ("Dart", "dart"), ("C#", "cs"), ("C++", "cpp")]),
    ("Frameworks", AZURE, 182, 75, [
        ("React", "react"), ("Vite", "vite"), ("Tailwind", "tailwind"), ("Flutter", "flutter"),
        ("Spring Boot", "spring"), ("Node.js", "nodejs"), ("Express", "express"), (".NET", "dotnet"),
        ("HTML", "html"), ("CSS", "css")]),
    ("Data, AI & Tools", INDIGO, 260, 110, [
        ("PostgreSQL", "postgres"), ("Prisma", "prisma"), ("SQLite", "sqlite"), ("Firebase", "firebase"),
        ("Supabase", "supabase"), ("scikit-learn", "sklearn"), ("pandas", ("si", "pandas", "#ffffff")),
        ("Jupyter", ("si", "jupyter", "#F37626")), ("Ollama", ("si", "ollama", "#ffffff")),
        ("Groq", ("mono", "Gq", "#F55036")), ("Gradio", ("mono", "Gr", "#F97316")), ("Git", "git"),
        ("GitHub Actions", "githubactions"), ("Docker", "docker"), ("Vercel", "vercel"), ("Postman", "postman"),
        ("Jest", "jest"), ("Cypress", "cypress")]),
]


# ---------- auto-detection: new languages / topics in your repos join the galaxy ----------
LANG_ICONS = {"Python": "py", "Java": "java", "TypeScript": "ts", "JavaScript": "js", "Dart": "dart", "C#": "cs",
              "C++": "cpp", "C": "c", "Go": "go", "Rust": "rust", "Kotlin": "kotlin", "Swift": "swift", "PHP": "php",
              "Ruby": "ruby", "R": "r", "Scala": "scala", "Lua": "lua", "Haskell": "haskell", "Elixir": "elixir",
              "Solidity": "solidity", "Shell": "bash", "PowerShell": "powershell", "Vue": "vue", "Svelte": "svelte"}
# topic -> (display name, skillicons id, orbit index)
TOPIC_ICONS = {
    "nextjs": ("Next.js", "nextjs", 1), "vue": ("Vue", "vue", 1), "vuejs": ("Vue", "vue", 1), "angular": ("Angular", "angular", 1),
    "svelte": ("Svelte", "svelte", 1), "nuxt": ("Nuxt", "nuxtjs", 1), "django": ("Django", "django", 1),
    "flask": ("Flask", "flask", 1), "fastapi": ("FastAPI", "fastapi", 1), "nestjs": ("NestJS", "nestjs", 1),
    "laravel": ("Laravel", "laravel", 1), "bootstrap": ("Bootstrap", "bootstrap", 1), "electron": ("Electron", "electron", 1),
    "tauri": ("Tauri", "tauri", 1), "threejs": ("Three.js", "threejs", 1), "redux": ("Redux", "redux", 1),
    "jquery": ("jQuery", "jquery", 1), "react": ("React", "react", 1), "flutter": ("Flutter", "flutter", 1),
    "spring-boot": ("Spring Boot", "spring", 1), "nodejs": ("Node.js", "nodejs", 1), "express": ("Express", "express", 1),
    "tailwindcss": ("Tailwind", "tailwind", 1), "dotnet": (".NET", "dotnet", 1), "vite": ("Vite", "vite", 1),
    "mongodb": ("MongoDB", "mongodb", 2), "mysql": ("MySQL", "mysql", 2), "postgresql": ("PostgreSQL", "postgres", 2),
    "redis": ("Redis", "redis", 2), "sqlite": ("SQLite", "sqlite", 2), "firebase": ("Firebase", "firebase", 2),
    "supabase": ("Supabase", "supabase", 2), "prisma": ("Prisma", "prisma", 2), "graphql": ("GraphQL", "graphql", 2),
    "tensorflow": ("TensorFlow", "tensorflow", 2), "pytorch": ("PyTorch", "pytorch", 2), "opencv": ("OpenCV", "opencv", 2),
    "scikit-learn": ("scikit-learn", "sklearn", 2), "docker": ("Docker", "docker", 2), "kubernetes": ("Kubernetes", "kubernetes", 2),
    "aws": ("AWS", "aws", 2), "azure": ("Azure", "azure", 2), "gcp": ("Google Cloud", "gcp", 2), "linux": ("Linux", "linux", 2),
    "nginx": ("Nginx", "nginx", 2), "netlify": ("Netlify", "netlify", 2), "heroku": ("Heroku", "heroku", 2),
    "vercel": ("Vercel", "vercel", 2), "postman": ("Postman", "postman", 2), "jest": ("Jest", "jest", 2),
    "cypress": ("Cypress", "cypress", 2), "selenium": ("Selenium", "selenium", 2), "figma": ("Figma", "figma", 2),
    "arduino": ("Arduino", "arduino", 2), "raspberry-pi": ("Raspberry Pi", "raspberrypi", 2), "unity": ("Unity", "unity", 2),
    "blender": ("Blender", "blender", 2), "kafka": ("Kafka", "kafka", 2), "rabbitmq": ("RabbitMQ", "rabbitmq", 2),
    "elasticsearch": ("Elasticsearch", "elasticsearch", 2), "github-actions": ("GitHub Actions", "githubactions", 2),
}
ORBIT_CAPACITY = [10, 16, 26]       # how many logos fit on each ring
LANG_MIN_SHARE = 0.05               # a language must be ≥5% of some repo to count


def detect_new_tech():
    """Languages and topics found in your repos that the galaxy doesn't show yet."""
    from gh import languages, my_work, owned_repos
    have = {src for o in ORBITS for _, src in o[4] if isinstance(src, str)}
    found = {}
    for r in sorted(my_work(owned_repos()), key=lambda r: r["created_at"]):
        langs = languages(r)
        size = sum(langs.values()) or 1
        for lang, n in langs.items():
            icon = LANG_ICONS.get(lang)
            if icon and n / size >= LANG_MIN_SHARE and icon not in have:
                found.setdefault(icon, (lang, icon, 0))
        for t in r.get("topics", []):
            if t in TOPIC_ICONS and TOPIC_ICONS[t][1] not in have:
                name, icon, orbit = TOPIC_ICONS[t]
                found.setdefault(icon, (name, icon, orbit))
    added = []
    for name, icon, orbit in found.values():
        if len(ORBITS[orbit][4]) >= ORBIT_CAPACITY[orbit] or len(skillicon(icon)) < 400:   # ring full / unknown icon
            continue
        ORBITS[orbit][4].append((name, icon))
        added.append(name)
    print("tech stack — auto-added:", ", ".join(added) or "nothing new")


def galaxy():
    W, H = 1200, 630
    cx, cy = 318, 315
    icon_cache = {}

    def icon(src):
        key = str(src)
        if key not in icon_cache:
            if isinstance(src, str):
                raw = skillicon(src)
            elif src[0] == "si":
                raw = simpleicon(src[1], src[2])
            else:
                raw = monogram(src[1], src[2])
            icon_cache[key] = base64.b64encode(raw.encode()).decode()
        return icon_cache[key]

    rings, css = [], []
    for o, (label, col, rad, secs, items) in enumerate(ORBITS):
        size = [50, 46, 42][o]
        direction = "normal" if o % 2 == 0 else "reverse"
        counter = "reverse" if o % 2 == 0 else "normal"
        css.append(f".orb{o} {{ transform-box: view-box; transform-origin: {cx}px {cy}px; animation: spin {secs}s linear infinite {direction}; }}"
                   f".ico{o} {{ transform-box: fill-box; transform-origin: center; animation: spin {secs}s linear infinite {counter}; }}")
        nodes = []
        for k, (name, src) in enumerate(items):
            ang = 2 * math.pi * k / len(items) - math.pi / 2 + o * 0.35
            x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
            nodes.append(f'<g transform="translate({x:.1f},{y:.1f})"><g class="ico{o}">'
                         f'<circle r="{size / 2 + 6}" fill="{BG0}" stroke="{col}" stroke-opacity=".35"/>'
                         f'<image href="data:image/svg+xml;base64,{icon(src)}" x="{-size / 2}" y="{-size / 2}" width="{size}" height="{size}"><title>{escape(name)}</title></image>'
                         f'</g></g>')
        rings.append(f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{col}" stroke-opacity=".28" stroke-width="1.5" stroke-dasharray="{"3 7" if o == 2 else "none"}"/>'
                     f'<g class="orb{o}">{"".join(nodes)}</g>')

    # legend
    lx, ly = 660, 165
    legend = []
    for o, (label, col, rad, secs, items) in enumerate(ORBITS):
        legend.append(f'<g class="rise" style="animation-delay:{0.3 + o * 0.15:.2f}s">'
                      f'<circle cx="{lx + 6}" cy="{ly - 5}" r="6" fill="none" stroke="{col}" stroke-width="2.5"/>'
                      f'<text x="{lx + 22}" y="{ly}" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{col}" letter-spacing="1.5">{escape(label.upper())}</text>')
        x, y = lx, ly + 14
        for name, _ in items:
            w = tw(name, 13) + 22
            if x + w > W - 40:
                x, y = lx, y + 34
            legend.append(f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="26" rx="13" fill="{col}" fill-opacity=".08" stroke="{col}" stroke-opacity=".3"/>'
                          f'<text x="{x + w / 2:.0f}" y="{y + 17.5}" font-family="{SANS}" font-size="13" fill="{TEXT}" text-anchor="middle">{escape(name)}</text>')
            x += w + 7
        legend.append("</g>")
        ly = y + 26 + 38

    style = f"""
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
{''.join(css)}
.core {{ transform-box: fill-box; transform-origin: center; animation: breathe 4s ease-in-out infinite alternate; }}
@keyframes breathe {{ from {{ transform: scale(.92); opacity: .7; }} to {{ transform: scale(1.08); opacity: 1; }} }}
.rise {{ animation: rise .8s {EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
.twinkle {{ animation: tw 3s ease-in-out infinite alternate; }}
@keyframes tw {{ from {{ opacity: .15; }} to {{ opacity: .8; }} }}"""

    import random
    rnd = random.Random(3)
    pts = [(rnd.randint(10, W - 10), rnd.randint(10, H - 10)) for _ in range(90)]
    pts = [(x, y) for x, y in pts if not (lx - 20 < x < W - 20 and 80 < y < ly)][:70]   # keep the legend clear
    stars = "".join(f'<circle class="twinkle" cx="{x}" cy="{y}" r="{rnd.choice([0.8, 1, 1.4])}" '
                    f'fill="{ICE}" style="animation-delay:-{rnd.uniform(0, 3):.1f}s"/>' for x, y in pts)

    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{H}" rx="26"/></clipPath>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{stops(["#050914", "#0b1533", "#0a1026"])}</linearGradient>
  <radialGradient id="neb"><stop offset="0" stop-color="#3b82f6" stop-opacity=".35"/><stop offset=".6" stop-color="#6366f1" stop-opacity=".08"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
  <radialGradient id="core"><stop offset="0" stop-color="#e0f2fe"/><stop offset=".45" stop-color="{AZURE}"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
  <linearGradient id="title" x1="0" y1="0" x2="1" y2="0">{stops(GRAD)}</linearGradient>
</defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  {stars}
  <circle cx="{cx}" cy="{cy}" r="300" fill="url(#neb)"/>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="25.25" fill="none" stroke="{SKY}" stroke-opacity=".12"/>
{''.join(rings)}
<circle class="core" cx="{cx}" cy="{cy}" r="52" fill="url(#core)"/>
<circle cx="{cx}" cy="{cy}" r="34" fill="{BG0}" stroke="{SKY}" stroke-opacity=".6" stroke-width="1.5"/>
<text x="{cx}" y="{cy + 8}" font-family="{SANS}" font-size="22" font-weight="800" fill="url(#title)" text-anchor="middle">KR</text>

<g class="rise">
  <text x="{lx}" y="119" font-family="{SANS}" font-size="32" font-weight="800" fill="url(#title)">My tech stack</text>
</g>
{''.join(legend)}
"""
    n = sum(len(o[4]) for o in ORBITS)
    out("tech-galaxy.svg", svg(W, H, style, body, f"Tech stack galaxy with {n} technologies: " +
                               "; ".join(f"{o[0]}: " + ", ".join(i[0] for i in o[4]) for o in ORBITS)))


# =====================================================================================
# FEATURED PROJECT CARDS (hand-written copy)
# =====================================================================================
FEATURED = [
    dict(file="card-talentbridge.svg", number="01", emoji="💼", title="TalentBridge ATS", tag="full-stack · hiring pipeline", accent=INDIGO, live=True,
         desc_lines=["Applicant tracking system with candidate and recruiter",
                     "roles, a rule-enforced hiring pipeline and JWT auth —",
                     "Spring Boot API on Render, React 19 SPA on Vercel."],
         stack=["Java 21", "Spring Boot", "React 19", "Tailwind", "Docker"]),
    dict(file="card-ceylon-petals.svg", number="02", emoji="💐", title="Ceylon Petals", tag="e-commerce · flower shop", accent=AZURE, live=True,
         desc_lines=["Full-stack flower shop for Sri Lanka — storefront, PayHere",
                     "card checkout, COD and WhatsApp orders, plus an owner",
                     "console for orders, stock, customers and analytics."],
         stack=["TypeScript", "React 19", "Express 5", "Prisma", "PostgreSQL"]),
    dict(file="card-hotel-agent.svg", number="03", emoji="🏨", title="Hotel AI Agent", tag="llm · tool calling", accent=CYAN, live=False,
         desc_lines=["Chat-based front-desk assistant that registers, finds,",
                     "edits and removes guests through LLM tool calling — and",
                     "asks for missing details instead of guessing."],
         stack=["Python", "Llama 3.1", "Groq", "SQLite", "Gradio"]),
    dict(file="card-gooddeeds.svg", number="04", emoji="🤝", title="GoodDeeds", tag="mobile · community impact", accent=BLUE, live=False,
         desc_lines=["Flutter + Firebase app for community service events —",
                     "volunteer and organizer roles, 48-hour attendance",
                     "check-in, impact points and real-time social activity."],
         stack=["Flutter", "Dart", "Firebase", "Firestore"]),
]


def featured():
    for p in FEATURED:
        p = dict(p)
        out(p.pop("file"), card(**p))


# =====================================================================================
# DIVIDER + FOOTER
# =====================================================================================
def divider():
    W, H = 1200, 36
    style = """
.p { transform-box: fill-box; transform-origin: center; animation: bob 3.2s ease-in-out infinite alternate; }
@keyframes bob { from { transform: translateY(2px) rotate(-12deg); } to { transform: translateY(-3px) rotate(12deg); } }"""
    body = f"""
<defs>
  <linearGradient id="l" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset="1" stop-color="{CYAN}" stop-opacity=".65"/></linearGradient>
  <linearGradient id="r" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#6366f1" stop-opacity=".65"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></linearGradient>
</defs>
<rect x="160" y="17" width="380" height="2" rx="1" fill="url(#l)"/>
<rect x="660" y="17" width="380" height="2" rx="1" fill="url(#r)"/>
<g transform="translate(570,18)"><path class="p" d="{SPARK}" fill="{CYAN}" transform="scale(.8)"/></g>
<g transform="translate(600,18)"><path class="p" d="{PETAL}" fill="{AZURE}" style="animation-delay:.5s"/></g>
<g transform="translate(630,18)"><path class="p" d="{SPARK}" fill="{INDIGO}" transform="scale(.8)" style="animation-delay:1s"/></g>
"""
    out("divider.svg", svg(W, H, style, body, "divider"))


if __name__ == "__main__":
    detect_new_tech()
    if "--galaxy-only" in sys.argv:          # what the scheduled workflow runs
        galaxy()
    else:
        hero(); galaxy(); featured(); divider()
