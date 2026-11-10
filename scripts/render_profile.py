
from __future__ import annotations
import datetime as dt
import json
import os
import urllib.request
from collections import defaultdict
from html import escape
from pathlib import Path

USERNAME = os.getenv("GITHUB_USERNAME", "GustavoFerreira24")
TOKEN = os.getenv("GITHUB_TOKEN")
ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "cards"
CARDS.mkdir(exist_ok=True)

PAPER = "#f3f0e8"
PAPER_LIGHT = "#fbfaf6"
INK = "#111111"
INK_SOFT = "#44413c"
MUTED = "#77736b"
RULE = "#d8d2c7"
BLUE = "#315BFF"
RED = "#FF4438"
YELLOW = "#FFD13B"
GREEN = "#31A354"

W = 880
BOTTOM = 12
TILE_W, TILE_H = 880 / 3 - 8, 210
REPO_W, REPO_H = 880 / 3 - 8, 190

SERIF = "'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', Palatino, Georgia, serif"
SANS = "'Avenir Next', Avenir, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'SFMono-Regular', Menlo, Monaco, Consolas, 'Liberation Mono', monospace"

BASE_CSS = '''
@keyframes rise{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.3)}70%{opacity:1;transform:scale(1.15)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translateX(4px)}}
@keyframes tilein{
  0%{opacity:0;transform:translateY(70px) scale(.72) rotate(-5deg)}
  55%{opacity:1;transform:translateY(-8px) scale(1.035) rotate(1.2deg)}
  78%{transform:translateY(2px) scale(.99) rotate(-.35deg)}
  100%{opacity:1;transform:none}
}
@keyframes slidein{from{opacity:0;transform:translateX(-22px)}to{opacity:1;transform:none}}
@keyframes arrowin{
  0%{opacity:0;transform:translateX(-24px)}
  65%{opacity:1;transform:translateX(5px)}
  100%{opacity:1;transform:none}
}
@keyframes sheen{
  0%{transform:translateX(-290px) skewX(-20deg)}
  24%,100%{transform:translateX(430px) skewX(-20deg)}
}
@keyframes ring{0%{opacity:.55;transform:scale(.2)}100%{opacity:0;transform:scale(2.15)}}
@keyframes draw{from{stroke-dashoffset:120}to{stroke-dashoffset:0}}

.r{opacity:0;animation:rise .8s cubic-bezier(.2,.7,.2,1) both;transform-box:fill-box}
.f{opacity:0;animation:fade .9s ease-out both}
.g{transform-box:fill-box;transform-origin:bottom;transform:scaleY(0);animation:grow .8s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .4s ease-out both}
.live{animation:pulse 1.7s ease-in-out infinite}
.n{transform-box:fill-box;animation:nudge 1.8s ease-in-out infinite}
.ti{opacity:0;transform-box:fill-box;transform-origin:50% 60%;animation:tilein 1.0s cubic-bezier(.2,.8,.2,1) both}
.sl{opacity:0;transform-box:fill-box;animation:slidein .62s cubic-bezier(.2,.7,.2,1) both}
.ai{opacity:0;transform-box:fill-box;animation:arrowin .7s cubic-bezier(.2,.7,.2,1) both}
.sh{animation:sheen 5.3s ease-in-out infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 1.1s ease-out both}
.rc{opacity:0;transform-box:fill-box;animation:slidein .72s cubic-bezier(.2,.7,.2,1) both}
.edge{stroke-dasharray:120;stroke-dashoffset:120;animation:draw .9s ease forwards}

@media (prefers-reduced-motion: reduce){
  .r,.f,.g,.p,.live,.n,.ti,.sl,.ai,.rg,.rc,.edge{
    animation:none!important;opacity:1!important;transform:none!important;stroke-dashoffset:0!important
  }
  .sh{display:none!important}
}
'''

def svg(w, h, body, label, left=0, right=0, bottom=BOTTOM):
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    ww, hh = w + left + right, h + bottom
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ww:.3f}" height="{hh}" viewBox="0 0 {ww:.3f} {hh}" '
        f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
        f'<style>{BASE_CSS}</style>{body}</svg>'
    )

def save(name, content):
    (CARDS / name).write_text(content, encoding="utf-8")

def d(sec):
    return f'style="animation-delay:{sec:.2f}s"'

def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    if line:
        lines.append(line)
    return lines

def text_lines(x, y, lines, lh, attrs):
    return "".join(
        f'<text x="{x}" y="{y+i*lh}" {attrs}>{escape(line)}</text>'
        for i, line in enumerate(lines)
    )

def fetch_contributions():
    if not TOKEN:
        return None
    query = "query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": USERNAME}}).encode(),
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "profile-readme-renderer",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.load(resp)
    if result.get("errors"):
        raise RuntimeError(result["errors"])
    cal = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [day for week in cal["weeks"] for day in week["contributionDays"]]
    return {"total": cal["totalContributions"], "days": days}

def stats(data):
    if not data:
        return None
    by_month = defaultdict(int)
    for day in data["days"]:
        by_month[day["date"][:7]] += day["contributionCount"]
    return {
        "total": data["total"],
        "active": sum(day["contributionCount"] > 0 for day in data["days"]),
        "months": sorted(by_month.items())[-12:],
    }

def hero():
    h = 420
    pts = [(650,92),(742,116),(820,74),(690,172),(792,202),(850,154),(722,258),(825,270)]
    edges = [(0,1),(1,2),(0,3),(1,3),(1,5),(2,5),(3,4),(4,5),(3,6),(4,6),(4,7),(5,7)]
    network = []
    for i,(a,b) in enumerate(edges):
        x1,y1=pts[a]; x2,y2=pts[b]
        network.append(
            f'<line class="edge" style="animation-delay:{.32+i*.045:.3f}s" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{INK}" stroke-width="1.5" opacity=".25"/>'
        )
    for i,(x,y) in enumerate(pts):
        fill = BLUE if i in (1,4) else (YELLOW if i==6 else INK)
        radius = 6 if i in (1,4) else 4
        network.append(f'<circle class="p" {d(.55+i*.05)} cx="{x}" cy="{y}" r="{radius}" fill="{fill}"/>')

    body = f'''
<defs>
  <linearGradient id="nameShine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="600" y2="0">
    <stop offset="0" stop-color="{INK}"/>
    <stop offset=".42" stop-color="{INK}"/>
    <stop offset=".50" stop-color="{BLUE}"/>
    <stop offset=".58" stop-color="{INK}"/>
    <stop offset="1" stop-color="{INK}"/>
    <animateTransform attributeName="gradientTransform" type="translate"
      values="-650 0;650 0;650 0" keyTimes="0;.42;1"
      dur="7s" begin="1.5s" repeatCount="indefinite"/>
  </linearGradient>
</defs>
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<g class="f" {d(0)}>
  <rect class="live" x="48" y="49" width="8" height="8" rx="2" fill="{BLUE}"/>
  <text x="66" y="57" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">COMPUTER ENGINEERING @ ISEP</text>
</g>
<text class="r" {d(.12)} x="44" y="184" font-family="{SERIF}" font-size="104" letter-spacing="-2" fill="{INK}">Gustavo</text>
<text class="r" {d(.26)} x="44" y="282" font-family="{SERIF}" font-style="italic" font-size="108" letter-spacing="-2" fill="url(#nameShine)">Ferreira</text>
<g class="r" {d(.48)}>
  <text x="48" y="330" font-family="{SANS}" font-size="18" fill="{INK_SOFT}">Building practical projects across AI, Data Engineering and Cloud.</text>
</g>
<g class="f" {d(.66)}>
  <circle class="live" cx="51" cy="382" r="6" fill="{GREEN}"/>
  <text x="68" y="388" font-family="{MONO}" font-size="15" font-weight="700" letter-spacing=".7" fill="{INK}">OPEN TO A CURRICULAR INTERNSHIP - 2027</text>
</g>
{''.join(network)}
'''
    save("hero-v4.svg", svg(W,h,body,"Gustavo Ferreira — Computer Engineering at ISEP"))

def activity(s):
    h = 232
    if not s:
        body = f'''
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text x="40" y="48" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text x="38" y="96" font-family="{SERIF}" font-size="40" fill="{INK}">Syncing activity...</text>
'''
        save("activity-v4.svg", svg(W,h,body,"GitHub activity"))
        return

    months = s["months"]
    maxv = max((v for _,v in months), default=1) or 1
    x0, x1, base, maxh, gap = 40, 610, 186, 72, 10
    bw = (x1-x0-gap*(len(months)-1))/len(months)
    bars = []
    best_i = max(range(len(months)), key=lambda i: months[i][1]) if months else 0
    for i,(month,value) in enumerate(months):
        height = max(4, round(value/maxv*maxh))
        x = x0+i*(bw+gap)
        fill = BLUE if i in (best_i, len(months)-1) else INK
        label = dt.datetime.strptime(month,"%Y-%m").strftime("%b")
        bars.append(
            f'<rect class="g" {d(.6+i*.06)} x="{x:.1f}" y="{base-height}" width="{bw:.1f}" height="{height}" rx="4" fill="{fill}"/>'
            f'<text class="f" {d(.65+i*.06)} x="{x+bw/2:.1f}" y="{base+22}" text-anchor="middle" '
            f'font-family="{MONO}" font-size="11" fill="{MUTED}">{label}</text>'
        )

    body = f'''
<rect width="{W}" height="{h}" rx="14" fill="{PAPER}"/>
<text class="f" {d(.12)} x="40" y="48" font-family="{MONO}" font-size="12" letter-spacing="1" fill="{MUTED}">THE LAST 12 MONTHS ON GITHUB</text>
<text class="r" {d(.18)} x="38" y="94" font-family="{SERIF}" font-size="40" fill="{INK}">{s["total"]:,} <tspan font-style="italic">contributions</tspan></text>
<g class="r" {d(.32)}>
  <text x="666" y="92" font-family="{SERIF}" font-size="32" fill="{BLUE}">{s["active"]} <tspan font-style="italic">days</tspan></text>
  <text x="666" y="112" font-family="{SANS}" font-size="12.5" fill="{MUTED}">active in the last year</text>
  <rect x="666" y="128" width="170" height="1" fill="{RULE}"/>
  <text x="666" y="156" font-family="{SERIF}" font-size="22" font-style="italic" fill="{INK}">Projects over</text>
  <text x="666" y="180" font-family="{SERIF}" font-size="22" font-style="italic" fill="{INK}">streaks.</text>
  <text x="666" y="201" font-family="{SANS}" font-size="11.5" fill="{MUTED}">The work matters more</text>
  <text x="666" y="216" font-family="{SANS}" font-size="11.5" fill="{MUTED}">than the counter.</text>
</g>
{''.join(bars)}
'''
    save("activity-v4.svg", svg(W,h,body,f'{s["total"]} GitHub contributions'))

def tile(filename, kicker, line1, line2, blurb, bg, fg, pos, start, arrow=False):
    lines = wrap(blurb, 35)[:3]
    blurbs = "".join(
        f'<text class="r" {d(start+.52+i*.08)} x="24" y="{153+i*19}" font-family="{SANS}" font-size="13.2" fill="{fg}" opacity=".9">{escape(line)}</text>'
        for i,line in enumerate(lines)
    )
    arrow_svg = (
        f'<g class="ai" {d(start+.35)}><text class="n" style="animation-delay:{start+1.15:.2f}s" '
        f'x="250" y="38" font-family="{MONO}" font-size="15" fill="{fg}">→</text></g>'
    ) if arrow else ""
    body = f'''
<defs>
  <clipPath id="tileClip"><rect width="{TILE_W}" height="{TILE_H}" rx="14"/></clipPath>
  <linearGradient id="tileSheen" x1="0" x2="1">
    <stop offset="0" stop-color="#ffffff" stop-opacity="0"/>
    <stop offset=".5" stop-color="#ffffff" stop-opacity=".30"/>
    <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
  </linearGradient>
</defs>
<g class="ti" {d(start)}>
  <g clip-path="url(#tileClip)">
    <rect width="{TILE_W}" height="{TILE_H}" rx="14" fill="{bg}"/>
    <circle class="rg" {d(start+.50)} cx="{TILE_W-42}" cy="{TILE_H-42}" r="54"
      fill="none" stroke="{fg}" stroke-opacity=".45" stroke-width="2"/>
    <rect class="sh" style="animation-delay:{start+1.4:.2f}s" x="0" y="-20"
      width="85" height="{TILE_H+40}" fill="url(#tileSheen)" transform="translate(-290 0)"/>
  </g>
  <text class="sl" {d(start+.22)} x="24" y="38" font-family="{MONO}" font-size="11"
    letter-spacing="1.1" font-weight="700" fill="{fg}">{escape(kicker)}</text>
  {arrow_svg}
  <text class="r" {d(start+.32)} x="22" y="91" font-family="{SERIF}" font-size="39"
    fill="{fg}">{escape(line1)}</text>
  <text class="r" {d(start+.43)} x="22" y="128" font-family="{SERIF}" font-style="italic"
    font-size="39" fill="{fg}">{escape(line2)}</text>
  {blurbs}
</g>
'''
    save(filename, svg(TILE_W,TILE_H,body,f"{kicker}: {line1} {line2}",left=4*pos,right=8-4*pos))

def section_title(slug, plain, italic, theme):
    fg = "#e6edf3" if theme == "dark" else INK
    body = (
        f'<text class="r" {d(.25)} x="2" y="47" font-family="{SERIF}" font-size="35" fill="{fg}">'
        f'{escape(plain)} <tspan font-style="italic">{escape(italic)}</tspan></text>'
    )
    save(f"title-{slug}-{theme}-v4.svg", svg(W,64,body,f"{plain} {italic}",bottom=0))

def project_card(filename, title, desc, tech, color, pos, status, cols=3):
    if cols == 2:
        cw, left, right, chars, max_lines = W/2 - 6, 6*pos, 6 - 6*pos, 58, 2
    else:
        cw, left, right, chars, max_lines = REPO_W, 4*pos, 8 - 4*pos, 36, 3
    lines = wrap(desc, chars)[:max_lines]
    # Space below the description is based on max_lines, so cards in a row keep the same height.
    rule_y = max(154, 107 + (max_lines - 1) * 20 + 24)
    tech_y = rule_y + 20
    ch = max(REPO_H, tech_y + 16)
    body = f'''
<rect width="{cw}" height="{ch}" rx="14" fill="{PAPER_LIGHT}"/>
<g class="rc" {d(.35+pos*.12)}>
  <rect class="p" {d(.52+pos*.12)} x="24" y="28" width="8" height="8" rx="2" fill="{color}"/>
  <text x="40" y="37" font-family="{MONO}" font-size="10.5" letter-spacing=".8" fill="{MUTED}">{escape(status)}</text>
  <text x="24" y="75" font-family="{SANS}" font-weight="700" font-size="19" fill="{INK}">{escape(title)}</text>
  {text_lines(24,107,lines,20,f'font-family="{SANS}" font-size="13.5" fill="{INK_SOFT}"')}
  <line x1="24" y1="{rule_y}" x2="{cw-24}" y2="{rule_y}" stroke="{RULE}" stroke-width="1"/>
  <text x="24" y="{tech_y}" font-family="{MONO}" font-size="11.5" fill="{MUTED}">{escape(tech)}</text>
</g>
'''
    save(filename, svg(cw,ch,body,f"{status}: {title}",left=left,right=right))

def main():
    try:
        data = fetch_contributions()
    except Exception as exc:
        print(f"Contribution fetch failed: {exc}")
        data = None

    hero()
    activity(stats(data))
    tile("academic-v4.svg","BUILD","Academic","Projects",
         "Team engineering at ISEP across software, data, networking and systems.",
         BLUE,"#ffffff",0,.35,arrow=True)
    tile("personal-v4.svg","EXPLORE","Personal","Projects",
         "Self-directed builds: data pipelines, ML models and study tools.",
         RED,"#ffffff",1,.48,arrow=True)
    tile("focus-v4.svg","FOCUS","AI, Data","& Cloud",
         "Career paths explored through real projects rather than theory alone.",
         YELLOW,INK,2,.61)

    for theme in ("dark", "light"):
        section_title("building", "What I'm", "building", theme)
        section_title("selected", "Selected", "work", theme)

    project_card("current-ccna-v4.svg","CCNA AI Assistant",
                 "Study assistant that retrieves grounded answers from CCNA course materials.",
                 "Python · RAG · Embeddings",BLUE,0,"CURRENT PROJECT")
    project_card("current-laprizza-v4.svg","LaPrizza",
                 "Restaurant management platform for catalogue, orders, stock and preparation workflows.",
                 "C# · .NET 8 · DDD",GREEN,1,"CURRENT PROJECT")
    project_card("current-hackathon-v4.svg","Smart Aveiro",
                 "Smart-city challenge turning urban mobility data into useful insights for the city.",
                 "Data · Analytics · Hackathon",YELLOW,2,"UPCOMING HACKATHON")
    project_card("done-weather-v4.svg","Weather Data Pipeline",
                 "ETL pipeline for hourly weather in Porto, Lisbon and Madrid: raw JSON to validated Parquet to SQL analytics.",
                 "Python · pandas · Parquet · DuckDB · pytest",BLUE,0,"COMPLETED",cols=2)
    project_card("done-bank-v4.svg","Bank Marketing ML",
                 "Predicts term-deposit subscriptions with leakage-aware features, model benchmarking and threshold tuning.",
                 "Python · pandas · scikit-learn",RED,1,"COMPLETED",cols=2)
    print("Editorial profile cards rendered.")

if __name__ == "__main__":
    main()
