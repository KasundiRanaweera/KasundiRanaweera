"""Refresh the auto-generated project showcase in README.md (stdlib only).

Runs in .github/workflows/projects.yml. Picks up every "standard" repository:
  - owned by you (not a fork), not archived, not empty
  - not listed in .github/profile-projects.json -> "featured" or "exclude"
  - not tagged with the topic "hide-from-profile"
The newest ones get an animated card (assets/projects/<repo>.svg); the rest are listed in a table.
Card copy comes from: config "overrides" -> repo description -> first paragraph of the README.
"""
import json, os, re, sys, urllib.error, urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from theme import ACCENTS, card, wrap, write  # noqa: E402

CONFIG = json.load(open(os.path.join(ROOT, ".github", "profile-projects.json"), encoding="utf-8"))
OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER") or CONFIG["owner"]
TOKEN = os.environ.get("GITHUB_TOKEN")
CARD_DIR = os.path.join(ROOT, "assets", "projects")
README = os.path.join(ROOT, "README.md")

EMOJI = {"Python": "🐍", "Jupyter Notebook": "📓", "Java": "☕", "TypeScript": "⚡", "JavaScript": "🌐",
         "Dart": "📱", "C#": "🧩", "C++": "⚙️", "HTML": "🎨", "Go": "🐹", "Kotlin": "📱", "Swift": "📱"}
IGNORED_LANGS = {"CMake", "C", "Objective-C", "Swift", "Kotlin", "Dockerfile", "PLpgSQL", "Batchfile",
                 "Shell", "PowerShell", "Makefile", "Procfile", "SCSS"}


def get(url, raw=False):
    headers = {"User-Agent": f"{OWNER}-profile", "Accept": "application/vnd.github+json"}
    if TOKEN and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            return body if raw else json.loads(body)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def readme_blurb(repo):
    text = get(f"https://raw.githubusercontent.com/{OWNER}/{repo['name']}/{repo['default_branch']}/README.md", raw=True)
    if not text:
        return ""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    para, paras = [], []
    for line in text.splitlines() + [""]:
        s = line.strip()
        skip = (not s or s.startswith(("#", "!", "[!", "<", "|", "---", "***", "===", "- [", "```", "$ ", "> **Note")))
        if skip:
            if para:
                paras.append(" ".join(para))
                para = []
            continue
        para.append(s.lstrip("> ").lstrip("-* ").strip())
    for p in paras:
        p = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", p)        # links / images -> text
        p = re.sub(r"[*`]|(?<!\w)_|_(?!\w)", "", p).strip()      # emphasis / code marks
        if len(p) >= 40 and not p.lower().startswith(("clone", "run ", "install", "npm ", "pip ")):
            return p
    return ""


def pretty(name):
    name = re.sub(r"[_\-]+", " ", name).strip()
    return " ".join(w if w.isupper() or any(c.isupper() for c in w[1:]) else w.capitalize() for w in name.split())


def stack_for(repo):
    if repo["topics"]:
        return [t.replace("-", " ").title() for t in repo["topics"] if t != CONFIG["hide_topic"]][:5]
    langs = get(repo["languages_url"]) or {}
    names = [l for l in sorted(langs, key=langs.get, reverse=True) if l not in IGNORED_LANGS]
    names = ["Jupyter" if l == "Jupyter Notebook" else l for l in names]
    if "Dart" in names:                       # C++/HTML there are Flutter's platform runners
        names = ["Flutter"] + [l for l in names if l not in ("C++", "HTML", "JavaScript")]
    if len(names) > 1:                         # markup only counts when it's all there is
        names = [l for l in names if l not in ("HTML", "CSS")] or names
    return names[:4]


def collect():
    repos, page = [], 1
    while True:
        batch = get(f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    skip = set(CONFIG["featured"]) | set(CONFIG["exclude"]) | {OWNER}
    keep = [r for r in repos
            if not r["fork"] and not r["archived"] and r["size"] > 0
            and r["name"] not in skip and CONFIG["hide_topic"] not in r.get("topics", [])]
    keep.sort(key=lambda r: r["created_at"], reverse=True)

    projects = []
    for r in keep:
        o = CONFIG["overrides"].get(r["name"], {})
        created = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00"))
        lang = r["language"] or ""
        projects.append(dict(
            name=r["name"], url=r["html_url"], homepage=r["homepage"] or "",
            title=o.get("title") or pretty(r["name"]),
            desc=o.get("description") or (r["description"] or "").strip() or readme_blurb(r)
                 or "A fresh project — the README is on its way.",
            stack=o.get("stack") or stack_for(r),
            emoji=o.get("emoji") or EMOJI.get(lang, "✨"),
            lang=lang, created=created,
        ))
    return projects


def render(projects):
    now = datetime.now(timezone.utc)
    n_cards = CONFIG["cards"]
    os.makedirs(CARD_DIR, exist_ok=True)
    wanted = set()
    cells = []
    for i, p in enumerate(projects[:n_cards]):
        fresh = (now - p["created"]).days <= 30
        badge = "NEW" if fresh else p["created"].strftime("%b %Y")
        tag = " · ".join(x for x in [(p["lang"] or "project").lower(), p["created"].strftime("%b '%y").lower()] if x)
        svg = card(p["title"], tag, wrap(p["desc"]), p["stack"], ACCENTS[i % len(ACCENTS)],
                   emoji=p["emoji"], number=f"{i + CONFIG['first_card_number']:02d}", live=bool(p["homepage"]), badge=badge)
        fname = f"{p['name']}.svg"
        wanted.add(fname)
        write(os.path.join(CARD_DIR, fname), svg)
        links = f'<a href="{p["url"]}">Source</a>' + (f' · <a href="{p["homepage"]}">Live demo</a>' if p["homepage"] else "")
        cells.append(f'    <td width="50%">\n      <a href="{p["homepage"] or p["url"]}"><img src="./assets/projects/{fname}" width="100%" '
                     f'alt="{p["title"]} — {p["desc"][:150].replace(chr(34), "")}"/></a>\n'
                     f'      <p align="center"><sub>{links}</sub></p>\n    </td>')
    for f in os.listdir(CARD_DIR):                       # drop cards that rotated out
        if f.endswith(".svg") and f not in wanted:
            os.remove(os.path.join(CARD_DIR, f))

    rows = ["<table>"]
    for i in range(0, len(cells), 2):
        rows += ["  <tr>", *cells[i:i + 2], "  </tr>"]
    rows.append("</table>")
    latest = "\n".join(rows) if cells else "<p><i>New projects will appear here automatically.</i></p>"

    rest = projects[n_cards:]
    if rest:
        table = ["<details>", "<summary><b>&nbsp;🔹 More things I've built</b></summary>", "<br/>", "",
                 "| | Project | What it is | Stack |", "|:-:|---|---|---|"]
        for p in rest:
            d = wrap(p["desc"], 220, 1)[0].replace("|", "/")
            table.append(f'| {p["emoji"]} | [{p["title"]}]({p["url"]}) | {d} | {" · ".join(p["stack"])} |')
        table += ["", "</details>"]
        more = "\n".join(table)
    else:
        more = ""
    return latest, more


def splice(text, key, content):
    start, end = f"<!-- {key}:START -->", f"<!-- {key}:END -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        sys.exit(f"README is missing the {start} / {end} markers")
    return pattern.sub(lambda _: f"{start}\n{content}\n{end}", text)


def main():
    projects = collect()
    print(f"{len(projects)} standard projects:", ", ".join(p["name"] for p in projects))
    latest, more = render(projects)
    text = open(README, encoding="utf-8").read()
    new = splice(splice(text, "LATEST-PROJECTS", latest), "MORE-PROJECTS", more)
    if new != text:
        with open(README, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print("README updated")
    else:
        print("README already up to date")


if __name__ == "__main__":
    main()
