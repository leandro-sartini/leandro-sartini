"""Render the live dungeon card from the GitHub contribution calendar.

dungeon.svg: the last year of contributions is a dungeon floor. Every day with commits holds a gem (bigger day, rarer
gem); a summoner walks the floor column by column and collects them, then the run shows FLOOR CLEARED. The HUD on top
derives a level from lifetime contributions, plus the current and best daily streaks.
Usage: GITHUB_TOKEN=... python scripts/profile_cards.py <login> <out_dir>
"""

import json
import math
import os
import sys
import urllib.request
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from pixel import DIM, EMERALD, GOLD, HERO, INK, MANA, RUBY, TEXT, VIOLET, bar, hero_palette, sprite, svg, text, window

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
  }
}"""

TILE, GAP = 14, 3
GEMS = ((1, EMERALD), (4, MANA), (8, VIOLET), (15, GOLD))
WALK_SECONDS = 28
HOLD_SECONDS = 5


def graphql(token, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-cards"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def fetch(login, token):
    """Return (weeks of the last year, lifetime contribution total)."""
    now = datetime.now(UTC).replace(microsecond=0, tzinfo=None)
    year = graphql(
        token, {"login": login, "from": (now - timedelta(days=365)).isoformat() + "Z", "to": now.isoformat() + "Z"}
    )
    weeks = [
        [(d["date"], d["contributionCount"]) for d in w["contributionDays"]]
        for w in year["contributionsCollection"]["contributionCalendar"]["weeks"]
    ]
    created = datetime.fromisoformat(year["createdAt"].replace("Z", ""))
    total, start = 0, created
    while start < now:
        end = min(start + timedelta(days=365), now)
        chunk = graphql(token, {"login": login, "from": start.isoformat() + "Z", "to": end.isoformat() + "Z"})
        total += chunk["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        start = end
    return weeks, total


def streaks(days):
    """Current streak (today may still be empty) and best streak, in days."""
    best = run = 0
    for _, count in days:
        run = run + 1 if count else 0
        best = max(best, run)
    current = 0
    tail = list(days)
    if tail and not tail[-1][1] and tail[-1][0] == date.today().isoformat():
        tail.pop()
    for _, count in reversed(tail):
        if not count:
            break
        current += 1
    return current, best


def level(total):
    lv = min(99, int(math.sqrt(total / 5)))
    floor_xp, next_xp = lv * lv * 5, (lv + 1) * (lv + 1) * 5
    return lv, (total - floor_xp) / (next_xp - floor_xp) if lv < 99 else 1.0


def gem(count):
    color = None
    for threshold, c in GEMS:
        if count >= threshold:
            color = c
    return color


def render(weeks, total):
    days = [d for w in weeks for d in w]
    cols = len(weeks)
    ox, oy = 36, 150
    w = ox * 2 + cols * (TILE + GAP)
    h = oy + 7 * (TILE + GAP) + 64
    lv, ratio = level(total)
    current, best = streaks(days)
    gems_year = sum(1 for _, c in days if c)
    cycle = WALK_SECONDS + HOLD_SECONDS

    body = [window(0, 0, w, h)]
    body.append(text(ox, 50, "BONUS DUNGEON", 26, "h", GOLD))
    body.append(text(w - ox, 50, "FLOOR: LAST 365 DAYS · AUTO-SAVED EVERY 6H", 20, "t", DIM, "end"))
    body.append(text(ox, 92, f"LV {lv}", 26, "h", TEXT))
    body.append(text(ox + 110, 84, "XP", 14, "s", DIM))
    body.append(bar(ox + 140, 70, 260, 18, ratio, GOLD))
    body.append(text(ox + 140, 112, f"{total:,} lifetime contributions", 20, "t", DIM))
    hud = [("GEMS", f"{gems_year}", EMERALD), ("COMBO", f"{current}d", RUBY), ("BEST", f"{best}d", MANA)]
    for i, (label, value, color) in enumerate(hud):
        x = w - ox - (len(hud) - i) * 150 + 20
        body.append(text(x, 78, label, 14, "s", DIM))
        body.append(text(x, 108, value, 28, "h", color))

    # floor tiles, then gems that vanish when the hero walks over them
    path, step = [], 0
    total_steps = sum(len(wk) for wk in weeks)
    for c, week in enumerate(weeks):
        order = range(len(week)) if c % 2 == 0 else reversed(range(len(week)))
        for r in order:
            x, y = ox + c * (TILE + GAP), oy + r * (TILE + GAP)
            body.append(f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" fill="#0d1440"/>')
            body.append(f'<rect x="{x}" y="{y}" width="{TILE}" height="2" fill="#1d2766"/>')
            path.append((x + TILE / 2, y + TILE / 2))
            color = gem(week[r][1])
            if color:
                t = step / total_steps * WALK_SECONDS / cycle
                cx, cy = x + TILE / 2, y + TILE / 2
                body.append(
                    f'<g><path d="M{cx} {cy - 6}L{cx + 5} {cy}L{cx} {cy + 6}L{cx - 5} {cy}Z" fill="{color}" '
                    f'stroke="{INK}" stroke-width="1"/><rect x="{cx - 2}" y="{cy - 3}" width="2" height="2" fill="#fff"/>'
                    f'<animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;{t:.4f};{t + 0.002:.4f};.999;1" '
                    f'dur="{cycle}s" repeatCount="indefinite"/></g>'
                )
            step += 1

    route = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in path)
    walk = WALK_SECONDS / cycle
    hero = sprite(HERO, hero_palette("summoner"), -9, -20, 1.4)
    body.append(
        f'<g>{hero}<animateMotion path="{route}" dur="{cycle}s" keyPoints="0;1;1" keyTimes="0;{walk:.4f};1" '
        'calcMode="linear" repeatCount="indefinite"/></g>'
    )
    banner_w = 560
    by = oy + 7 * (TILE + GAP) / 2 - 34
    cleared = window(w / 2 - banner_w / 2, by, banner_w, 68) + text(
        w / 2, by + 44, f"FLOOR CLEARED · {gems_year} GEMS", 22, "h", GOLD, "middle"
    )
    body.append(
        f'<g opacity="0">{cleared}<animate attributeName="opacity" values="0;0;1;1" '
        f'keyTimes="0;{walk:.4f};{walk + 0.01:.4f};1" dur="{cycle}s" repeatCount="indefinite"/></g>'
    )
    legend_x = ox
    body.append(text(legend_x, h - 22, "GEMS:", 14, "s", DIM))
    for i, (threshold, color) in enumerate(GEMS):
        x = legend_x + 70 + i * 62
        body.append(f'<path d="M{x} {h - 34}L{x + 5} {h - 28}L{x} {h - 22}L{x - 5} {h - 28}Z" fill="{color}"/>')
        body.append(text(x + 10, h - 22, f"{threshold}+", 18, "t", DIM))
    return svg(w, h, "".join(body), f"Contribution dungeon: level {lv}, {gems_year} active days, streak {current}")


def main():
    login, out_dir = sys.argv[1], Path(sys.argv[2])
    weeks, total = fetch(login, os.environ["GITHUB_TOKEN"])
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dungeon.svg").write_text(render(weeks, total), encoding="utf-8")


if __name__ == "__main__":
    main()
