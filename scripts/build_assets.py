"""Generate the hand-made animated SVG assets for the profile README.

usage: python build_assets.py <dir with 1.jpg (photo) and 2.jpg (3D avatar)> <assets dir>
needs: Pillow, internet access (tech logos are fetched and embedded at build time)

Project cards for new repositories are generated separately by update_projects.py.
"""
import base64, io, math, os, re, sys, urllib.request
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from theme import *  # noqa: E402,F403
from PIL import Image  # noqa: E402

IMG_DIR, OUT = sys.argv[1], sys.argv[2]


def out(name, content):
    write(os.path.join(OUT, name), content)


def jpeg_b64(img, size, quality=86):
    buf = io.BytesIO()
    img.convert("RGB").resize(size, Image.LANCZOS).save(buf, "JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


avatar = Image.open(os.path.join(IMG_DIR, "2.jpg"))
photo = Image.open(os.path.join(IMG_DIR, "1.jpg"))
# 3D avatar: square crop of head + shoulders, well clear of the bottom-right watermark
AVATAR = jpeg_b64(avatar.crop((95, 400, 805, 1110)), (320, 320))
# real photo: portrait crop for the polaroid
PHOTO = jpeg_b64(photo.crop((30, 150, 894, 1230)), (304, 380))

PETAL = "M0,-10 C7,-10 10,-2 0,10 C-10,-2 -7,-10 0,-10Z"
SPARK = "M0,-9 L2,-2 L9,0 L2,2 L0,9 L-2,2 L-9,0 L-2,-2Z"


def petals(n, w, h, seed=7):
    import random
    rnd = random.Random(seed)
    shapes, css = [], []
    colors = [SKY, AZURE, INDIGO, CYAN, ICE]
    for i in range(n):
        x = rnd.randint(380, w - 20)
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
# HERO
# =====================================================================================
def hero():
    W, H = 1200, 440
    cx, cy, r = 232, 220, 124
    petal_svg, petal_css = petals(16, W, H)
    roles = ["Full-Stack Developer", "AI Agent Builder", "Flutter Mobile Developer", "CS Undergraduate @ NSBM"]
    role_svg = "\n".join(
        f'<text class="role r{i}" x="458" y="262" font-family="{SANS}" font-size="27" font-weight="600" '
        f'fill="{TEXT}">{escape(t)}</text>' for i, t in enumerate(roles))
    chips = [("Sri Lanka", CYAN), ("BSc (Hons) Computer Science", INDIGO), ("Java · TypeScript · Python · Dart", AZURE)]
    chip_svg, x = [], 430
    for i, (t, c) in enumerate(chips):
        w = tw(t, 14) + 44
        chip_svg.append(
            f'<g class="rise" style="animation-delay:{0.75 + i * 0.1:.2f}s">'
            f'<rect x="{x}" y="336" width="{w:.0f}" height="34" rx="17" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-opacity=".45"/>'
            f'<circle cx="{x + 17}" cy="353" r="4" fill="{c}"/>'
            f'<text x="{x + 29}" y="358" font-family="{SANS}" font-size="14" fill="{TEXT}">{escape(t)}</text></g>')
        x += w + 12

    style = f"""
.rise {{ animation: rise .8s {EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
.orb {{ transform-box: fill-box; transform-origin: center; }}
.o1 {{ animation: drift1 14s ease-in-out infinite alternate; }}
.o2 {{ animation: drift2 17s ease-in-out infinite alternate; }}
.o3 {{ animation: drift1 21s ease-in-out infinite alternate-reverse; }}
@keyframes drift1 {{ to {{ transform: translate(-60px, 40px) scale(1.12); }} }}
@keyframes drift2 {{ to {{ transform: translate(70px, -30px) scale(.92); }} }}
.spin {{ transform-box: view-box; transform-origin: {cx}px {cy}px; animation: spin 26s linear infinite; }}
.spin.rev {{ animation-duration: 40s; animation-direction: reverse; }}
.orbit {{ transform-box: view-box; transform-origin: {cx}px {cy}px; animation: spin 9s linear infinite; }}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.avatar {{ transform-box: view-box; transform-origin: {cx}px {cy}px; animation: pop 1s {EASE} both; }}
@keyframes pop {{ from {{ opacity: 0; transform: scale(.88); }} to {{ opacity: 1; transform: none; }} }}
.pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse 2s ease-out infinite; }}
@keyframes pulse {{ from {{ opacity: .7; transform: scale(1); }} to {{ opacity: 0; transform: scale(2.6); }} }}
.role {{ opacity: 0; animation: role 12s {EASE} infinite; }}
.r1 {{ animation-delay: 3s; }} .r2 {{ animation-delay: 6s; }} .r3 {{ animation-delay: 9s; }}
@keyframes role {{
  0% {{ opacity: 0; transform: translateY(16px); }}
  4%, 21% {{ opacity: 1; transform: none; }}
  25%, 100% {{ opacity: 0; transform: translateY(-16px); }}
}}
.caret {{ animation: blink 1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.shine {{ animation: shine 6s ease-in-out 1.2s infinite; }}
@keyframes shine {{ 0% {{ transform: translateX(-200px); }} 45%, 100% {{ transform: translateX(760px); }} }}
@media (prefers-reduced-motion: reduce) {{ .r0 {{ opacity: 1; }} .petal {{ display: none; }} }}
{petal_css}"""

    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">{stops(["#050914", "#0d1a3d", "#0a1230"])}</linearGradient>
  <radialGradient id="gA"><stop offset="0" stop-color="{AZURE}" stop-opacity=".5"/><stop offset="1" stop-color="{AZURE}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gC"><stop offset="0" stop-color="{CYAN}" stop-opacity=".35"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <radialGradient id="gI"><stop offset="0" stop-color="#6366f1" stop-opacity=".5"/><stop offset="1" stop-color="#6366f1" stop-opacity="0"/></radialGradient>
  <linearGradient id="name" x1="0" y1="0" x2="1" y2="0">{stops(GRAD)}</linearGradient>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">{stops(RING)}</linearGradient>
  <linearGradient id="shineG" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{TEXT}"/></pattern>
  <clipPath id="card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <clipPath id="face"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>
  <mask id="nameMask"><text x="428" y="214" font-family="{SANS}" font-size="66" font-weight="800" letter-spacing="-1.5" fill="#fff">Kasundi Ranaweera</text></mask>
</defs>
<g clip-path="url(#card)">
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" fill="url(#dots)" opacity=".06"/>
  <circle class="orb o1" cx="1010" cy="70" r="300" fill="url(#gA)"/>
  <circle class="orb o2" cx="200" cy="430" r="280" fill="url(#gC)"/>
  <circle class="orb o3" cx="760" cy="440" r="240" fill="url(#gI)"/>
  {petal_svg}
</g>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="27.5" fill="none" stroke="{SKY}" stroke-opacity=".12"/>

<!-- avatar -->
<g class="avatar">
  <circle cx="{cx}" cy="{cy}" r="{r + 26}" fill="{AZURE}" fill-opacity=".07"/>
  <circle class="spin" cx="{cx}" cy="{cy}" r="{r + 18}" fill="none" stroke="url(#ring)" stroke-width="3" stroke-linecap="round" stroke-dasharray="2 12"/>
  <circle class="spin rev" cx="{cx}" cy="{cy}" r="{r + 9}" fill="none" stroke="url(#ring)" stroke-width="2.5" stroke-dasharray="120 40 30 40" stroke-linecap="round" opacity=".9"/>
  <image href="data:image/jpeg;base64,{AVATAR}" x="{cx - r}" y="{cy - r}" width="{2 * r}" height="{2 * r}" clip-path="url(#face)" preserveAspectRatio="xMidYMid slice"/>
  <g class="orbit"><g transform="translate({cx},{cy - r - 18})"><path d="{SPARK}" fill="{SKY}" transform="scale(1.1)"/></g></g>
  <g transform="translate({cx - 78},{cy + r + 2})">
    <rect width="156" height="32" rx="16" fill="{BG1}" stroke="{CYAN}" stroke-opacity=".6"/>
    <circle class="pulse" cx="20" cy="16" r="5" fill="{CYAN}"/><circle cx="20" cy="16" r="5" fill="{CYAN}"/>
    <text x="33" y="21" font-family="{SANS}" font-size="13" font-weight="600" fill="{TEXT}">open to internships</text>
  </g>
</g>

<!-- text -->
<g class="rise" style="animation-delay:.15s">
  <text x="430" y="130" font-family="{MONO}" font-size="17" fill="{CYAN}">~/kasundi <tspan fill="{AZURE}">$</tspan> <tspan fill="{MUTED}">whoami</tspan><tspan class="caret" fill="{AZURE}"> ▍</tspan></text>
</g>
<g class="rise" style="animation-delay:.3s">
  <text x="428" y="214" font-family="{SANS}" font-size="66" font-weight="800" letter-spacing="-1.5" fill="url(#name)">Kasundi Ranaweera</text>
  <g mask="url(#nameMask)" opacity=".55"><rect class="shine" x="380" y="140" width="140" height="90" fill="url(#shineG)" transform="translate(-200,0)"/></g>
</g>
<g class="rise" style="animation-delay:.45s">
  <text x="430" y="262" font-family="{SANS}" font-size="27" font-weight="600" fill="{AZURE}">›</text>
  {role_svg}
</g>
<g class="rise" style="animation-delay:.6s">
  <text x="430" y="306" font-family="{SANS}" font-size="17.5" fill="{MUTED}">Turning ideas into deployed products — from the database schema all the way to the UI.</text>
</g>
{''.join(chip_svg)}
"""
    out("hero.svg", svg(W, H, style, body, "Kasundi Ranaweera — Full-Stack Developer, AI agent builder, CS undergraduate"))


# =====================================================================================
# ABOUT (polaroid + code editor)
# =====================================================================================
def about():
    W, H = 1200, 480
    K, V, P, S, C, KEY = INDIGO, SKY, MUTED, "#bfdbfe", DIM, CYAN

    def s(t): return (f'"{t}"', S)
    lines = [
        [("const ", K), ("kasundi", V), (" = {", P)],
        [("  role:     ", KEY), s("Full-Stack Developer & AI tinkerer"), (",", P)],
        [("  studying: ", KEY), s("BSc (Hons) Computer Science @ NSBM"), (",", P)],
        [("  basedIn:  ", KEY), s("Sri Lanka"), (",", P)],
        [("  builds:   ", KEY), ("[", P), s("web apps"), (", ", P), s("AI agents"), (", ", P), s("mobile apps"), ("],", P)],
        [("  focus:    ", KEY), s("LLM tool calling & AI agents"), (",", P)],
        [("  learning: ", KEY), ("[", P), s("system design"), (", ", P), s("testing"), (", ", P), s("CI/CD"), ("],", P)],
        [("  nextUp:   ", KEY), s("dissertation — NLP for low-resource languages"), (",", P)],
        [("  seeking:  ", KEY), s("software · data · ML internships"), (",", P)],
        [("  motto:    ", KEY), s("my journey, my pace"), (",", P)],
        [("};", P)],
        [("// just a girl in tech, turning ideas into reality ✦", C)],
    ]
    code = []
    for i, toks in enumerate(lines):
        y = 116 + i * 27
        spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in toks)
        code.append(f'<g class="ln" style="animation-delay:{0.35 + i * 0.11:.2f}s">'
                    f'<text x="452" y="{y}" font-family="{MONO}" font-size="13" fill="{DIM}" text-anchor="end">{i + 1}</text>'
                    f'<text x="474" y="{y}" font-family="{MONO}" font-size="15.5" xml:space="preserve">{spans}</text></g>')
    last_y = 116 + (len(lines) - 1) * 27
    caret_x = 474 + tw(lines[-1][0][0], 15.5, mono=True) + 4

    style = f"""
.ln {{ animation: ln .6s {EASE} both; }}
@keyframes ln {{ from {{ opacity: 0; transform: translateX(-8px); }} to {{ opacity: 1; transform: none; }} }}
.win {{ animation: rise .8s {EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(16px); }} to {{ opacity: 1; transform: none; }} }}
.polaroid {{ transform-box: view-box; transform-origin: 215px 60px; animation: sway 7s ease-in-out infinite alternate; }}
@keyframes sway {{ from {{ transform: rotate(-4.5deg); }} to {{ transform: rotate(-2deg); }} }}
.caret {{ animation: blink 1s steps(1) infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.spark {{ transform-box: fill-box; transform-origin: center; animation: twinkle 3s ease-in-out infinite; }}
@keyframes twinkle {{ 0%, 100% {{ opacity: .2; transform: scale(.6) rotate(0deg); }} 50% {{ opacity: 1; transform: scale(1) rotate(45deg); }} }}
@media (prefers-reduced-motion: reduce) {{ .polaroid {{ transform: rotate(-3deg); }} }}"""

    body = f"""
<defs>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="14" stdDeviation="14" flood-color="#000" flood-opacity=".45"/></filter>
  <clipPath id="pic"><rect x="81" y="76" width="268" height="300" rx="4"/></clipPath>
  <linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">{stops(RING)}</linearGradient>
  <linearGradient id="win" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></linearGradient>
</defs>

<!-- polaroid -->
<g class="polaroid" filter="url(#shadow)">
  <rect x="65" y="60" width="300" height="384" rx="6" fill="#f6f9ff"/>
  <image href="data:image/jpeg;base64,{PHOTO}" x="81" y="76" width="268" height="300" clip-path="url(#pic)" preserveAspectRatio="xMidYMid slice"/>
  <text x="215" y="414" font-family="'Segoe Print', 'Bradley Hand', 'Comic Sans MS', cursive" font-size="17" fill="#1e3a8a" text-anchor="middle">the human behind the commits ✦</text>
  <rect x="170" y="44" width="92" height="30" fill="{AZURE}" fill-opacity=".55" transform="rotate(-6 216 59)"/>
</g>
<path class="spark" d="{SPARK}" fill="{AZURE}" transform="translate(372,84)"/>
<path class="spark" d="{SPARK}" fill="{CYAN}" transform="translate(52,420) scale(.7)" style="animation-delay:1.2s"/>

<!-- editor -->
<g class="win" style="animation-delay:.1s">
  <rect x="412" y="20" width="768" height="444" rx="18" fill="url(#win)" stroke="{LINE}" stroke-width="1.5"/>
  <path d="M412,58 V38 a18,18 0 0 1 18,-18 H1162 a18,18 0 0 1 18,18 V58 Z" fill="{BG0}"/>
  <rect x="412" y="56" width="768" height="2.5" fill="url(#bar)" opacity=".85"/>
  <circle cx="438" cy="39" r="6" fill="#ff6b81"/><circle cx="458" cy="39" r="6" fill="#ffd166"/><circle cx="478" cy="39" r="6" fill="#4ade80"/>
  <rect x="502" y="26" width="132" height="30" rx="8" fill="{BG1}"/>
  <text x="518" y="46" font-family="{MONO}" font-size="13" fill="{TEXT}"><tspan fill="{AZURE}">TS</tspan>  about-me.ts</text>
  <text x="1160" y="45" font-family="{MONO}" font-size="12" fill="{DIM}" text-anchor="end">● saved</text>
</g>
{''.join(code)}
<rect class="caret" x="{caret_x:.0f}" y="{last_y - 15}" width="9" height="19" fill="{AZURE}" style="animation-delay:1.8s"/>
"""
    out("about.svg", svg(W, H, style, body, "About Kasundi: full-stack developer and CS undergraduate at NSBM, Sri Lanka, focused on AI agents and seeking internships"))


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
    ("Data, AI & shipping", INDIGO, 260, 110, [
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
                      f'<text x="{lx + 22}" y="{ly}" font-family="{MONO}" font-size="12.5" font-weight="700" fill="{col}" letter-spacing="1.5">ORBIT {o + 1} · {escape(label.upper())}</text>')
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
    stars = "".join(f'<circle class="twinkle" cx="{rnd.randint(10, W - 10)}" cy="{rnd.randint(10, H - 10)}" r="{rnd.choice([0.8, 1, 1.4])}" '
                    f'fill="{ICE}" style="animation-delay:-{rnd.uniform(0, 3):.1f}s"/>' for _ in range(70))

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
  <text x="{lx}" y="77" font-family="{MONO}" font-size="13" fill="{DIM}">~/tech-galaxy <tspan fill="{AZURE}">--orbit</tspan></text>
  <text x="{lx}" y="119" font-family="{SANS}" font-size="32" font-weight="800" fill="url(#title)">Everything in my orbit</text>
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
# JOURNEY TIMELINE
# =====================================================================================
def timeline():
    W, H = 1200, 250
    steps = [
        ("FEB '26", "Hello, GitHub", ["first repos,", "first commits"]),
        ("MAR '26", "Flutter + React", ["student CRUD app,", "campus shuttle system"]),
        ("APR '26", "Built for people", ["GoodDeeds app,", "blind-match PAS (.NET)"]),
        ("JUN '26", "Backend bootcamp", ["Spring Boot APIs,", "CI with GitHub Actions"]),
        ("AUG '26", "Ship it", ["TalentBridge ATS live,", "regression ML"]),
        ("SEP '26", "Enter the agents", ["Ceylon Petals,", "hotel AI agent"]),
        ("NEXT", "Internship ✦", ["NLP for low-resource", "languages"]),
    ]
    cols = [CYAN, SKY, AZURE, BLUE, "#6d8ff8", INDIGO, CYAN]
    x0, x1, ly = 100, 1100, 128
    step = (x1 - x0) / (len(steps) - 1)
    nodes = []
    for i, (m, t, sub) in enumerate(steps):
        c, x, d = cols[i], x0 + i * step, 0.35 + i * 0.22
        last = i == len(steps) - 1
        dot = f'<circle class="pulse" cx="{x:.0f}" cy="{ly}" r="9" fill="{c}" style="animation-delay:{d + .4:.2f}s"/>' if last else ""
        nodes.append(f"""<g class="node" style="animation-delay:{d:.2f}s">
  <text x="{x:.0f}" y="{ly - 34}" font-family="{MONO}" font-size="13" font-weight="700" fill="{c}" text-anchor="middle" letter-spacing="1">{m}</text>
  {dot}<circle cx="{x:.0f}" cy="{ly}" r="13" fill="{BG1}" stroke="{c}" stroke-width="2.5" {'stroke-dasharray="4 4"' if last else ''}/>
  <circle cx="{x:.0f}" cy="{ly}" r="5" fill="{c}"/>
  <text x="{x:.0f}" y="{ly + 46}" font-family="{SANS}" font-size="16" font-weight="700" fill="{TEXT}" text-anchor="middle">{escape(t)}</text>
  <text x="{x:.0f}" y="{ly + 70}" font-family="{SANS}" font-size="13" fill="{MUTED}" text-anchor="middle">{escape(sub[0])}</text>
  <text x="{x:.0f}" y="{ly + 88}" font-family="{SANS}" font-size="13" fill="{MUTED}" text-anchor="middle">{escape(sub[1])}</text>
</g>""")
    style = f"""
.track {{ transform-box: fill-box; transform-origin: left center; animation: grow 1.8s {EASE} .2s both; }}
@keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: none; }} }}
.node {{ animation: rise .7s {EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(12px); }} to {{ opacity: 1; transform: none; }} }}
.pulse {{ transform-box: fill-box; transform-origin: center; animation: pulse 2s ease-out infinite; }}
@keyframes pulse {{ from {{ opacity: .6; transform: scale(1); }} to {{ opacity: 0; transform: scale(2.6); }} }}
.travel {{ animation: travel 6s ease-in-out 2s infinite; }}
@keyframes travel {{ from {{ transform: translateX(0); opacity: 0; }} 10%, 85% {{ opacity: 1; }} to {{ transform: translateX({x1 - x0 - step:.0f}px); opacity: 0; }} }}"""
    body = f"""
<defs>
  <linearGradient id="t" x1="0" y1="0" x2="1" y2="0">{stops(RING)}</linearGradient>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{BG1}"/><stop offset="1" stop-color="{BG0}"/></linearGradient>
  <radialGradient id="dot"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="24" fill="url(#bg)"/>
<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="23.25" fill="none" stroke="{LINE}"/>
<text x="40" y="44" font-family="{MONO}" font-size="13" fill="{DIM}">git log --oneline --graph  <tspan fill="{AZURE}">my-journey</tspan></text>
<rect x="{x0}" y="{ly - 1.5}" width="{x1 - x0 - step:.0f}" height="3" rx="1.5" fill="url(#t)" class="track"/>
<line x1="{x1 - step:.0f}" y1="{ly}" x2="{x1}" y2="{ly}" stroke="{CYAN}" stroke-width="2" stroke-dasharray="3 7" stroke-linecap="round" opacity=".7"/>
<circle class="travel" cx="{x0}" cy="{ly}" r="7" fill="url(#dot)"/>
{''.join(nodes)}
"""
    out("journey.svg", svg(W, H, style, body, "Kasundi's journey: Feb 2026 first repos; Mar Flutter and React; Apr GoodDeeds and PAS; Jun Spring Boot and GitHub Actions; Aug TalentBridge ATS live; Sep Ceylon Petals and hotel AI agent; next an internship and NLP research"))


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
    hero(); about(); galaxy(); featured(); timeline(); divider(); footer()
