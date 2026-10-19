"""Shared pieces for the profile cards: palette, embedded pixel fonts, JRPG windows and sprites."""

import base64
from html import escape
from pathlib import Path

FONTS = Path(__file__).resolve().parent.parent / "assets" / "fonts"

NIGHT = "#070a18"
INK = "#0b0b16"
WIN_TOP = "#2c3fb5"
WIN_BOTTOM = "#0a1150"
FRAME = "#e9ecff"
GOLD = "#ffcc4d"
GOLD_DARK = "#b9770e"
EMERALD = "#39d98a"
MANA = "#5ab0ff"
RUBY = "#ff4d6d"
VIOLET = "#a77bff"
TEXT = "#f2f4ff"
DIM = "#9aa3d6"


def font_css():
    faces = []
    for family, file in (("Silk", "Silkscreen-Regular"), ("SilkB", "Silkscreen-Bold"), ("Term", "VT323-Regular")):
        data = base64.b64encode((FONTS / f"{file}.woff2").read_bytes()).decode()
        faces.append(f"@font-face{{font-family:{family};src:url(data:font/woff2;base64,{data}) format('woff2')}}")
    return "".join(faces)


def svg(width, height, body, title, extra_css=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="{title}" shape-rendering="crispEdges">'
        f"<title>{title}</title>"
        f"<style>{font_css()}"
        ".h{font-family:SilkB,monospace}.s{font-family:Silk,monospace}.t{font-family:Term,monospace}"
        f"{extra_css}</style>"
        "<defs>"
        f'<linearGradient id="win" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{WIN_TOP}"/>'
        f'<stop offset="1" stop-color="{WIN_BOTTOM}"/></linearGradient>'
        "</defs>"
        f"{body}</svg>"
    )


def window(x, y, w, h):
    """A classic JRPG menu window: blue gradient, white double frame."""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{INK}"/>'
        f'<rect x="{x + 3}" y="{y + 3}" width="{w - 6}" height="{h - 6}" rx="8" fill="url(#win)" '
        f'stroke="{FRAME}" stroke-width="3"/>'
        f'<rect x="{x + 8}" y="{y + 8}" width="{w - 16}" height="{h - 16}" rx="5" fill="none" '
        f'stroke="{FRAME}" stroke-opacity=".25" stroke-width="1"/>'
    )


def text(x, y, content, size, cls="s", fill=TEXT, anchor="start", extra=""):
    return (
        f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" {extra}>'
        f"{escape(str(content), quote=False)}</text>"
    )


def shadow_text(x, y, content, size, fill=GOLD, shade=INK, offset=4, cls="h", anchor="start"):
    return text(x + offset, y + offset, content, size, cls, shade, anchor) + text(
        x, y, content, size, cls, fill, anchor
    )


def bar(x, y, w, h, ratio, fill, back="#05082a"):
    filled = max(0, min(1, ratio)) * (w - 4)
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{INK}"/>'
        f'<rect x="{x + 2}" y="{y + 2}" width="{w - 4}" height="{h - 4}" fill="{back}"/>'
        f'<rect x="{x + 2}" y="{y + 2}" width="{filled:.1f}" height="{h - 4}" fill="{fill}"/>'
        f'<rect x="{x + 2}" y="{y + 2}" width="{filled:.1f}" height="{max(1, (h - 4) // 3)}" fill="#fff" '
        f'fill-opacity=".35"/>'
    )


def sprite(rows, palette, x, y, scale):
    """Draw a pixel sprite from strings; '.' is transparent. Horizontal runs merge into one rect."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            run = c
            while run < len(row) and row[run] == ch:
                run += 1
            out.append(
                f'<rect x="{x + c * scale}" y="{y + r * scale}" width="{(run - c) * scale}" height="{scale}" '
                f'fill="{palette[ch]}"/>'
            )
            c = run
    return "".join(out)


HERO = [
    "...........KOOK...",
    "..........KOooOK..",
    "..........KOooOK..",
    ".....KKKK..KOOK...",
    "....KhhhhK..KWK...",
    "...KhHHHHhK.KWK...",
    "..KhHHHHHHhKKWK...",
    "..KHHKKKKHHKKWK...",
    "..KHKSSSSKHKKWK...",
    "..KHKEScEKHKKWK...",
    "..KHKSSSSKHKKWK...",
    "..KHHKSSKHHKKWK...",
    ".KRRGGGGGGRRKWK...",
    ".KRrRRRRRRRrSSK...",
    "KRRrRRGRRRRRKWK...",
    "KRRrRRGRRRRRKWK...",
    "KRRrRRGRRRRrKWK...",
    "KRRRRRGRRRRRKWK...",
    "KRRRRRGRRRRRKWK...",
    ".KRRRRRRRRRRKWK...",
    "..KBBK..KBBK.KK...",
    "..KKKK..KKKK......",
]

# One sprite, three palette swaps: the JRPG way of making a party.
CLASSES = {
    "summoner": {"H": "#5b3fb0", "h": "#8f6cf0", "R": "#3a2a85", "r": "#5b45c0", "O": MANA, "o": "#d6ecff"},
    "strategist": {"H": "#1f5fa8", "h": "#5aa0f0", "R": "#c9ced8", "r": "#ffffff", "O": GOLD, "o": "#fff3c4"},
    "builder": {"H": "#2f7a3f", "h": "#5cc06d", "R": "#8a4b1f", "r": "#c0702f", "O": EMERALD, "o": "#d9ffe9"},
}


def hero_palette(cls):
    base = {"K": INK, "S": "#f1c27d", "E": MANA, "c": "#d99a5b", "G": GOLD, "W": "#8b5a2b", "B": "#3b2416"}
    return base | CLASSES[cls]


FAMILIAR = [
    "...KK...",
    "..KooK..",
    ".KMMMMK.",
    "KMEMMEMK",
    "KMMMMMMK",
    ".KMMMMK.",
    "..K..K..",
]


def familiar_palette(color):
    return {"K": INK, "M": color, "E": "#ffffff", "o": GOLD}
