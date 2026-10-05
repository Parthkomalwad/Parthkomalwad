"""Render 1280x640 GitHub social preview PNGs for each repo.

Usage: python scripts/gen_social.py
Needs Google Chrome (headless screenshot). Output: social/<repo>.png (social preview) and social/card-<repo>.png (profile README card)
Upload each PNG in the repo's Settings -> General -> Social preview.
"""
import html
import os
import shutil
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "social")
CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chrome",
]

# Brand tokens copied from each project's docs at parthkomalwad.dev/projects/<slug>/ (dark theme).
GF = "https://fonts.googleapis.com/css2?family="
SABLE = {"acc": "#A99BFF", "ink": "#C4B8FF", "ok": "#4CC38A", "bg": "#0A0D12", "surf": "#11161E",
         "display": "'Bricolage Grotesque'", "body": "'Schibsted Grotesk'", "mono": "'JetBrains Mono'",
         "fonts": GF + "Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Schibsted+Grotesk:wght@400;500&family=JetBrains+Mono:wght@500"}
JEVBRIEF = {"acc": "#ff5fdc", "ink": "#ff8ae6", "ok": "#5fd18e", "bg": "#0e0e10", "surf": "#18181b",
            "display": "system-ui, 'Segoe UI'", "body": "system-ui, 'Segoe UI'", "mono": "'Cascadia Mono', 'JetBrains Mono'",
            "fonts": GF + "JetBrains+Mono:wght@500"}
ARCHON = {"acc": "#818CF8", "ink": "#A5B4FC", "ok": "#10B981", "bg": "#0F1117", "surf": "#161B27",
          "display": "'Geist'", "body": "'Geist'", "mono": "'JetBrains Mono'",
          "fonts": GF + "Geist:wght@400;500;700;800&family=JetBrains+Mono:wght@500"}
VERITAS = {"acc": "#C9A84C", "ink": "#E8D08A", "ok": "#4CC38A", "bg": "#0C0B0E", "surf": "#151318",
           "display": "'Syne'", "body": "'IBM Plex Sans'", "mono": "'IBM Plex Mono'",
           "fonts": GF + "Syne:wght@700;800&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@500"}

REPOS = [
    {"slug": "sable", "name": "sable", "theme": SABLE, "logo": True,
     "tag": "Your server's AI operator.",
     "lines": ["Talk to your server in plain English. Every command previewed,",
               "anything risky gated behind YES, sandboxed sub-agents, skills that learn."],
     "chips": ["Python", "tmux", "bubblewrap", "MCP", "Ollama · OpenAI · Anthropic"],
     "badge": "v1.0"},
    {"slug": "jevbrief", "name": "jevbrief", "theme": JEVBRIEF,
     "tag": "Cleaner state for AI decisions.",
     "lines": ["Trims logs, tool output and web pages down to",
               "what matters before the model decides."],
     "chips": ["TypeScript", "Python", "PyPI"]},
    {"slug": "archon", "name": "Archon", "theme": ARCHON,
     "tag": "Encrypted database backups. Zero code changes.",
     "lines": ["A Docker sidecar: dump, encrypt with AES-256, checksum with SHA-256,",
               "upload, prune. One POST /restore call to bring it back."],
     "chips": ["Python", "Docker", "Postgres", "MongoDB", "MySQL", "SQLite"]},
    {"slug": "veritaschain", "name": "VeritasChain", "theme": VERITAS,
     "tag": "Hash it. Anchor it. Prove it.",
     "lines": ["Pin a file to IPFS and anchor its fingerprint on Ethereum.",
               "Change one pixel and the proof fails. Verify with no account."],
     "chips": ["React 19", "FastAPI", "Solidity", "IPFS", "Ethereum"]},
]


def page(r):
    t = r["theme"]
    logo = ""
    if r.get("logo"):
        with open(os.path.join(OUT, "sable-logo.svg"), encoding="utf-8") as f:
            logo = f'<div class="logo">{f.read()}</div>'
    badge = f'<span class="badge">{r["badge"]}</span>' if r.get("badge") else ""
    chips = "".join(f"<span>{html.escape(c)}</span>" for c in r["chips"])
    lines = "<br>".join(html.escape(l) for l in r["lines"])
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{t['fonts']}&display=block"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1280px;height:640px;overflow:hidden}}
body{{background:radial-gradient(820px 520px at 88% 12%,{t['acc']}26,transparent 62%),linear-gradient(160deg,{t['surf']},{t['bg']} 70%);
font-family:{t['body']},system-ui,sans-serif;color:#ECEBF0;position:relative}}
.grid{{position:absolute;inset:0;background-image:linear-gradient({t['acc']}12 1px,transparent 1px),linear-gradient(90deg,{t['acc']}12 1px,transparent 1px);background-size:48px 48px;
mask-image:linear-gradient(to bottom,transparent 10%,#000 85%)}}
.bar{{position:absolute;left:0;top:0;bottom:0;width:8px;background:linear-gradient({t['ink']},{t['acc']})}}
.wrap{{position:absolute;inset:72px 80px 64px 88px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:28px}}
.logo svg{{width:120px;height:120px;display:block}}
h1{{font-family:{t['display']},system-ui,sans-serif;font-size:100px;font-weight:800;letter-spacing:-2px;line-height:1}}
.badge{{font:500 22px {t['mono']},monospace;color:{t['ok']};border:2px solid {t['ok']}66;border-radius:999px;padding:6px 16px;margin-left:16px;vertical-align:middle;letter-spacing:0}}
.tag{{margin-top:30px;font-family:{t['display']},system-ui,sans-serif;font-size:42px;color:{t['ink']};font-weight:700;letter-spacing:-.5px}}
.lines{{margin-top:20px;font-size:27px;line-height:1.5;color:#B9B8C2}}
.foot{{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;gap:24px}}
.chips{{display:flex;gap:12px;flex-wrap:wrap;max-width:860px}}
.chips span{{font:500 20px {t['mono']},monospace;color:{t['ink']};background:{t['acc']}14;border:1px solid {t['acc']}55;border-radius:8px;padding:8px 14px}}
.who{{font:20px {t['mono']},monospace;color:#8b8a96;text-align:right;white-space:nowrap}}
.who b{{color:#ECEBF0;font-weight:500}}
.dot{{display:inline-block;width:12px;height:12px;border-radius:50%;background:{t['ok']};margin-right:8px}}
</style></head><body><div class="grid"></div><div class="bar"></div><div class="wrap">
<div class="top">{logo}<h1>{html.escape(r['name'])}{badge}</h1></div>
<div class="tag">{html.escape(r['tag'])}</div>
<div class="lines">{lines}</div>
<div class="foot"><div class="chips">{chips}</div>
<div class="who"><span class="dot"></span>github.com/<b>Parthkomalwad</b><br>parthkomalwad.dev</div></div>
</div></body></html>"""


def card_page(r):
    """Profile README card: shared type for a consistent grid, brand colour only."""
    t = r["theme"]
    logo = ""
    if r.get("logo"):
        with open(os.path.join(OUT, "sable-logo.svg"), encoding="utf-8") as f:
            logo = f'<div class="logo">{f.read()}</div>'
    badge = f'<span class="badge">{r["badge"]}</span>' if r.get("badge") else ""
    chips = "".join(f"<span>{html.escape(c)}</span>" for c in r["chips"][:4])
    desc = html.escape(" ".join(r["lines"]))
    return f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;700;800&family=JetBrains+Mono:wght@500&display=block"><style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1000px;height:560px;overflow:hidden;background:transparent}}
.c{{position:absolute;inset:0;border-radius:28px;overflow:hidden;border:2px solid {t['acc']}40;
background:radial-gradient(600px 380px at 92% 0%,{t['acc']}30,transparent 65%),linear-gradient(165deg,{t['surf']},{t['bg']});
font-family:'Geist',system-ui,sans-serif;color:#EEEDF2;padding:56px 60px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:22px}}
.logo svg{{width:84px;height:84px;display:block}}
h1{{font-size:76px;font-weight:800;letter-spacing:-2px;line-height:1}}
.badge{{font:500 20px 'JetBrains Mono',monospace;color:{t['ok']};border:2px solid {t['ok']}66;border-radius:999px;padding:5px 14px;margin-left:14px;vertical-align:middle;letter-spacing:0}}
.tag{{margin-top:26px;font-size:36px;font-weight:700;color:{t['ink']};letter-spacing:-.5px;line-height:1.2}}
.d{{margin-top:16px;font-size:26px;line-height:1.45;color:#B4B3BE}}
.chips{{margin-top:auto;display:flex;gap:10px;flex-wrap:wrap}}
.chips span{{font:500 21px 'JetBrains Mono',monospace;color:{t['ink']};background:{t['acc']}18;border:1px solid {t['acc']}50;border-radius:8px;padding:7px 13px}}
.go{{position:absolute;right:56px;bottom:56px;font-size:24px;font-weight:700;color:{t['ink']}}}
</style></head><body><div class="c">
<div class="top">{logo}<h1>{html.escape(r['name'])}{badge}</h1></div>
<div class="tag">{html.escape(r['tag'])}</div>
<div class="d">{desc}</div>
<div class="chips">{chips}</div>
<div class="go">View &rarr;</div>
</div></body></html>"""


def chrome():
    for c in CHROME_CANDIDATES:
        if os.path.isfile(c) or shutil.which(c):
            return c
    raise SystemExit("Chrome or Edge not found")


def shoot(exe, html_text, png, w, h, tmp, transparent=False):
    src = os.path.join(tmp, os.path.basename(png) + ".html")
    with open(src, "w", encoding="utf-8") as f:
        f.write(html_text)
    args = [exe, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
            "--virtual-time-budget=5000", f"--screenshot={png}"]
    if transparent:
        args.append("--default-background-color=00000000")
    subprocess.run(args + ["file:///" + src.replace("\\", "/")], check=True, capture_output=True)
    print("wrote", png)


def main():
    exe = chrome()
    tmp = tempfile.mkdtemp()
    for r in REPOS:
        shoot(exe, page(r), os.path.join(OUT, r["slug"] + ".png"), 1280, 640, tmp)
        shoot(exe, card_page(r), os.path.join(OUT, "card-" + r["slug"] + ".png"), 1000, 560, tmp, transparent=True)


if __name__ == "__main__":
    main()
