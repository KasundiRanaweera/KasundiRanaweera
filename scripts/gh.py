"""Tiny GitHub API helpers shared by the profile scripts (stdlib only)."""
import json, os, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = json.load(open(os.path.join(ROOT, ".github", "profile-projects.json"), encoding="utf-8"))
OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER") or CONFIG["owner"]
TOKEN = os.environ.get("GITHUB_TOKEN")

# Flutter projects ship generated platform runners; those bytes aren't languages you wrote
FLUTTER_RUNNER_LANGS = {"C++", "C", "CMake", "Swift", "Kotlin", "Objective-C", "HTML", "JavaScript"}


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


def graphql(query, **variables):
    if not TOKEN:
        sys.exit("GITHUB_TOKEN is required for the GraphQL API")
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": query, "variables": variables}).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": f"{OWNER}-profile"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if "errors" in data:
        sys.exit(data["errors"])
    return data["data"]


def owned_repos():
    repos, page = [], 1
    while True:
        batch = get(f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def my_work(repos):
    """Repos that represent your own work: no forks, archives, empties, exclusions or hidden ones."""
    skip = set(CONFIG["exclude"]) | {OWNER}
    return [r for r in repos
            if not r["fork"] and not r["archived"] and r["size"] > 0
            and r["name"] not in skip and CONFIG["hide_topic"] not in r.get("topics", [])]


def languages(repo):
    langs = get(repo["languages_url"]) or {}
    if "Dart" in langs:
        langs = {k: v for k, v in langs.items() if k not in FLUTTER_RUNNER_LANGS}
    return langs
