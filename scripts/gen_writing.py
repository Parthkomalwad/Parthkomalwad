"""Rebuild the Writing list in README.md from the parthkomalwad.dev RSS feed.

Runs in GitHub Actions next to gen_projects.py. If the feed can't be read,
the README is left as it is, so a site outage never blanks the section.
"""
import html, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

FEED = os.environ.get("FEED_URL", "https://parthkomalwad.dev/rss.xml")
SITE = "https://parthkomalwad.dev/writing/"
README = os.path.join(os.path.dirname(__file__), "..", "README.md")
START, END = "<!-- WRITING:START -->", "<!-- WRITING:END -->"
MAX_POSTS = 3


def fetch_posts():
    req = urllib.request.Request(FEED, headers={"User-Agent": "Parthkomalwad-profile"})
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    posts = []
    for item in root.iter("item"):
        posts.append({
            "title": item.findtext("title", "").strip(),
            "link": item.findtext("link", "").strip(),
            "desc": item.findtext("description", "").strip(),
            "date": parsedate_to_datetime(item.findtext("pubDate")),
        })
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts[:MAX_POSTS]


def render(posts):
    e = html.escape
    items = [
        f'<li><a href="{e(p["link"])}"><b>{e(p["title"])}</b></a><br/>'
        f'<sub>{p["date"]:%b %-d, %Y} &middot; {e(p["desc"])}</sub></li>'
        for p in posts
    ]
    return ("<ul>\n" + "\n".join(items) + "\n</ul>\n\n"
            f'<p align="right"><a href="{SITE}"><b>All writing on parthkomalwad.dev &rarr;</b></a></p>')


def main():
    try:
        posts = fetch_posts()
    except Exception as exc:  # network or feed problem: keep the old list
        print(f"feed unavailable, README unchanged: {exc}", file=sys.stderr)
        return
    if not posts:
        return
    with open(README, encoding="utf-8") as f:
        text = f.read()
    if START not in text or END not in text:
        sys.exit(f"README.md is missing {START} / {END} markers")
    block = f"{START}\n{render(posts)}\n{END}"
    text = re.sub(re.escape(START) + ".*?" + re.escape(END), lambda _: block, text, flags=re.S)
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
