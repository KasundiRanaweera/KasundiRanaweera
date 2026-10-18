"""Hourly GitHub stats for the profile README (stdlib only).

usage: GITHUB_TOKEN=... python stats.py <out dir>
Writes, for .github/workflows/stats.yml to publish on the `output` branch:
  contributions-dark.svg / contributions-light.svg  compact GitHub-style chart, green snake eating the squares
  streak.svg                                        total, current and longest streak (all years)
  languages.svg                                     most used languages across your own repos
and, inside the repo itself (committed to main by the same workflow):
  assets/tiles, assets/chart, README.md             plain chart with a hover tooltip on every square
"""
import os, sys
from datetime import date, datetime, timedelta, timezone
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import theme as th  # noqa: E402
from gh import CONFIG, OWNER, graphql, languages, my_work, owned_repos  # noqa: E402

OUT = sys.argv[1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.now(timezone.utc).date()   # replaced in main() by the last day of GitHub's calendar (your timezone)

QUERY = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { date weekday contributionCount contributionLevel } } } } } }"""
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

# GitHub's own colours
THEMES = {
    "dark": dict(bg="#0d1117", border="#30363d", text="#e6edf3", muted="#8b949e", outline="#ffffff", outline_op=".05",
                 levels=["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"], snake="#b8f34a", snake_edge="#0d1117"),
    "light": dict(bg="#ffffff", border="#d0d7de", text="#1f2328", muted="#59636e", outline="#1b1f23", outline_op=".06",
                  levels=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"], snake="#4d9a1e", snake_edge="#ffffff"),
}
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
CELL, STEP = 10, 13
SNAKE_LENGTH = 4
SNAKE_SECONDS, SNAKE_PAUSE = 24, 2.5              # one sweep of the whole year, then a short pause


def fetch():
    return graphql(QUERY, login=OWNER)["user"]["contributionsCollection"]["contributionCalendar"]


def day_label(d):
    n, dt = d["contributionCount"], date.fromisoformat(d["date"])
    suffix = "th" if 10 <= dt.day % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(dt.day % 10, "th")
    return f'{n or "No"} contribution{"" if n == 1 else "s"} on {dt.strftime("%B")} {dt.day}{suffix}.'


def month_marks(weeks):
    """(week index, 'Oct') for every month label GitHub would draw."""
    marks, last = [], -9
    for wi, week in enumerate(weeks):
        first = date.fromisoformat(week["contributionDays"][0]["date"])
        if wi == 0 or first.day <= 7:                 # GitHub labels the week a month starts in
            if wi - last >= 3 and (wi > 0 or first.day <= 14):
                marks.append((wi, first.strftime("%b")))
                last = wi
    return marks


# =====================================================================================
# snake chart — compact, green snake that eats the squares, for the "On GitHub" section
# =====================================================================================
def render_snake(cal, t):
    weeks = cal["weeks"]
    pad, left = 12, 30
    grid_x, grid_y = pad + left, pad + 20             # month labels sit above the grid
    W = grid_x + len(weeks) * STEP - 3 + pad
    H = grid_y + 7 * STEP - 3 + pad

    # snake route: down one week column, up the next, through every day
    route = []
    for wi, week in enumerate(weeks):
        days = sorted(week["contributionDays"], key=lambda d: d["weekday"], reverse=wi % 2 == 1)
        route += [(wi, d) for d in days]
    T_STEP = SNAKE_SECONDS / len(route)               # seconds per cell
    moving = len(route) * T_STEP
    total_s = moving + SNAKE_PAUSE
    f_end = moving / total_s

    months = "".join(f'<text x="{grid_x + wi * STEP}" y="{grid_y - 7}" font-size="11" fill="{t["text"]}">{m}</text>'
                     for wi, m in month_marks(weeks))
    css, cells = [], []
    for i, (wi, d) in enumerate(route):
        x, y = grid_x + wi * STEP, grid_y + d["weekday"] * STEP
        lvl = LEVEL[d["contributionLevel"]]
        colour = t["levels"][lvl]
        cls = ""
        if lvl:   # eaten when the head arrives, back during the pause (CSS animation works wherever the SVG is an <img>)
            eaten, back = 100 * (i + 1) * T_STEP / total_s, 100 * (moving + SNAKE_PAUSE * .5) / total_s
            css.append(f".e{i}{{animation:e{i} {total_s:.2f}s step-end infinite}}"
                       f"@keyframes e{i}{{0%{{fill:{colour}}}{eaten:.2f}%{{fill:{t['levels'][0]}}}{back:.2f}%{{fill:{colour}}}}}")
            cls = f' class="e{i}"'
        cells.append(f'<rect{cls} x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{colour}"'
                     f' stroke="{t["outline"]}" stroke-opacity="{t["outline_op"]}"/>')

    path = "M" + " L".join(f"{grid_x + wi * STEP + CELL / 2},{grid_y + d['weekday'] * STEP + CELL / 2}" for wi, d in route)
    snake = []
    for k in range(SNAKE_LENGTH):                     # head first, body trails one cell behind each
        size = CELL - k * 1.2
        snake.append(
            f'<rect x="{-size / 2:.1f}" y="{-size / 2:.1f}" width="{size:.1f}" height="{size:.1f}" rx="3" fill="{t["snake"]}" '
            f'stroke="{t["snake_edge"]}" stroke-width="1.2" fill-opacity="{1 - k * .15:.2f}" opacity="0">'
            f'<animateMotion path="{path}" dur="{total_s:.2f}s" begin="{k * T_STEP:.3f}s" repeatCount="indefinite" '
            f'calcMode="linear" keyPoints="0;1;1" keyTimes="0;{f_end:.4f};1"/>'
            f'<animate attributeName="opacity" dur="{total_s:.2f}s" begin="{k * T_STEP:.3f}s" repeatCount="indefinite" '
            f'calcMode="discrete" values="1;0" keyTimes="0;{f_end:.4f}"/></rect>')

    days = "".join(f'<text x="{pad}" y="{grid_y + r * STEP + 9}" font-size="11" fill="{t["text"]}">{n}</text>'
                   for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri")))
    heading = f'{cal["totalContributions"]:,} contributions in the last year'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{heading}">'
            f'<title>{heading}</title><style>{"".join(css)}</style>'
            f'<g font-family="{FONT}">'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="6" fill="{t["bg"]}" stroke="{t["border"]}"/>'
            f'{months}{days}{"".join(cells)}{"".join(reversed(snake))}</g></svg>\n')


# =====================================================================================
# plain chart with hover text — 7 rows of tiny images, each with a title like GitHub's tooltip
# (GitHub shows README images as pictures, so per-square hover needs one <img title=…> per day)
# =====================================================================================
TW, TH, GUT = 14, 19, 30                               # tile width/height (height fits <pre>'s 19.7px line), gutter width
RECT_W, RECT_H = 11, 15
TILE_THEMES = {
    "d": dict(levels=["#232b36", "#0e4429", "#006d32", "#26a641", "#39d353"], text="#e6edf3", muted="#8b949e", edge="#ffffff", edge_op=".05"),
    "l": dict(levels=["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"], text="#1f2328", muted="#59636e", edge="#1b1f23", edge_op=".06"),
}
MODE = {"d": "gh-dark-mode-only", "l": "gh-light-mode-only"}


def tile_svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>\n'


def square(x, y, colour, edge, edge_op):
    return (f'<rect x="{x}" y="{y}" width="{RECT_W}" height="{RECT_H}" rx="2.5" fill="{colour}" '
            f'stroke="{edge}" stroke-opacity="{edge_op}"/>')


def write_tiles(root):
    """Static pieces: one tile per contribution level and theme, weekday labels, an empty tile."""
    d = os.path.join(root, "assets", "tiles")
    os.makedirs(d, exist_ok=True)
    for k, t in TILE_THEMES.items():
        for lvl, colour in enumerate(t["levels"]):
            save_to(os.path.join(d, f"{k}{lvl}.svg"), tile_svg(TW, TH, square((TW - RECT_W) / 2, (TH - RECT_H) / 2, colour, t["edge"], t["edge_op"])))
        for name in ("Mon", "Wed", "Fri"):
            save_to(os.path.join(d, f"{k}-{name.lower()}.svg"),
                    tile_svg(GUT, TH, f'<text x="0" y="{TH / 2 + 4.2}" font-size="11" font-family="{FONT}" fill="{t["text"]}">{name}</text>'))
    save_to(os.path.join(d, "blank.svg"), tile_svg(TW, TH, ""))
    save_to(os.path.join(d, "gutter.svg"), tile_svg(GUT, TH, ""))


def write_rows(root, weeks):
    """Month row and Less/More legend: depend on today's date, so rebuilt every run."""
    d = os.path.join(root, "assets", "chart")
    os.makedirs(d, exist_ok=True)
    width = GUT + len(weeks) * TW
    for k, t in TILE_THEMES.items():
        months = "".join(f'<text x="{GUT + wi * TW}" y="{TH / 2 + 4.2}" font-size="11" font-family="{FONT}" fill="{t["text"]}">{m}</text>'
                         for wi, m in month_marks(weeks))
        save_to(os.path.join(d, f"months-{k}.svg"), tile_svg(width, TH, months))
        lx = width - (5 * TW + 70)
        legend = (f'<text x="{lx}" y="{TH / 2 + 4.2}" font-size="11" font-family="{FONT}" fill="{t["muted"]}">Less</text>'
                  + "".join(square(lx + 30 + i * TW + (TW - RECT_W) / 2, (TH - RECT_H) / 2, c, t["edge"], t["edge_op"]) for i, c in enumerate(t["levels"]))
                  + f'<text x="{lx + 34 + 5 * TW}" y="{TH / 2 + 4.2}" font-size="11" font-family="{FONT}" fill="{t["muted"]}">More</text>')
        save_to(os.path.join(d, f"legend-{k}.svg"), tile_svg(width, TH, legend))


def chart_block(cal):
    """README markup for the hoverable chart (both GitHub themes)."""
    weeks = cal["weeks"]
    total = cal["totalContributions"]
    by = [{d["weekday"]: d for d in w["contributionDays"]} for w in weeks]

    def img(src, k, title="", w=TW):
        t = f' title="{title}"' if title else ""
        return f'<img src="./assets/{src}#{MODE[k]}"{t} width="{w}" height="{TH}" align="top">'

    rows = [[] for _ in range(9)]
    for k in ("d", "l"):
        rows[0].append(img(f"chart/months-{k}.svg", k, w=GUT + len(weeks) * TW))
        for r in range(7):
            rows[r + 1].append(img(f"tiles/{k}-{('mon', 'wed', 'fri')[(r - 1) // 2]}.svg", k, w=GUT) if r in (1, 3, 5)
                               else img("tiles/gutter.svg", k, w=GUT))
            for wd in by:
                rows[r + 1].append(img(f"tiles/{k}{LEVEL[wd[r]['contributionLevel']]}.svg", k, escape(day_label(wd[r])))
                                   if r in wd else img("tiles/blank.svg", k))
        rows[8].append(img(f"chart/legend-{k}.svg", k, w=GUT + len(weeks) * TW))
    body = ["".join(r) for r in rows]
    # each theme's block is its own line group; GitHub hides the one that doesn't match the viewer's theme
    return (f'**{total:,}** contributions in the last year\n\n<pre>\n' + "\n".join(body) + "\n</pre>")


def splice_readme(block):
    path = os.path.join(ROOT, "README.md")
    s = open(path, encoding="utf-8").read()
    start, end = "<!-- CONTRIB-CHART:START -->", "<!-- CONTRIB-CHART:END -->"
    a, b = s.find(start), s.find(end)
    if a < 0 or b < 0:
        print("README has no CONTRIB-CHART markers — skipping chart block")
        return
    new = s[:a + len(start)] + "\n" + block + "\n" + s[b:]
    if new != s:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print("README chart block updated")


# =====================================================================================
# streak card — totals and streaks across every year you've contributed
# =====================================================================================
YEARS = "query($login: String!) { user(login: $login) { contributionsCollection { contributionYears } } }"
HISTORY = """query($login: String!, $from: DateTime!, $to: DateTime!) { user(login: $login) {
  contributionsCollection(from: $from, to: $to) { contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }"""


def history():
    years = graphql(YEARS, login=OWNER)["user"]["contributionsCollection"]["contributionYears"]
    days = {}
    for y in years:
        cal = graphql(HISTORY, login=OWNER, **{"from": f"{y}-01-01T00:00:00Z", "to": f"{y}-12-31T23:59:59Z"})
        for w in cal["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in w["contributionDays"]:
                day = date.fromisoformat(d["date"])
                if day <= TODAY:
                    days[day] = d["contributionCount"]
    return sorted(days.items())


def streaks(days):
    counts = dict(days)
    one = timedelta(days=1)
    total = sum(counts.values())
    first = next((d for d, c in days if c), None)
    # today without a contribution yet doesn't break the streak
    d = TODAY if counts.get(TODAY, 0) else TODAY - one
    end, current = d, 0
    while counts.get(d, 0) > 0:
        current, d = current + 1, d - one
    cur = (current, d + one, end) if current else (0, None, None)
    best, run, start = (0, None, None), 0, None
    for day, c in days:
        if c:
            start = day if run == 0 else start
            run += 1
            if run > best[0]:
                best = (run, start, day)
        else:
            run = 0
    return total, first, cur, best


def fmt(d):
    if d is None:
        return ""
    return d.strftime("%b %d").replace(" 0", " ") + ("" if d.year == TODAY.year else d.strftime(", %Y"))


def span(a, b):
    if a is None:
        return "No streak yet"
    return fmt(a) if a == b else f"{fmt(a)} – {fmt(b)}"


def streak_card(days):
    total, first, (cur, cs, ce), (best, bs, be) = streaks(days)
    W, H = 495, 195
    cols = [82.5, 247.5, 412.5]

    def stat(x, number, label, sub, colour, delay):
        return (f'<g class="rise" style="animation-delay:{delay}s">'
                f'<text x="{x}" y="88" font-size="28" font-weight="800" fill="{th.TEXT}" text-anchor="middle">{number:,}</text>'
                f'<text x="{x}" y="140" font-size="14" font-weight="600" fill="{colour}" text-anchor="middle">{label}</text>'
                f'<text x="{x}" y="165" font-size="12" fill="{th.DIM}" text-anchor="middle">{escape(sub)}</text></g>')

    style = f"""
.rise {{ animation: rise .8s {th.EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
.ring {{ stroke-dasharray: 100; animation: draw 1.4s {th.EASE} .2s both; }}
@keyframes draw {{ from {{ stroke-dashoffset: 100; }} to {{ stroke-dashoffset: 0; }} }}
.flame {{ transform-box: fill-box; transform-origin: center bottom; animation: flicker 1.6s ease-in-out infinite alternate; }}
@keyframes flicker {{ to {{ transform: scale(1.12) rotate(4deg); }} }}"""
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{th.BG1}"/><stop offset="1" stop-color="{th.BG0}"/></linearGradient>
  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">{th.stops(th.RING)}</linearGradient>
</defs>
<g font-family="{th.SANS}">
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="url(#bg)" stroke="{th.LINE}"/>
<line x1="165" y1="28" x2="165" y2="167" stroke="{th.LINE}"/><line x1="330" y1="28" x2="330" y2="167" stroke="{th.LINE}"/>
{stat(cols[0], total, "Total Contributions", f"{fmt(first)} – Present" if first else "", th.SKY, .1)}
<circle class="ring" cx="{cols[1]}" cy="71" r="40" fill="none" stroke="url(#ring)" stroke-width="5" pathLength="100" transform="rotate(-90 {cols[1]} 71)"/>
<circle cx="{cols[1]}" cy="31" r="13" fill="{th.BG1}"/>
<text class="flame" x="{cols[1]}" y="38" font-size="18" text-anchor="middle">🔥</text>
<g class="rise" style="animation-delay:.25s">
  <text x="{cols[1]}" y="81" font-size="28" font-weight="800" fill="{th.TEXT}" text-anchor="middle">{cur:,}</text>
  <text x="{cols[1]}" y="140" font-size="14" font-weight="700" fill="{th.AZURE}" text-anchor="middle">Current Streak</text>
  <text x="{cols[1]}" y="165" font-size="12" fill="{th.DIM}" text-anchor="middle">{escape(span(cs, ce))}</text>
</g>
{stat(cols[2], best, "Longest Streak", span(bs, be), th.INDIGO, .4)}
</g>"""
    title = f"{total:,} total contributions; current streak {cur} days; longest streak {best} days"
    return th.svg(W, H, style, body, title), (total, cur, best)


# =====================================================================================
# languages card — bytes across your own repos (forks, exclusions and hidden repos left out)
# =====================================================================================
LANG_COLORS = {"Java": "#b07219", "Python": "#3572A5", "TypeScript": "#3178c6", "JavaScript": "#f1e05a",
               "Dart": "#00B4AB", "C#": "#178600", "C++": "#f34b7d", "C": "#555555", "HTML": "#e34c26",
               "CSS": "#663399", "Go": "#00ADD8", "Kotlin": "#A97BFF", "Swift": "#F05138", "PHP": "#4F5D95",
               "Rust": "#dea584", "Ruby": "#701516", "Shell": "#89e051", "Vue": "#41b883", "Svelte": "#ff3e00",
               "R": "#198CE7", "Scala": "#c22d40", "Jupyter Notebook": "#DA5B0B", "SQL": "#e38c00", "TSQL": "#e38c00"}


def language_totals(repos):
    hide = set(CONFIG.get("hide_languages", []))
    totals = {}
    for r in repos:
        for lang, n in languages(r).items():
            if lang not in hide:
                totals[lang] = totals.get(lang, 0) + n
    return sorted(totals.items(), key=lambda kv: kv[1], reverse=True)


def languages_card(totals, top=6):
    W, H = 300, 195
    shown = totals[:top]
    s = sum(n for _, n in shown) or 1
    x, bar = 24, []
    for lang, n in shown:
        w = 252 * n / s
        bar.append(f'<rect x="{x:.2f}" y="54" width="{w:.2f}" height="8" fill="{LANG_COLORS.get(lang, th.MUTED)}"/>')
        x += w
    rows = []
    for i, (lang, n) in enumerate(shown):
        cx, cy = 24 + (i % 2) * 134, 94 + (i // 2) * 30
        rows.append(f'<g class="rise" style="animation-delay:{.2 + i * .07:.2f}s">'
                    f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{LANG_COLORS.get(lang, th.MUTED)}"/>'
                    f'<text x="{cx + 16}" y="{cy}" font-size="13" fill="{th.TEXT}">{escape(lang)} '
                    f'<tspan fill="{th.DIM}">{100 * n / s:.1f}%</tspan></text></g>')
    style = f"""
.rise {{ animation: rise .8s {th.EASE} both; }}
@keyframes rise {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: none; }} }}
.bar {{ transform-box: fill-box; transform-origin: left center; animation: grow 1.2s {th.EASE} .15s both; }}
@keyframes grow {{ from {{ transform: scaleX(0); }} to {{ transform: none; }} }}"""
    body = f"""
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{th.BG1}"/><stop offset="1" stop-color="{th.BG0}"/></linearGradient>
  <clipPath id="bar"><rect x="24" y="54" width="252" height="8" rx="4"/></clipPath>
</defs>
<g font-family="{th.SANS}">
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="20" fill="url(#bg)" stroke="{th.LINE}"/>
<text x="24" y="36" font-size="16" font-weight="700" fill="{th.SKY}">Most Used Languages</text>
<g clip-path="url(#bar)"><g class="bar">{''.join(bar)}</g></g>
{''.join(rows)}
</g>"""
    title = "Most used languages: " + ", ".join(f"{l} {100 * n / s:.1f}%" for l, n in shown)
    return th.svg(W, H, style, body, title)


def save(name, content):
    save_to(os.path.join(OUT, name), content)


def save_to(path, content):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def main():
    global TODAY
    os.makedirs(OUT, exist_ok=True)
    cal = fetch()
    TODAY = max(date.fromisoformat(d["date"]) for w in cal["weeks"] for d in w["contributionDays"])
    for name, theme in THEMES.items():
        save(f"contributions-{name}.svg", render_snake(cal, theme))
    write_tiles(ROOT)
    write_rows(ROOT, cal["weeks"])
    splice_readme(chart_block(cal))
    streak, (total, cur, best) = streak_card(history())
    save("streak.svg", streak)
    totals = language_totals(my_work(owned_repos()))
    save("languages.svg", languages_card(totals))
    print(f"chart: {cal['totalContributions']} in the last year | streak: total {total}, current {cur}, longest {best}")
    print("languages:", ", ".join(f"{l} {n}" for l, n in totals[:8]))


if __name__ == "__main__":
    main()
