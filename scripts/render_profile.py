
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

INK = "#111111"
PAPER = "#F6F1E7"
PAPER2 = "#FFFDF8"
MUTED = "#6E6A63"
GRID = "#D8D1C4"
BLUE = "#315BFF"
RED = "#FF4438"
YELLOW = "#FFD13B"
GREEN = "#28A745"
PURPLE = "#7656D6"

STYLE = '''
<style>
  .sans { font-family: Inter, "Segoe UI", Arial, sans-serif; }
  .serif { font-family: Georgia, "Times New Roman", serif; }
  .mono { font-family: "SFMono-Regular", Consolas, "Liberation Mono", monospace; }
  .fade { opacity:0; animation:fade .6s ease forwards; }
  .rise { opacity:0; transform:translateY(12px); animation:rise .65s cubic-bezier(.2,.8,.2,1) forwards; }
  .pop { opacity:0; transform:scale(.78); transform-box:fill-box; transform-origin:center; animation:pop .35s ease forwards; }
  .bar { transform:scaleY(0); transform-box:fill-box; transform-origin:bottom; animation:grow .75s cubic-bezier(.2,.8,.2,1) forwards; }
  .line { stroke-dasharray:800; stroke-dashoffset:800; animation:draw 1.1s ease forwards; }
  .pulse { animation:pulse 2.2s ease-in-out infinite; transform-box:fill-box; transform-origin:center; }
  @keyframes fade { to{opacity:1} }
  @keyframes rise { to{opacity:1; transform:translateY(0)} }
  @keyframes pop { to{opacity:1; transform:scale(1)} }
  @keyframes grow { to{transform:scaleY(1)} }
  @keyframes draw { to{stroke-dashoffset:0} }
  @keyframes pulse { 0%,100%{opacity:.35} 50%{opacity:1} }
  @media (prefers-reduced-motion: reduce) {
    .fade,.rise,.pop,.bar,.line,.pulse {
      animation:none!important; opacity:1!important; transform:none!important;
      stroke-dashoffset:0!important;
    }
  }
</style>
'''

def wrap_svg(w, h, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{STYLE}{body}</svg>'

def save(name, content):
    (CARDS / name).write_text(content, encoding="utf-8")

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
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    return {"total": cal["totalContributions"], "days": days}

def stats(data):
    if not data:
        return None
    days = data["days"]
    by_month = defaultdict(int)
    for d in days:
        by_month[d["date"][:7]] += d["contributionCount"]

    active = sum(d["contributionCount"] > 0 for d in days)
    busiest = max(days, key=lambda d: d["contributionCount"])

    counts = {d["date"]: d["contributionCount"] for d in days}
    cur = dt.date.today()
    if counts.get(cur.isoformat(), 0) == 0:
        cur -= dt.timedelta(days=1)
    streak = 0
    while counts.get(cur.isoformat(), 0) > 0:
        streak += 1
        cur -= dt.timedelta(days=1)

    return {
        "total": data["total"],
        "active": active,
        "busiest_count": busiest["contributionCount"],
        "busiest_date": busiest["date"],
        "streak": streak,
        "months": sorted(by_month.items())[-12:],
    }

def hero():
    pts = [(690,70),(770,92),(835,58),(728,138),(812,160),(865,122),(748,204),(842,214)]
    edges = [(0,1),(1,2),(0,3),(1,3),(1,5),(2,5),(3,4),(4,5),(3,6),(4,6),(4,7),(5,7)]
    network = []
    for i,(a,b) in enumerate(edges):
        x1,y1=pts[a]; x2,y2=pts[b]
        network.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{INK}" stroke-width="1.5" opacity=".28" class="line" style="animation-delay:{0.18+i*.035:.2f}s"/>')
    for i,(x,y) in enumerate(pts):
        col = BLUE if i in (1,4) else (YELLOW if i==6 else INK)
        network.append(f'<circle cx="{x}" cy="{y}" r="{6 if i in (1,4) else 4}" fill="{col}" class="pop" style="animation-delay:{0.25+i*.045:.2f}s"/>')

    body = f'''
<rect width="900" height="300" rx="22" fill="{PAPER}"/>
<rect x="1" y="1" width="898" height="298" rx="21" fill="none" stroke="{GRID}"/>

<rect x="38" y="34" width="9" height="9" fill="{BLUE}" class="pop"/>
<text x="58" y="43" fill="{MUTED}" font-size="12" letter-spacing="1.2" class="mono fade" style="animation-delay:.08s">COMPUTER ENGINEERING @ ISEP</text>

<text x="38" y="120" fill="{INK}" font-size="58" class="serif rise" style="animation-delay:.12s">Gustavo</text>
<text x="38" y="178" fill="{INK}" font-size="65" font-style="italic" class="serif rise" style="animation-delay:.22s">Ferreira</text>

<text x="42" y="224" fill="{MUTED}" font-size="17" class="sans rise" style="animation-delay:.32s">Building practical systems across AI, data and cloud -</text>
<text x="42" y="248" fill="{MUTED}" font-size="17" class="sans rise" style="animation-delay:.38s">one project at a time.</text>

<circle cx="44" cy="276" r="5" fill="{GREEN}" class="pulse"/>
<text x="58" y="281" fill="{MUTED}" font-size="12" class="mono fade" style="animation-delay:.48s">OPEN TO A CURRICULAR INTERNSHIP · 2027</text>

{''.join(network)}
<text x="688" y="258" fill="{INK}" opacity=".58" font-size="12" class="mono fade" style="animation-delay:.62s">AI // DATA // CLOUD</text>
'''
    save("hero.svg", wrap_svg(900,300,body))

def contribution_card(data):
    if not data:
        body = f'''
<rect width="900" height="210" rx="22" fill="{PAPER2}"/>
<rect x="1" y="1" width="898" height="208" rx="21" fill="none" stroke="{GRID}"/>
<text x="38" y="50" fill="{INK}" font-size="30" class="serif rise">Every commit, <tspan fill="{BLUE}" font-style="italic">a little further.</tspan></text>
<text x="38" y="95" fill="{MUTED}" font-size="13" class="mono fade" style="animation-delay:.2s">Run the GitHub Action once to load live contribution data.</text>
'''
        save("contributions.svg", wrap_svg(900,210,body))
        return

    days = data["days"]
    by_date = {d["date"]: d["contributionCount"] for d in days}
    first = dt.date.fromisoformat(days[0]["date"])
    last = dt.date.fromisoformat(days[-1]["date"])
    start = first - dt.timedelta(days=(first.weekday()+1)%7)

    weeks=[]
    cur=start
    while cur<=last:
        week=[]
        for _ in range(7):
            week.append((cur,by_date.get(cur.isoformat(),0)))
            cur += dt.timedelta(days=1)
        weeks.append(week)

    maxc=max((c for w in weeks for _,c in w),default=1) or 1
    palette=["#ECE7DC","#C5D2FF","#8EA9FF","#587EFF",BLUE]
    cells=[]
    x0,y0,size,gap=38,92,10,3
    for wi,week in enumerate(weeks[-53:]):
        for di,(date,count) in enumerate(week):
            level=0 if count==0 else min(4,max(1,int((count/maxc)*4)+1))
            x=x0+wi*(size+gap); y=y0+di*(size+gap)
            cells.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="2" fill="{palette[level]}" class="pop" style="animation-delay:{.06+wi*.008+di*.002:.3f}s"/>')

    body=f'''
<rect width="900" height="210" rx="22" fill="{PAPER2}"/>
<rect x="1" y="1" width="898" height="208" rx="21" fill="none" stroke="{GRID}"/>
<text x="38" y="50" fill="{INK}" font-size="30" class="serif rise">Every commit, <tspan fill="{BLUE}" font-style="italic">a little further.</tspan></text>
<text x="862" y="48" text-anchor="end" fill="{MUTED}" font-size="10" letter-spacing="1" class="mono fade">REFRESHED DAILY</text>
{''.join(cells)}
'''
    save("contributions.svg", wrap_svg(900,210,body))

def activity_card(s):
    if not s:
        body=f'''
<rect width="900" height="300" rx="22" fill="{PAPER}"/>
<rect x="1" y="1" width="898" height="298" rx="21" fill="none" stroke="{GRID}"/>
<text x="38" y="52" fill="{MUTED}" font-size="11" letter-spacing="1.2" class="mono">THE LAST 12 MONTHS ON GITHUB</text>
<text x="38" y="112" fill="{INK}" font-size="42" class="serif">Syncing activity...</text>
<text x="38" y="145" fill="{MUTED}" font-size="13" class="sans">Run the workflow once and this card will fill with your real GitHub data.</text>
'''
        save("activity.svg", wrap_svg(900,300,body))
        return

    months=s["months"]; maxv=max((v for _,v in months),default=1) or 1
    chart=[]
    x0=40; gap=52; bw=30; base=257
    for i,(m,v) in enumerate(months):
        h=95*v/maxv if v else 3
        x=x0+i*gap; y=base-h
        label=dt.datetime.strptime(m,"%Y-%m").strftime("%b")
        chart.append(f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{h:.1f}" rx="4" fill="{INK if i != len(months)-1 else BLUE}" class="bar" style="animation-delay:{.18+i*.035:.2f}s"/>')
        chart.append(f'<text x="{x+bw/2}" y="278" text-anchor="middle" fill="{MUTED}" font-size="10" class="mono">{label}</text>')

    body=f'''
<rect width="900" height="300" rx="22" fill="{PAPER}"/>
<rect x="1" y="1" width="898" height="298" rx="21" fill="none" stroke="{GRID}"/>
<text x="38" y="43" fill="{MUTED}" font-size="11" letter-spacing="1.2" class="mono fade">THE LAST 12 MONTHS ON GITHUB</text>
<text x="38" y="103" fill="{INK}" font-size="46" class="serif rise">{s["total"]:,} contributions</text>

<text x="667" y="83" fill="{INK}" font-size="30" class="serif rise" style="animation-delay:.12s">{s["streak"]} days</text>
<text x="667" y="101" fill="{MUTED}" font-size="11" class="sans">current streak</text>
<line x1="667" y1="118" x2="855" y2="118" stroke="{GRID}"/>

<text x="667" y="153" fill="{INK}" font-size="30" class="serif rise" style="animation-delay:.18s">{s["active"]} / 365</text>
<text x="667" y="171" fill="{MUTED}" font-size="11" class="sans">active days</text>
<line x1="667" y1="188" x2="855" y2="188" stroke="{GRID}"/>

<text x="667" y="223" fill="{INK}" font-size="30" class="serif rise" style="animation-delay:.24s">{s["busiest_count"]}</text>
<text x="667" y="241" fill="{MUTED}" font-size="11" class="sans">on the busiest day</text>

{''.join(chart)}
'''
    save("activity.svg", wrap_svg(900,300,body))

def area_card(filename, kicker, title, subtitle, accent, text_color="#111111"):
    body=f'''
<rect width="300" height="190" rx="20" fill="{accent}"/>
<text x="22" y="34" fill="{text_color}" font-size="10" letter-spacing="1.1" font-weight="700" class="mono fade">{escape(kicker)}</text>
<text x="22" y="89" fill="{text_color}" font-size="31" class="serif rise">{escape(title)}</text>
<text x="22" y="125" fill="{text_color}" opacity=".78" font-size="13" class="sans rise" style="animation-delay:.12s">{escape(subtitle)}</text>
<text x="258" y="35" fill="{text_color}" font-size="19" font-weight="700" class="sans">→</text>
'''
    save(filename, wrap_svg(300,190,body))

def project_card(filename, title, l1, l2, stack, accent):
    body=f'''
<rect width="300" height="205" rx="20" fill="{PAPER2}"/>
<rect x="1" y="1" width="298" height="203" rx="19" fill="none" stroke="{GRID}"/>
<rect x="20" y="22" width="7" height="7" fill="{accent}" class="pop"/>
<text x="37" y="30" fill="{MUTED}" font-size="10" letter-spacing=".8" class="mono">PROJECT</text>
<text x="20" y="76" fill="{INK}" font-size="22" font-weight="700" class="sans rise">{escape(title)}</text>
<text x="20" y="112" fill="{MUTED}" font-size="13" class="sans rise" style="animation-delay:.10s">{escape(l1)}</text>
<text x="20" y="132" fill="{MUTED}" font-size="13" class="sans rise" style="animation-delay:.14s">{escape(l2)}</text>
<text x="20" y="178" fill="{INK}" opacity=".72" font-size="11" class="mono fade" style="animation-delay:.22s">{escape(stack)}</text>
'''
    save(filename, wrap_svg(300,205,body))

def main():
    hero()
    try:
        data = fetch_contributions()
    except Exception as exc:
        print(f"Contribution fetch failed: {exc}")
        data = None

    contribution_card(data)
    activity_card(stats(data))

    area_card("area-ai.svg","EXPLORE","AI Engineering","RAG · ML · intelligent systems",BLUE,"#FFFFFF")
    area_card("area-data.svg","BUILD","Data Engineering","Pipelines · SQL · analytics",RED,"#FFFFFF")
    area_card("area-systems.svg","FOUNDATION","Cloud & Systems","Networking · infra · automation",YELLOW,INK)

    project_card("project-rag.svg","CCNA AI Assistant","RAG assistant grounded in","CCNA study materials","Python · RAG · Embeddings",BLUE)
    project_card("project-weather.svg","Weather Data Pipeline","API ingestion → validation →","Parquet → DuckDB analytics","Python · SQL · DuckDB",GREEN)
    project_card("project-bank.svg","Bank Marketing ML","Leakage-aware classification","with threshold tuning","Python · scikit-learn · Pandas",PURPLE)

    print("Profile cards rendered.")

if __name__ == "__main__":
    main()
