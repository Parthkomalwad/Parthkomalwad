"""Rebuild the Projects grid in README.md from the owner's public repos.

Runs in GitHub Actions. Only public, non-fork, non-archived repos are listed,
so a repo shows up here on the next run after it is made public. Each repo
gets an SVG card in assets/projects/, styled to match the hero and headers.
"""
import glob, html, json, os, re, sys, textwrap, urllib.request
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "Parthkomalwad")
ROOT = os.path.join(os.path.dirname(__file__), "..")
README = os.path.join(ROOT, "README.md")
CARDS = os.path.join(ROOT, "assets", "projects")
START, END = "<!-- PROJECTS:START -->", "<!-- PROJECTS:END -->"
# Repos that are plumbing, not projects.
EXCLUDE = {USER.lower(), "parthkomalwad.dev-comments"}
MAX_TOPICS = 3

FONT = 'font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"'
MONO = 'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"'
ACC = "#38bdf8"
LANG_COLORS = {
    "Python": "#3572A5", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "Go": "#00ADD8",
    "Rust": "#dea584", "HTML": "#e34c26", "CSS": "#563d7c", "Shell": "#89e051",
    "Solidity": "#AA6746", "C#": "#178600", "C++": "#f34b7d", "Java": "#b07219",
}
W, H = 600, 210  # card is 196 tall; the rest is transparent gap between rows


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
        return "updated today"
    if days < 14:
        return f"updated {days}d ago"
    if days < 60:
        return f"updated {days // 7}w ago"
    if days < 365:
        return f"updated {days // 30}mo ago"
    return f"updated {days // 365}y ago"


def card(r, now):
    e = html.escape
    lines = textwrap.wrap(r["description"] or "No description yet.", 70)
    if len(lines) > 3:
        lines = lines[:3]
        lines[2] = lines[2][:67].rsplit(" ", 1)[0].rstrip(" .,;:") + "…"
    desc = "".join(
        f'<text x="32" y="{92 + i * 24}" font-size="15" fill="#8b949e">{e(t)}</text>'
        for i, t in enumerate(lines))

    chips, x = "", 32
    for t in r.get("topics", [])[:MAX_TOPICS]:
        w = len(t) * 7.4 + 20
        chips += (f'<rect x="{x}" y="160" width="{w:.0f}" height="22" rx="11" fill="{ACC}" fill-opacity=".1"/>'
                  f'<text x="{x + w / 2:.0f}" y="175" {MONO} font-size="12" fill="#7dd3fc" text-anchor="middle">{e(t)}</text>')
        x += w + 8

    lang = r["language"]
    meta = f'★ {r["stargazers_count"]}  ·  {ago(r["pushed_at"], now)}'
    lang_svg = ""
    if lang:
        lang_svg = (f'<circle cx="{W - 32 - len(lang) * 7.2 - 16:.0f}" cy="43" r="6" fill="{LANG_COLORS.get(lang, "#8b949e")}"/>'
                    f'<text x="{W - 32}" y="48" font-size="14" fill="#c9d1d9" text-anchor="end">{e(lang)}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{e(r["name"])}: {e(r["description"] or "")}">
<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080f"/><stop offset="1" stop-color="#0b1424"/></linearGradient></defs>
<rect x=".5" y=".5" width="{W - 1}" height="195" rx="14" fill="url(#bg)" stroke="#30363d"/>
<rect x="32" y="0" width="56" height="3" rx="1.5" fill="{ACC}"/>
<g {FONT}>
<text x="32" y="50" font-size="24" font-weight="700" fill="#e6edf3">{e(r["name"])}</text>
{lang_svg}
{desc}
<text x="{W - 32}" y="176" font-size="13" fill="#8b949e" text-anchor="end">{e(meta)}</text>
</g>
{chips}
</svg>
'''


def render(repos, now):
    shown = [r for r in repos
             if not (r["private"] or r["fork"] or r["archived"] or r["name"].lower() in EXCLUDE)]
    shown.sort(key=lambda r: r["pushed_at"], reverse=True)

    os.makedirs(CARDS, exist_ok=True)
    keep = set()
    for r in shown:
        name = re.sub(r"[^A-Za-z0-9._-]", "-", r["name"]).lower() + ".svg"
        keep.add(name)
        with open(os.path.join(CARDS, name), "w", encoding="utf-8") as f:
            f.write(card(r, now))
        r["card"] = f"assets/projects/{name}"
    for old in glob.glob(os.path.join(CARDS, "*.svg")):
        if os.path.basename(old) not in keep:
            os.remove(old)

    cells = [f'<a href="{r["html_url"]}"><img src="{r["card"]}" width="49%" '
             f'alt="{html.escape(r["name"])}: {html.escape(r["description"] or "")}"/></a>'
             for r in shown]
    rows = ["&nbsp;\n".join(cells[i:i + 2]) for i in range(0, len(cells), 2)]
    return ('<p align="center">\n' + "\n<br/>\n".join(rows) + "\n</p>\n\n"
            f'<p align="center"><sub>{len(shown)} public repos, newest activity first. '
            f'Updated automatically every 6 hours.</sub></p>')


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    if START not in text or END not in text:
        sys.exit(f"README.md is missing {START} / {END} markers")
    block = f"{START}\n{render(fetch_repos(), datetime.now(timezone.utc))}\n{END}"
    text = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
