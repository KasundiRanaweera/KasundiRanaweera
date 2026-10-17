"""Generate the hand-made animated SVG assets for the profile README.

usage: python build_assets.py <assets dir>
needs: internet access (tech logos are fetched and embedded at build time)

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
# HERO — name + tagline, centred
# =====================================================================================
TAGLINE = [("🎓", "Computer Science Undergraduate", CYAN),
           ("💻", "Full-Stack Developer", AZURE),
           ("🤖", "AI/ML & Data Science Enthusiast", INDIGO)]
MOTTO = ("✨", "exploring, creating, improving.")


def hero():
    W, H = 1200, 280
    petal_svg, petal_css = petals(18, W, H, x_min=20)

    # tagline pills, centred as one row
    fs, gap = 17, 14
    widths = [tw(t, fs) * 1.08 + fs + 56 for _, t, _ in TAGLINE]
    x = (W - sum(widths) - gap * (len(widths) - 1)) / 2
    pills = []
    for i, ((emo, t, c), w) in enumerate(zip(TAGLINE, widths)):
        pills.append(
            f'<g class="rise" style="animation-delay:{0.55 + i * 0.12:.2f}s">'
            f'<rect x="{x:.0f}" y="150" width="{w:.0f}" height="44" rx="22" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".5"/>'
            f'<text x="{x + 22:.0f}" y="178" font-family="{SANS}" font-size="{fs}" fill="{TEXT}">'
            f'<tspan>{emo}</tspan><tspan dx="9" font-weight="600">{escape(t)}</tspan></text></g>')
        x += w + gap

    style = f"""
.rise {{ animation: rise .8s {EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
.orb {{ transform-box: fill-box; transform-origin: center; }}
.o1 {{ animation: drift1 14s ease-in-out infinite alternate; }}
.o2 {{ animation: drift2 17s ease-in-out infinite alternate; }}
.o3 {{ animation: drift1 21s ease-in-out infinite alternate-reverse; }}
@keyframes drift1 {{ to {{ transform: translate(-60px, 40px) scale(1.12); }} }}
@keyframes drift2 {{ to {{ transform: translate(70px, -30px) scale(.92); }} }}
.shine {{ animation: shine 6s ease-in-out 1.2s infinite; }}
@keyframes shine {{ 0% {{ transform: translateX(-200px); }} 45%, 100% {{ transform: translateX(1300px); }} }}
.line {{ transform-box: fill-box; transform-origin: center; animation: grow 1.2s {EASE} .45s both; }}
@keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: none; }} }}
@media (prefers-reduced-motion: reduce) {{ .petal {{ display: none; }} }}
{petal_css}"""

    name = f'x="600" y="108" font-family="{SANS}" font-size="80" font-weight="800" letter-spacing="-2" text-anchor="middle"'
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{stops(["#050914", "#0d1a3d", "#0a1230"])}</linearGradient>
  <radialGradient id="gA"><stop offset="0" stop-color="{AZURE}" stop-opacity=".5"/><stop offset="1" stop-color="{AZURE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gC"><stop offset="0" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gI"><stop offset="0" stop-color="#6366f1" stop-opacity=".5"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">{stops(GRAD)}</linearGradient>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".5" stop-color="{AZURE}"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></linearGradient>
  <linearGradient id="shineG" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{TEXT}"/></pattern>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <mask id="nameMask"><text {name} fill="#fff">Kasundi Ranaweera</text></mask>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".06"/>
  <circle class="orb o1" cx="1040" cy="40" r="300" fill="url(#gA)"/>
  <circle class="orb o2" cx="140" cy="300" r="280" fill="url(#gC)"/>
  <circle class="orb o3" cx="640" cy="330" r="240" fill="url(#gI)"/>
  {petal_svg}
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="27.5" fill="none" stroke="{SKY}" stroke-opacity=".12"/>

<g class="rise" style="animation-delay:.25s">
  <text {name} fill="url(#name)">Kasundi Ranaweera</text>
  <g mask="url(#nameMask)" opacity=".55"><rect class="shine" x="0" y="22" width="160" height="110" fill="url(#shineG)" transform="translate(-200,0)"/></g>
</g>
<rect class="line" x="420" y="126" width="360" height="2" rx="1" fill="url(#ring)"/>
{''.join(pills)}
<g class="rise" style="animation-delay:.95s">
  <text x="600" y="240" font-family="{SANS}" font-size="19" font-style="italic" fill="{MUTED}" text-anchor="middle"><tspan font-style="normal">{MOTTO[0]}</tspan> {escape(MOTTO[1])}</text>
</g>
"""
    out("hero.svg", svg(W, H, style, body, "Kasundi Ranaweera — Computer Science Undergraduate | Full-Stack Developer | AI/ML & Data Science Enthusiast | exploring, creating, improving."))


# =====================================================================================
# TECH GALAXY — three orbits of real logos, with a legend
# =====================================================================================
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "profile-build"}), timeout=30) as r:
        return r.read().decode()


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


def footer():
    W, H = 1200, 170
    wave = "M0,70 C150,30 300,110 450,70 C600,30 750,110 900,70 C1050,30 1200,110 1350,70 C1500,30 1650,110 1800,70 C1950,30 2100,110 2250,70 C2400,30 2550,110 2700,70 V170 H0Z"
    style = f"""
.w1 {{ animation: wave 14s linear infinite; }}
.w2 {{ animation: wave 20s linear infinite reverse; }}
@keyframes wave {{ to {{ transform: translateX(-900px); }} }}
.in {{ animation: rise 1s {EASE} .3s both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}"""
    body = f"""
<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<linearGradient id="g" x1="0" y1="0" x2="1" y2="0">{stops(RING)}</linearGradient>
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></linearGradient></defs>
<g clip-path="url(#c)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <path class="w2" d="{wave}" fill="#6366f1" opacity=".16" transform="translate(0,22)"/>
  <path class="w1" d="{wave}" fill="url(#g)" opacity=".22" transform="translate(0,44)"/>
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="23.25" fill="none" stroke="{LINE}"/>
<g class="in">
  <text x="600" y="66" font-family="{SANS}" font-size="24" font-weight="700" fill="{TEXT}" text-anchor="middle">creating <tspan fill="{CYAN}">·</tspan> learning <tspan fill="{INDIGO}">·</tspan> growing</text>
  <text x="600" y="96" font-family="{MONO}" font-size="14" fill="{MUTED}" text-anchor="middle">thanks for stopping by ✦ my journey, my pace</text>
</g>
"""
    out("footer.svg", svg(W, H, style, body, "creating, learning, growing — thanks for stopping by"))


if __name__ == "__main__":
    hero(); galaxy(); featured(); divider(); footer()
