import html, os, random, sys

random.seed(7)
FONT = 'font-family="Segoe UI, -apple-system, BlinkMacSystemFont, Helvetica, Arial, sans-serif"'
MONO = 'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"'
RM = '@media (prefers-reduced-motion: reduce){*{animation:none!important}}'
ACC = "#38bdf8"

# ---------- HERO: pseudo-3D orbiting agent sphere ----------
W, H = 1200, 340
cx, cy, R = 920, 170, 125
tilts = [(-20, .32, 9), (35, .45, 12), (80, .28, 10), (-60, .5, 14), (10, .9, 16)]
cols = ["#38bdf8", "#a78bfa", "#7ee787"]
orb = []
for k, (rot, ry, dur) in enumerate(tilts):
    ryv = R * ry
    path = f"M{R},0 A{R},{ryv:.1f} 0 1,1 {-R},0 A{R},{ryv:.1f} 0 1,1 {R},0"
    g = f'<g transform="translate({cx},{cy}) rotate({rot})">'
    g += f'<ellipse rx="{R}" ry="{ryv:.1f}" fill="none" stroke="{ACC}" stroke-opacity=".18"/>'
    for j in range(3):
        b = f"{-dur * j / 3:.2f}s"
        g += (f'<circle r="4" fill="{cols[(k + j) % 3]}">'
              f'<animateMotion dur="{dur}s" begin="{b}" repeatCount="indefinite" path="{path}"/>'
              f'<animate attributeName="r" values="4;7;4;2;4" keyTimes="0;.25;.5;.75;1" dur="{dur}s" begin="{b}" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values=".7;1;.7;.2;.7" keyTimes="0;.25;.5;.75;1" dur="{dur}s" begin="{b}" repeatCount="indefinite"/>'
              '</circle>')
    orb.append(g + '</g>')

stars = ''.join(
    f'<circle cx="{random.randint(0, W)}" cy="{random.randint(0, 230)}" r="{random.choice([.6, .9, 1.2])}" fill="#c9d1d9">'
    f'<animate attributeName="opacity" values=".1;.7;.1" dur="{random.uniform(3, 7):.1f}s" begin="{random.uniform(0, 5):.1f}s" repeatCount="indefinite"/></circle>'
    for _ in range(70))
grid = ''.join(f'<line x1="{x}" y1="236" x2="{600 + (x - 600) * 3}" y2="{H}" stroke="{ACC}" stroke-opacity=".08"/>' for x in range(0, 1201, 60))
grid += ''.join(f'<line x1="0" y1="{y}" x2="{W}" y2="{y}" stroke="{ACC}" stroke-opacity="{.04 + i * .025:.3f}"/>' for i, y in enumerate([240, 252, 268, 290, 318]))

hero = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Parth Komalwad, Senior AI Engineer">
<style>
.nm{{animation:up 1.2s ease-out both}} .sub{{animation:up 1.2s .3s ease-out both}} .tg{{animation:up 1.2s .6s ease-out both}}
@keyframes up{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}
.core{{animation:pulse 3s ease-in-out infinite;transform-origin:{cx}px {cy}px}}
@keyframes pulse{{50%{{transform:scale(1.15);opacity:.75}}}}
{RM}
</style>
<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080f"/><stop offset="1" stop-color="#0b1424"/></linearGradient>
<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-600" x2="0" y1="0" y2="0">
<stop offset="0" stop-color="#e6edf3"/><stop offset=".42" stop-color="#e6edf3"/><stop offset=".5" stop-color="#7dd3fc"/><stop offset=".58" stop-color="#e6edf3"/><stop offset="1" stop-color="#e6edf3"/>
<animate attributeName="x1" values="-600;700;700" keyTimes="0;.5;1" dur="6s" repeatCount="indefinite"/>
<animate attributeName="x2" values="0;1300;1300" keyTimes="0;.5;1" dur="6s" repeatCount="indefinite"/>
</linearGradient>
<radialGradient id="glow"><stop offset="0" stop-color="{ACC}" stop-opacity=".55"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="url(#bg)"/>
{grid}{stars}
<circle cx="{cx}" cy="{cy}" r="160" fill="url(#glow)" opacity=".35"/>
{''.join(orb)}
<g class="core"><circle cx="{cx}" cy="{cy}" r="17" fill="{ACC}" opacity=".9"/><circle cx="{cx}" cy="{cy}" r="29" fill="none" stroke="{ACC}" stroke-opacity=".5"/></g>
<g {FONT}>
<text class="nm" x="70" y="150" font-size="58" font-weight="700" letter-spacing="3" fill="url(#shine)">PARTH KOMALWAD</text>
<text class="sub" x="72" y="192" font-size="17" letter-spacing="8" fill="{ACC}">SENIOR AI ENGINEER</text>
<text class="tg" x="72" y="230" {MONO} font-size="15" fill="#8b949e">agents · retrieval · nl2sql · mcp  /  Pune, India</text>
</g>
</svg>'''


def header(label, idx):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="64" viewBox="0 0 900 64" role="img" aria-label="{label}">
<style>.u{{animation:sw 4s ease-in-out infinite}}@keyframes sw{{0%{{transform:translateX(-160px)}}100%{{transform:translateX(900px)}}}}{RM}</style>
<defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{ACC}" stop-opacity="0"/><stop offset=".5" stop-color="{ACC}"/><stop offset="1" stop-color="{ACC}" stop-opacity="0"/></linearGradient></defs>
<text x="0" y="37" {MONO} font-size="13" fill="{ACC}">{idx}</text>
<text x="40" y="38" {FONT} font-size="24" font-weight="700" letter-spacing="5" fill="#8b949e">{label}</text>
<rect x="0" y="54" width="900" height="1" fill="#30363d"/>
<rect class="u" x="0" y="53" width="160" height="3" fill="url(#l)"/>
</svg>'''


def card(name, tagline, lines, stack, w, h, flag=False):
    per = 2 * (w + h) - 8
    y0 = 118 if flag else 94
    fs = 15 if flag else 13
    body = ''.join(f'<text x="28" y="{y0 + i * 22}" {FONT} font-size="{fs}" fill="#c9d1d9">{html.escape(l)}</text>' for i, l in enumerate(lines))
    badge = (f'<rect x="{w - 128}" y="26" width="100" height="24" rx="12" fill="#0f2a3b" stroke="{ACC}" stroke-opacity=".5"/>'
             f'<text x="{w - 78}" y="42" text-anchor="middle" {MONO} font-size="11" fill="{ACC}">FLAGSHIP</text>') if flag else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{name}: {html.escape(tagline)}">
<style>.run{{stroke-dasharray:160 {per - 160};animation:run 6s linear infinite}}@keyframes run{{to{{stroke-dashoffset:-{per}}}}}
.go{{animation:go 2s ease-in-out infinite}}@keyframes go{{50%{{transform:translateX(5px)}}}}{RM}</style>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#111a2b"/><stop offset="1" stop-color="#0b111c"/></linearGradient></defs>
<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="url(#g)" stroke="#30363d"/>
<rect class="run" x="1" y="1" width="{w - 2}" height="{h - 2}" rx="14" fill="none" stroke="{ACC}" stroke-width="2"/>
{badge}
<text x="28" y="{54 if flag else 46}" {FONT} font-size="{30 if flag else 21}" font-weight="700" fill="#e6edf3">{name}</text>
<text x="28" y="{84 if flag else 68}" {FONT} font-size="{16 if flag else 13}" fill="{ACC}">{html.escape(tagline)}</text>
{body}
<text x="28" y="{h - 24}" {MONO} font-size="{12 if flag else 11}" fill="#8b949e">{html.escape(stack)}</text>
<g class="go"><text x="{w - 28}" y="{h - 24}" text-anchor="end" {FONT} font-size="13" font-weight="600" fill="{ACC}">View →</text></g>
</svg>'''


out = {
    'assets/hero.svg': hero,
    'assets/h-projects.svg': header('PROJECTS', '01'),
    'assets/h-stack.svg': header('STACK', '02'),
    'assets/h-activity.svg': header('ACTIVITY', '03'),
    'assets/card-sable.svg': card('Sable', 'The shell that asks first.', [
        'SSH in and type English. Sable plans the work, previews every command,',
        'gates anything destructive behind a typed YES, runs long jobs in',
        'sandboxed sub-agents, and turns repeated work into reusable skills.'],
        'Python · tmux · SQLite · bubblewrap · Claude / OpenAI / Ollama', 900, 250, True),
    'assets/card-jevbrief.svg': card('jevbrief', 'Context trimming for LLMs', [
        'Cuts logs, tool output and web', 'pages down to what matters', 'before the model decides.'],
        'TypeScript · Python', 292, 210),
    'assets/card-archon.svg': card('Archon', 'Backups as a sidecar', [
        'Encrypted, verified DB backups', 'as a drop-in Docker sidecar.', 'AES-256 + SHA-256.'],
        'Python · Docker · Postgres', 292, 210),
    'assets/card-veritaschain.svg': card('VeritasChain', 'On-chain file provenance', [
        'Hash a file, pin it to IPFS,', 'anchor the fingerprint on-chain.', 'No accounts, no storage.'],
        'React · FastAPI · Solidity', 292, 210),
}
root = sys.argv[1]
for k, v in out.items():
    with open(os.path.join(root, k), 'w', encoding='utf-8') as f:
        f.write(v)
print('wrote', len(out))
