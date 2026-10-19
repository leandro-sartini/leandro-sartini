"""Render the static profile art (title screen, party, status, trophies) into assets/.

Usage: python scripts/build_assets.py
"""

import random
import textwrap
from pathlib import Path

from pixel import (
    DIM,
    EMERALD,
    FAMILIAR,
    FRAME,
    GOLD,
    HERO,
    INK,
    MANA,
    NIGHT,
    RUBY,
    TEXT,
    VIOLET,
    bar,
    familiar_palette,
    hero_palette,
    shadow_text,
    sprite,
    svg,
    text,
    window,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def stars(width, height, count, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(count):
        x, y = rnd.randrange(width), rnd.randrange(height)
        size = rnd.choice((2, 2, 2, 3, 4))
        dur = rnd.uniform(1.8, 4.5)
        out.append(
            f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="#fff">'
            f'<animate attributeName="opacity" values="1;.15;1" dur="{dur:.1f}s" begin="{rnd.uniform(0, 3):.1f}s" '
            'repeatCount="indefinite"/></rect>'
        )
    return "".join(out)


def skyline(width, base, seed):
    """Pixel mountains and a castle, drawn as stepped columns."""
    rnd = random.Random(seed)
    far, near = [], []
    h = 60
    for x in range(0, width, 12):
        h = max(30, min(110, h + rnd.choice((-12, -6, 0, 6, 12))))
        far.append(f'<rect x="{x}" y="{base - h}" width="12" height="{h}" fill="#141b44"/>')
    h = 30
    for x in range(0, width, 8):
        h = max(14, min(60, h + rnd.choice((-8, -4, 0, 4, 8))))
        near.append(f'<rect x="{x}" y="{base - h}" width="8" height="{h + 40}" fill="#0c1130"/>')
    castle = []
    cx = 930
    for i, (dx, tw, th) in enumerate(((0, 40, 120), (48, 70, 90), (126, 40, 140), (174, 60, 80))):
        x0, y0 = cx + dx, base - th
        castle.append(f'<rect x="{x0}" y="{y0}" width="{tw}" height="{th}" fill="#0a0e26"/>')
        for b in range(0, tw, 10):
            castle.append(f'<rect x="{x0 + b}" y="{y0 - 8}" width="6" height="8" fill="#0a0e26"/>')
        wy = y0 + 24
        castle.append(
            f'<rect x="{x0 + tw // 2 - 3}" y="{wy}" width="6" height="10" fill="{GOLD}">'
            f'<animate attributeName="opacity" values="1;.55;1;.8;1" dur="{2 + i * 0.7:.1f}s" repeatCount="indefinite"/>'
            "</rect>"
        )
    return "".join(far) + "".join(castle) + "".join(near)


def banner():
    w, h = 1200, 400
    body = [f'<rect width="{w}" height="{h}" fill="{NIGHT}"/>']
    body.append(
        '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#070a18"/><stop offset=".7" stop-color="#1a1452"/>'
        '<stop offset="1" stop-color="#3a1d5c"/></linearGradient>'
        '<radialGradient id="glow"><stop offset="0" stop-color="#5ab0ff" stop-opacity=".55"/>'
        '<stop offset="1" stop-color="#5ab0ff" stop-opacity="0"/></radialGradient></defs>'
    )
    body.append(f'<rect width="{w}" height="{h}" fill="url(#sky)"/>')
    body.append(stars(w, 260, 90, 7))
    # moon
    body.append(
        sprite(
            ["..KKKK..", ".KmmmmK.", "KmmMmmmK", "KmmmmmMK", "KmMmmmmK", "KmmmmMmK", ".KmmmmK.", "..KKKK.."],
            {"K": "#20264f", "m": "#fff4cf", "M": "#e8d9a8"},
            1080,
            40,
            8,
        )
    )
    body.append(skyline(w, 340, 3))
    body.append(f'<rect y="340" width="{w}" height="60" fill="#06081a"/>')
    for x in range(0, w, 16):
        body.append(f'<rect x="{x}" y="340" width="8" height="4" fill="#1b2150"/>')

    # the summoner and three agent familiars orbiting
    hx, hy, scale = 120, 152, 8
    body.append(f'<ellipse cx="{hx + 72}" cy="{hy + 182}" rx="90" ry="12" fill="#000" fill-opacity=".45"/>')
    body.append(
        f'<circle cx="{hx + 104}" cy="{hy + 14}" r="70" fill="url(#glow)">'
        '<animate attributeName="r" values="60;78;60" dur="2.4s" repeatCount="indefinite"/></circle>'
    )
    body.append(
        f"<g>{sprite(HERO, hero_palette('summoner'), hx, hy, scale)}"
        '<animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" dur="2.4s" '
        'repeatCount="indefinite"/></g>'
    )
    orbit = f"M {hx + 72 - 150} {hy + 70} a 150 46 0 1 0 300 0 a 150 46 0 1 0 -300 0"
    for i, color in enumerate((MANA, EMERALD, RUBY)):
        body.append(
            f"<g>{sprite(FAMILIAR, familiar_palette(color), -16, -14, 4)}"
            f'<animateMotion path="{orbit}" dur="6s" begin="{-i * 2}s" repeatCount="indefinite"/></g>'
        )

    # title block
    tx = 430
    body.append(text(tx, 104, "- A NEW SAVE FILE HAS BEEN CREATED -", 18, "t", DIM))
    body.append(shadow_text(tx, 170, "LEANDRO", 64))
    body.append(shadow_text(tx, 236, "SARTINI", 64))
    body.append(text(tx, 278, "LEAD AI ENGINEER  ·  SR AI ENGINEER  ·  GAME STUDIO FOUNDER", 15, "s", TEXT))
    body.append(window(tx, 296, 330, 44))
    body.append(
        f"<g>{text(tx + 24, 325, '▶ PRESS START', 18, 'h', GOLD)}"
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.55;.56;1" dur="1.1s" '
        'repeatCount="indefinite"/></g>'
    )
    body.append(text(tx + 220, 325, "LV 99", 18, "h", EMERALD))
    return svg(w, h, "".join(body), "Leandro Sartini, title screen: a summoner with three AI familiars")


PARTY = [
    {
        "cls": "summoner",
        "guild": "RBBR",
        "job": "LEAD AI ENGINEER",
        "title": "AGENT SUMMONER",
        "hp": 0.96,
        "mp": 0.88,
        "skills": "Summon Agent Swarm · Forge Pipelines · Guardrail Ward",
        "lore": "Leads the AI team: agents, data, commerce and the tooling that makes them safe.",
    },
    {
        "cls": "strategist",
        "guild": "SSB",
        "job": "SR AI ENGINEER",
        "title": "AI STRATEGIST",
        "hp": 0.9,
        "mp": 0.94,
        "skills": "Value Oracle · Runbook Codex · MCP Bridge",
        "lore": "Turns enterprise AI ideas into measured, governed, production use cases.",
    },
    {
        "cls": "builder",
        "guild": "INDIE STUDIO",
        "job": "FOUNDER + GAME DEV",
        "title": "WORLD BUILDER",
        "hp": 0.82,
        "mp": 1.0,
        "skills": "Godot Forge · Pixel Conjuring · Bot Playtester",
        "lore": "Building our own game studio. First title: an action roguelite, PC first.",
    },
]


def party():
    w, row_h = 1200, 168
    h = 70 + row_h * len(PARTY) + 16
    body = [window(0, 0, w, h)]
    body.append(text(36, 50, "PARTY", 26, "h", GOLD))
    body.append(text(w - 36, 50, "MULTICLASS · 3 ACTIVE JOBS", 20, "t", DIM, "end"))
    for i, member in enumerate(PARTY):
        y = 70 + i * row_h
        if i:
            body.append(f'<rect x="30" y="{y - 6}" width="{w - 60}" height="2" fill="{FRAME}" fill-opacity=".2"/>')
        body.append(f'<rect x="36" y="{y + 6}" width="132" height="148" rx="6" fill="#000" fill-opacity=".25"/>')
        body.append(sprite(HERO, hero_palette(member["cls"]), 48, y + 14, 6))
        if i == 0:
            body.append(text(26, y + 84, "▶", 20, "h", GOLD))
        x = 196
        body.append(text(x, y + 34, member["title"], 26, "h", TEXT))
        body.append(text(x, y + 62, f"{member['job']}  @  {member['guild']}", 17, "s", GOLD))
        body.append(text(x, y + 92, member["lore"], 22, "t", DIM))
        body.append(text(x, y + 128, "SKILLS", 15, "s", EMERALD))
        body.append(text(x + 80, y + 128, member["skills"], 22, "t", TEXT))
        bx = 900
        body.append(text(bx, y + 34, "LV 99", 20, "h", TEXT))
        body.append(text(bx, y + 70, "HP", 15, "s", TEXT))
        body.append(bar(bx + 40, y + 56, 220, 18, member["hp"], EMERALD))
        body.append(text(bx, y + 104, "MP", 15, "s", TEXT))
        body.append(bar(bx + 40, y + 90, 220, 18, member["mp"], MANA))
        body.append(
            text(bx + 40, y + 134, f"{int(member['hp'] * 999)}/999   {int(member['mp'] * 999)}/999", 20, "t", DIM)
        )
    return svg(w, h, "".join(body), "Party: Agent Summoner at RBBR, AI Strategist at SSB, World Builder at our studio")


STATS = [
    ("AI / LLM ENGINEERING", 99, VIOLET),
    ("AGENT ORCHESTRATION", 97, VIOLET),
    ("DATA ENGINEERING", 95, MANA),
    ("ML + FORECASTING", 92, MANA),
    ("CLOUD (GCP · AWS)", 93, EMERALD),
    ("COMMERCE + ERP", 88, EMERALD),
    ("GAME DEV (GODOT)", 80, GOLD),
    ("LEADERSHIP", 94, RUBY),
]

EQUIPMENT = [
    ("WEAPON", "Claude Code + Claude API"),
    ("SHIELD", "Guardrails as hooks"),
    ("ARMOR", "Python · SQL · TypeScript"),
    ("HELM", "BigQuery · Cloud Run"),
    ("RING", "MCP servers"),
    ("CHARM", "Godot 4 · pixel art"),
]

LANGUAGES = [("PT", 5), ("EN", 5), ("ES", 5), ("DE", 3), ("FR", 2)]


def status():
    w, h = 1200, 470
    body = [window(0, 0, 700, h), window(712, 0, w - 712, h)]
    body.append(text(36, 50, "STATUS", 26, "h", GOLD))
    for i, (name, value, color) in enumerate(STATS):
        y = 92 + i * 44
        body.append(text(36, y + 14, name, 16, "s", TEXT))
        body.append(bar(330, y, 270, 20, value / 100, color))
        body.append(text(664, y + 16, str(value), 24, "t", TEXT, "end"))

    ex = 748
    body.append(text(ex, 50, "EQUIPMENT", 26, "h", GOLD))
    for i, (slot, item) in enumerate(EQUIPMENT):
        y = 96 + i * 38
        body.append(text(ex, y, slot, 15, "s", DIM))
        body.append(text(ex + 96, y, item, 24, "t", TEXT))
    body.append(f'<rect x="{ex}" y="326" width="{w - 712 - 72}" height="2" fill="{FRAME}" fill-opacity=".2"/>')
    body.append(text(ex, 364, "LANGUAGES", 20, "h", GOLD))
    for i, (lang, level) in enumerate(LANGUAGES):
        x = ex + i * 84
        body.append(text(x, 404, lang, 18, "s", TEXT))
        hearts = "".join(
            f'<rect x="{x + 34 + (k % 3) * 12}" y="{390 + (k // 3) * 12}" width="9" height="9" '
            f'fill="{RUBY if k < level else "#2a2f5c"}"/>'
            for k in range(6)
        )
        body.append(hearts)
    body.append(text(ex, 446, "human languages; the machine ones are under ARMOR", 20, "t", DIM))
    return svg(w, h, "".join(body), "Status: stats, equipment and languages")


TROPHY = [
    "KKKKKKKKKK",
    "KGGGGGGGGK",
    "KGgGGGGGGK",
    ".KGgGGGGK.",
    "..KGGGGK..",
    "...KGGK...",
    "....KK....",
    "...KGGK...",
    "..KKKKKK..",
]

ACHIEVEMENTS = [
    ("AGENT SUMMONER", "multi-agent workflows in production", VIOLET),
    ("WARDEN", "guardrails are hooks, not prose", RUBY),
    ("TOOLSMITH", "internal plugin + skills marketplace", MANA),
    ("GATEKEEPER", "a homemade PR quality gate", EMERALD),
    ("ORACLE", "demand forecasts the business plans on", GOLD),
    ("MERCHANT", "headless storefronts, shipped", MANA),
    ("BRIDGE BUILDER", "ERP to CRM, no middleware toll", EMERALD),
    ("WORLD BUILDER", "a game engine project, live", GOLD),
]


def achievements():
    w, cols = 1200, 4
    cell_w, cell_h = (w - 72) // cols, 120
    h = 70 + cell_h * 2 + 24
    body = [window(0, 0, w, h)]
    body.append(text(36, 50, "TROPHIES", 26, "h", GOLD))
    body.append(text(w - 36, 50, f"{len(ACHIEVEMENTS)}/{len(ACHIEVEMENTS)} UNLOCKED · 100%", 20, "t", EMERALD, "end"))
    for i, (name, desc, color) in enumerate(ACHIEVEMENTS):
        x, y = 36 + (i % cols) * cell_w, 74 + (i // cols) * cell_h
        body.append(
            f'<rect x="{x}" y="{y}" width="{cell_w - 16}" height="{cell_h - 16}" rx="6" fill="#000" '
            f'fill-opacity=".28" stroke="{color}" stroke-opacity=".6" stroke-width="2"/>'
        )
        body.append(sprite(TROPHY, {"K": INK, "G": color, "g": "#ffffff"}, x + 14, y + 22, 6))
        body.append(text(x + 90, y + 44, name, 13, "h", TEXT))
        for k, line in enumerate(textwrap.wrap(desc, 22)):
            body.append(text(x + 90, y + 70 + k * 20, line, 19, "t", DIM))
    return svg(w, h, "".join(body), "Trophies: " + ", ".join(a[0].title() for a in ACHIEVEMENTS))


def main():
    for name, render in (("banner", banner), ("party", party), ("status", status), ("achievements", achievements)):
        (ASSETS / f"{name}.svg").write_text(render(), encoding="utf-8")


if __name__ == "__main__":
    main()
