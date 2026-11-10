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

BG = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#f0f6fc"
MUTED = "#8b949e"
BLUE = "#58a6ff"
GREEN = "#3fb950"
PURPLE = "#a371f7"
ORANGE = "#d29922"

BASE_STYLE = """
<style>
  text { font-family: Inter, \"Segoe UI\", Arial, sans-serif; }
  .fade { opacity: 0; animation: fade .65s ease forwards; }
  .rise { opacity: 0; transform: translateY(12px); animation: rise .7s cubic-bezier(.2,.8,.2,1) forwards; }
  .bar { transform-box: fill-box; transform-origin: bottom; transform: scaleY(0); animation: grow .7s cubic-bezier(.2,.8,.2,1) forwards; }
  .cell { opacity: 0; transform-box: fill-box; transform-origin: center; transform: scale(.55); animation: pop .28s ease forwards; }
  .pulse { animation: pulse 2.2s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }
  @keyframes fade { to { opacity: 1; } }
  @keyframes rise { to { opacity: 1; transform: translateY(0); } }
  @keyframes grow { to { transform: scaleY(1); } }
  @keyframes pop { to { opacity: 1; transform: scale(1); } }
  @keyframes pulse { 0%,100%{opacity:.55} 50%{opacity:1} }
  @media (prefers-reduced-motion: reduce) {
    .fade,.rise,.bar,.cell,.pulse {
      animation: none !important;
      opacity: 1 !important;
      transform: none !important;
    }
  }
</style>
"""


def svg(width: int, height: int, body: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
{BASE_STYLE}
{body}
</svg>'''


def save(name: str, content: str) -> None:
    (CARDS / name).write_text(content, encoding="utf-8")


def fetch_contributions():
    if not TOKEN:
        return None
    query = """
    query($login:String!) {
      user(login:$login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
              }
            }
          }
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": USERNAME}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "profile-readme-renderer",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if data.get("errors"):
        raise RuntimeError(data["errors"])
    calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in calendar["weeks"]:
        days.extend(week["contributionDays"])
    return {"total": calendar["totalContributions"], "days": days}


def fallback_data():
    today = dt.date.today()
    days = []
    for i in range(365):
        d = today - dt.timedelta(days=364-i)
        days.append({"date": d.isoformat(), "contributionCount": 0})
    return {"total": 0, "days": days}


def stats(data):
    days = data["days"]
    active = sum(1 for d in days if d["contributionCount"] > 0)
    busiest = max(days, key=lambda d: d["contributionCount"], default={"date":"—","contributionCount":0})
    by_month = defaultdict(int)
    for d in days:
        by_month[d["date"][:7]] += d["contributionCount"]

    counts = {d["date"]: d["contributionCount"] for d in days}
    cur = dt.date.today()
    if counts.get(cur.isoformat(), 0) == 0:
        cur -= dt.timedelta(days=1)
    streak = 0
    while counts.get(cur.isoformat(), 0) > 0:
        streak += 1
        cur -= dt.timedelta(days=1)

    months = sorted(by_month.items())[-12:]
    return {
        "total": data["total"],
        "active": active,
        "busiest_date": busiest["date"],
        "busiest_count": busiest["contributionCount"],
        "streak": streak,
        "months": months,
    }


def render_hero():
    body = f'''
<rect width="900" height="230" rx="22" fill="{BG}"/>
<rect x="1" y="1" width="898" height="228" rx="21" fill="none" stroke="{BORDER}"/>
<circle cx="55" cy="48" r="7" fill="{GREEN}" class="pulse"/>
<text x="76" y="55" fill="{MUTED}" font-size="18" class="fade" style="animation-delay:.10s">available for a curricular internship · 2027</text>
<text x="46" y="116" fill="{TEXT}" font-size="44" font-weight="700" class="rise" style="animation-delay:.15s">Gustavo Ferreira</text>
<text x="48" y="151" fill="{BLUE}" font-size="22" font-weight="600" class="rise" style="animation-delay:.28s">Computer Engineering @ ISEP</text>
<text x="48" y="187" fill="{MUTED}" font-size="18" class="rise" style="animation-delay:.40s">Exploring AI/ML · Data Engineering · Cloud &amp; Systems</text>
'''
    save("hero.svg", svg(900, 230, body))


def render_area(name, title, subtitle, accent, delay):
    body = f'''
<rect width="300" height="180" rx="20" fill="{PANEL}"/>
<rect x="1" y="1" width="298" height="178" rx="19" fill="none" stroke="{BORDER}"/>
<rect x="22" y="23" width="42" height="6" rx="3" fill="{accent}" class="rise" style="animation-delay:{delay}s"/>
<text x="22" y="72" fill="{TEXT}" font-size="26" font-weight="700" class="rise" style="animation-delay:{delay+0.08}s">{escape(title)}</text>
<text x="22" y="105" fill="{MUTED}" font-size="15" class="rise" style="animation-delay:{delay+0.16}s">{escape(subtitle)}</text>
<text x="22" y="148" fill="{accent}" font-size="14" font-weight="600" class="fade" style="animation-delay:{delay+0.28}s">VIEW PROJECT →</text>
'''
    save(name, svg(300, 180, body))


def render_project(name, title, line1, line2, stack, accent, delay):
    body = f'''
<rect width="300" height="210" rx="20" fill="{PANEL}"/>
<rect x="1" y="1" width="298" height="208" rx="19" fill="none" stroke="{BORDER}"/>
<circle cx="25" cy="28" r="5" fill="{accent}" class="pulse"/>
<text x="40" y="34" fill="{MUTED}" font-size="12" font-weight="600" class="fade" style="animation-delay:{delay}s">FEATURED PROJECT</text>
<text x="22" y="76" fill="{TEXT}" font-size="21" font-weight="700" class="rise" style="animation-delay:{delay+0.08}s">{escape(title)}</text>
<text x="22" y="111" fill="{MUTED}" font-size="14" class="rise" style="animation-delay:{delay+0.16}s">{escape(line1)}</text>
<text x="22" y="133" fill="{MUTED}" font-size="14" class="rise" style="animation-delay:{delay+0.16}s">{escape(line2)}</text>
<text x="22" y="176" fill="{accent}" font-size="13" font-weight="600" class="fade" style="animation-delay:{delay+0.30}s">{escape(stack)}</text>
'''
    save(name, svg(300, 210, body))


def render_activity(s):
    months = s["months"]
    max_v = max((v for _,v in months), default=1) or 1
    chart = []
    start_x = 48
    base_y = 205
    gap = 62
    bar_w = 32
    for i, (month, value) in enumerate(months):
        h = 92 * value / max_v if value else 3
        x = start_x + i * gap
        y = base_y - h
        label = dt.datetime.strptime(month, "%Y-%m").strftime("%b")
        chart.append(f'<rect class="bar" style="animation-delay:{0.22+i*0.035:.2f}s" x="{x}" y="{y:.1f}" width="{bar_w}" height="{h:.1f}" rx="5" fill="{BLUE}" opacity=".85"/>')
        chart.append(f'<text x="{x+bar_w/2}" y="228" text-anchor="middle" fill="{MUTED}" font-size="11">{label}</text>')
    body = f'''
<rect width="900" height="260" rx="22" fill="{BG}"/>
<rect x="1" y="1" width="898" height="258" rx="21" fill="none" stroke="{BORDER}"/>
<text x="36" y="43" fill="{TEXT}" font-size="21" font-weight="700" class="rise">Activity · last 12 months</text>
<text x="36" y="82" fill="{BLUE}" font-size="28" font-weight="700" class="rise" style="animation-delay:.08s">{s["total"]}</text>
<text x="36" y="102" fill="{MUTED}" font-size="12">contributions</text>
<text x="184" y="82" fill="{GREEN}" font-size="28" font-weight="700" class="rise" style="animation-delay:.12s">{s["streak"]}</text>
<text x="184" y="102" fill="{MUTED}" font-size="12">day streak</text>
<text x="312" y="82" fill="{PURPLE}" font-size="28" font-weight="700" class="rise" style="animation-delay:.16s">{s["active"]}</text>
<text x="312" y="102" fill="{MUTED}" font-size="12">active days</text>
<text x="452" y="82" fill="{ORANGE}" font-size="28" font-weight="700" class="rise" style="animation-delay:.20s">{s["busiest_count"]}</text>
<text x="452" y="102" fill="{MUTED}" font-size="12">busiest day · {escape(s["busiest_date"])}</text>
{''.join(chart)}
'''
    save("activity.svg", svg(900, 260, body))


def render_contributions(data):
    days = data["days"]
    by_date = {d["date"]: d["contributionCount"] for d in days}
    first = dt.date.fromisoformat(days[0]["date"])
    last = dt.date.fromisoformat(days[-1]["date"])
    start = first - dt.timedelta(days=(first.weekday()+1) % 7)
    weeks = []
    cur = start
    while cur <= last:
        week = []
        for _ in range(7):
            week.append((cur, by_date.get(cur.isoformat(), 0)))
            cur += dt.timedelta(days=1)
        weeks.append(week)

    max_count = max((c for w in weeks for _,c in w), default=1) or 1
    palette = ["#21262d", "#0e4429", "#006d32", "#26a641", "#39d353"]
    cells = []
    x0, y0, size, gap = 36, 72, 11, 3
    for wi, week in enumerate(weeks[-53:]):
        for di, (_, count) in enumerate(week):
            if count <= 0:
                level = 0
            else:
                ratio = count / max_count
                level = min(4, max(1, int(ratio*4)+1))
            x = x0 + wi*(size+gap)
            y = y0 + di*(size+gap)
            delay = 0.08 + wi*0.012 + di*0.004
            cells.append(f'<rect class="cell" style="animation-delay:{delay:.3f}s" x="{x}" y="{y}" width="{size}" height="{size}" rx="2" fill="{palette[level]}"/>')
    body = f'''
<rect width="900" height="205" rx="22" fill="{BG}"/>
<rect x="1" y="1" width="898" height="203" rx="21" fill="none" stroke="{BORDER}"/>
<text x="36" y="42" fill="{TEXT}" font-size="21" font-weight="700" class="rise">Contribution graph</text>
<text x="864" y="42" text-anchor="end" fill="{MUTED}" font-size="12" class="fade" style="animation-delay:.12s">updated daily</text>
{''.join(cells)}
'''
    save("contributions.svg", svg(900, 205, body))


def main():
    render_hero()
    render_area("ai.svg", "AI / ML", "Models, evaluation & RAG", BLUE, .15)
    render_area("data.svg", "Data", "ETL, SQL & analytics", GREEN, .22)
    render_area("systems.svg", "Systems", "Architecture, networking & C", PURPLE, .29)

    render_project("project-bank.svg", "Bank Marketing ML", "Leakage-aware classification", "with threshold tuning", "Python · scikit-learn", BLUE, .12)
    render_project("project-weather.svg", "Weather Data Pipeline", "API → validation → Parquet", "→ DuckDB analytics", "Python · SQL · DuckDB", GREEN, .18)
    render_project("project-flight.svg", "Flight Management", "DDD, ANTLR DSL & JPA", "plus concurrent C simulation", "Java · C · ANTLR", PURPLE, .24)

    try:
        data = fetch_contributions() or fallback_data()
    except Exception as exc:
        print(f"Warning: contribution fetch failed: {exc}")
        data = fallback_data()

    s = stats(data)
    render_contributions(data)
    render_activity(s)
    print("Profile cards rendered.")


if __name__ == "__main__":
    main()
