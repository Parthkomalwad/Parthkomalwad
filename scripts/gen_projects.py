"""Rebuild the Projects list in README.md from the owner's public repos.

Runs in GitHub Actions. Only public, non-fork, non-archived repos are listed,
so a repo shows up here on the next run after it is made public.
"""
import json, os, re, sys, urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "Parthkomalwad")
README = os.path.join(os.path.dirname(__file__), "..", "README.md")
START, END = "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"
# Repos that are plumbing, not projects.
EXCLUDE = {USER.lower(), "parthkomalwad.dev-comments"}
MAX_TOPICS = 3
MAX_DESC = 110


def fetch_repos():
    repos, page = [], 1
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-profile"}
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    while True:
        url = f"https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
            batch = json.load(r)
        repos += batch
        if len(batch) < 100:
            return repos
        page += 1


def ago(iso, now):
    days = (now - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    if days < 1:
        return "today"
    if days < 14:
        return f"{days}d ago"
    if days < 60:
        return f"{days // 7}w ago"
    if days < 365:
        return f"{days // 30}mo ago"
    return f"{days // 365}y ago"


def cell(text):
    return (text or "").replace("|", "&#124;").replace("\n", " ").strip()


def short(text):
    if len(text) <= MAX_DESC:
        return text
    cut = text[:MAX_DESC].rsplit(" ", 1)[0].rstrip(".,;:")
    return cut + "…"


def render(repos, now):
    shown = [r for r in repos
             if not (r["private"] or r["fork"] or r["archived"] or r["name"].lower() in EXCLUDE)]
    shown.sort(key=lambda r: r["pushed_at"], reverse=True)
    rows = ["| Project | What it does | Language | ★ | Updated |", "|---|---|---|:-:|---|"]
    for r in shown:
        desc = short(cell(r["description"])) or "<i>No description yet</i>"
        topics = " ".join(f"<code>{t}</code>" for t in r.get("topics", [])[:MAX_TOPICS])
        if topics:
            desc += f"<br/><sub>{topics}</sub>"
        rows.append(
            f'| <a href="{r["html_url"]}"><b>{cell(r["name"])}</b></a> | {desc} '
            f'| {cell(r["language"]) or "—"} | {r["stargazers_count"]} | {ago(r["pushed_at"], now)} |'
        )
    footer = (f'\n<sub>{len(shown)} public repos, newest activity first. '
              f'Updated automatically on {now:%b %-d, %Y}.</sub>')
    return "\n".join(rows) + "\n" + footer


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    if START not in text or END not in text:
        sys.exit(f"README.md is missing {START} / {END} markers")
    now = datetime.now(timezone.utc)
    block = f"{START}\n{render(fetch_repos(), now)}\n{END}"
    text = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
