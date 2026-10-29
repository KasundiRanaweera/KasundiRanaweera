"""Tiny GitHub API helpers shared by the profile scripts (stdlib only)."""
import json, os, sys, time, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = json.load(open(os.path.join(ROOT, ".github", "profile-projects.json"), encoding="utf-8"))
OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER") or CONFIG["owner"]
TOKEN = os.environ.get("GITHUB_TOKEN")

# Flutter projects ship generated platform runners; those bytes aren't languages you wrote
FLUTTER_RUNNER_LANGS = {"C++", "C", "CMake", "Swift", "Kotlin", "Objective-C", "HTML", "JavaScript"}


def open_url(req, tries=4):
    """urlopen with retries — scheduled runs shouldn't fail on a dropped connection or a 5xx."""
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == tries - 1:
                raise
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if attempt == tries - 1:
                raise
        time.sleep(2 ** attempt)


def get(url, raw=False):
    headers = {"User-Agent": f"{OWNER}-profile", "Accept": "application/vnd.github+json"}
    if TOKEN and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {TOKEN}"
    try:
        body = open_url(urllib.request.Request(url, headers=headers))
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
    data = json.loads(open_url(req))
    if "errors" in data:
        sys.exit(data["errors"])
    return data["data"]


def owned_repos():
    repos, page = [], 1
    while True:
        batch = get(f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner&page={page}")
        if batch is None:
            sys.exit(f"GitHub user '{OWNER}' not found — check \"owner\" in .github/profile-projects.json")
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
