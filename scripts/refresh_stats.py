"""Refresh repository-hosted stat cards; leave the last snapshot on fetch failure."""

from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json
import subprocess
import xml.etree.ElementTree as ET


ASSETS = Path(__file__).resolve().parents[1] / "assets"
SVG = "{http://www.w3.org/2000/svg}"
COLORS = {
    "light": ("edf5f0", "183c30", "24785d"),
    "dark": ("142c25", "edf7f0", "90d5b3"),
}


def card_urls():
    for theme, (background, text, accent) in COLORS.items():
        streak = {
            "user": "Princeu3", "hide_border": "true", "border_radius": 12,
            "background": background, "stroke": background,
            "ring": accent, "fire": accent, "currStreakNum": text,
            "sideNums": text, "currStreakLabel": accent, "sideLabels": text,
            "dates": text, "timezone": "America/New_York",
            "disable_animations": "true",
        }
        yield f"streak-{theme}.svg", "https://streak-stats.demolab.com/?" + urlencode(streak), "Current Streak"


def contribution_days():
    query = 'query { user(login:"Princeu3") { contributionsCollection { contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }'
    result = json.loads(subprocess.check_output(["gh", "api", "graphql", "-f", "query=" + query], text=True))
    weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    counts = {day["date"]: day["contributionCount"] for week in weeks for day in week["contributionDays"]}
    today = datetime.now(ZoneInfo("America/New_York")).date()
    dates = [today - timedelta(days=offset) for offset in reversed(range(31))]
    return [(day.isoformat(), counts[day.isoformat()]) for day in dates]


def activity_svg(days, theme):
    background, text, accent = COLORS[theme]
    total = sum(count for _, count in days)
    maximum = max(1, *(count for _, count in days))
    bars = []
    for index, (day, count) in enumerate(days):
        height = max(2, count / maximum * 130)
        bars.append(f'<rect x="{32 + index * 20.5:.1f}" y="{248 - height:.1f}" width="14" height="{height:.1f}" rx="3" fill="#{accent}" opacity="{1 if count else 0.2}"><title>{day}: {count} contributions</title></rect>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="700" height="300" viewBox="0 0 700 300" role="img" aria-labelledby="title desc">
<title id="title">{total:,} GitHub contributions in the last 31 days</title>
<desc id="desc">Daily contributions from {days[0][0]} through {days[-1][0]}. Tallest bar: {maximum if total else 0} contributions.</desc>
<rect width="700" height="300" rx="12" fill="#{background}"/>
<g font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" fill="#{text}">
<text x="32" y="56" font-size="40" font-weight="700">{total:,} contributions</text>
<text x="32" y="88" font-size="22">Last 31 days · {sum(count > 0 for _, count in days)} active days</text>
{''.join(bars)}
<text x="32" y="281" font-size="20">{days[0][0]}</text>
<text x="660" y="281" text-anchor="end" font-size="20">{days[-1][0]}</text>
</g></svg>'''.encode()


def validate_svg(data, expected):
    root = ET.fromstring(data)
    if root.tag != SVG + "svg" or expected not in " ".join(root.itertext()):
        raise ValueError("Provider did not return the expected stats SVG")
    for element in root.iter():
        if element.tag in {SVG + "script", SVG + "foreignObject", SVG + "image"}:
            raise ValueError("Stats SVG contains active or external content")
        if any(key.lower().startswith("on") for key in element.attrib):
            raise ValueError("Stats SVG contains an event handler")
    if b"@import" in data or b"url(http" in data:
        raise ValueError("Stats SVG contains an external stylesheet or font")
    return data


def download(url):
    request = Request(url, headers={"User-Agent": "Princeu3-profile-stats"})
    with urlopen(request, timeout=45) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise ValueError("Stats SVG exceeds 2 MB")
    return data


def refresh(destination=ASSETS):
    # Fetch and validate every card before replacing any last-known-good snapshot.
    cards = {name: validate_svg(download(url), expected) for name, url, expected in card_urls()}
    days = contribution_days()
    cards.update({f"activity-{theme}.svg": validate_svg(activity_svg(days, theme), "contributions") for theme in COLORS})
    destination.mkdir(parents=True, exist_ok=True)
    for name, data in cards.items():
        temporary = destination / (name + ".tmp")
        temporary.write_bytes(data)
        temporary.replace(destination / name)
        print(f"Updated {name}")


if __name__ == "__main__":
    refresh()
