"""Draw the front page for Sunday 22 November 2026.

A single 1024x1024 newspaper front page, drawn with Pillow: a masthead,
a stats strip, a region bar, a "Day in UTC" timeline, three illustrated
heroes, ten illustrated mid cards, a world map with numbered pins, 24
briefs, a DATE CHECK box and a sources footer. Every story on the page
happened, or was first reported, on Sunday 22 November 2026; stories
from earlier days are named in the DATE CHECK box and left out of the
page. Run: python3 generate_image.py (writes entry.png next to it).
"""

import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (248, 244, 233)
INK = (20, 20, 20)
NAVY = (16, 28, 63)
NAVY2 = (24, 42, 92)
RED = (179, 39, 46)
RED_DARK = (143, 31, 38)
CREAM = (248, 244, 233)
GOLD = (176, 132, 16)
TEAL = (14, 107, 107)
ORANGE = (194, 94, 0)
PURPLE = (91, 42, 134)
GREEN = (46, 125, 50)
BLUE = (31, 78, 121)
GREY = (85, 85, 85)
LINE = (216, 210, 192)
OCEAN = (216, 230, 232)
LAND = (230, 220, 184)
LAND_LINE = (154, 143, 102)

FONT_DIR = "/usr/share/fonts/truetype/liberation"


def F(size, bold=False, italic=False, serif=False):
    name = "LiberationSerif" if serif else "LiberationSans"
    if bold and italic:
        name += "-BoldItalic"
    elif bold:
        name += "-Bold"
    elif italic:
        name += "-Italic"
    else:
        name += "-Regular"
    return ImageFont.truetype(os.path.join(FONT_DIR, name + ".ttf"), size)


def wrap(d, text, font, max_w, max_lines=None):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and d.textlength(lines[-1] + "\u2026", font=font) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1] + "\u2026"
    return lines


def para(d, x, y, lines, font, fill, lh):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


# ---------------------------------------------------------------- data

PRESS_TIME = "12:50 UTC"

STATS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed by air defence"),
    ("723", "seats voted in Hong Kong"),
    ("720/9", "India's record Test total in NZ"),
    ("$811bn", "Nvidia's lost week, worst since 2008"),
    ("$120bn", "adaptation target dropped at COP31"),
]

REGIONS = [
    ("EUROPE", 6, BLUE),
    ("MIDDLE EAST", 5, RED),
    ("ASIA-PACIFIC", 12, ORANGE),
    ("AMERICAS", 8, TEAL),
    ("OCEANIA", 4, PURPLE),
    ("WORLD", 2, GREY),
]

TIMELINE = [
    ("01:00", "HK polls open"),
    ("03:00", "COP31 objections close"),
    ("05:30", "Verstappen wins"),
    ("08:00", "161 drones downed"),
    ("14:00", "HK turnout 93.55%"),
    ("17:00", "ATP final"),
    ("18:00", "COP31 still stalled"),
]

HEROES = [
    {
        "num": 1, "place": "ANTALYA, T\u00dcRKIYE", "topic": "CLIMATE",
        "tag": "REPORTED", "scene": "cop31",
        "kicker": "COP31: FINAL TEXT",
        "head": "Climate deal lands with no mention of fossil fuels",
        "deck": "The final text keeps the 35% electricity-by-2035 goal, drops the "
                "$120bn adaptation target and is the first to admit 1.5\u00b0C will be "
                "overshot. Approval stalled Sunday, two days overdue.",
        "source": "(Reuters, AP)",
    },
    {
        "num": 2, "place": "MANAMA, BAHRAIN", "topic": "IRAN",
        "tag": "CLAIM", "scene": "bahrain",
        "kicker": "CLAIM VS DENIAL",
        "head": "Iran claims two US radars hit; Bahrain denies it",
        "deck": "The IRGC says it destroyed two Patriot radars on Saturday night. "
                "Bahrain answered on Sunday: the target was a civilian industrial "
                "site \u2014 a fire, no injuries \u2014 and a violation of its sovereignty.",
        "source": "(Al Jazeera, Reuters)",
    },
    {
        "num": 3, "place": "KYIV, UKRAINE", "topic": "WAR",
        "tag": "REPORTED", "scene": "ukraine",
        "kicker": "186 DRONES OVERNIGHT",
        "head": "Russia fires 186 drones; a Kyiv block is destroyed",
        "deck": "Air defences downed or jammed 161 of 186 strike drones. One "
                "destroyed a five-storey block in Dymer, near Kyiv; six Ukrainian "
                "drones bound for Moscow were downed.",
        "source": "(Ukrainian Air Force, Reuters)",
    },
]

MIDS = [
    {"num": 4, "place": "GULF OF FINLAND", "topic": "SEA", "tag": "ONGOING",
     "scene": "ship", "kicker": "SHIP ABLAZE",
     "head": "Sparta II still burning",
     "deck": "Hit Saturday; still burning at anchor Sunday.",
     "source": "(Reuters)"},
    {"num": 5, "place": "HONG KONG", "topic": "POLITICS", "tag": "REPORTED",
     "scene": "ballot", "kicker": "856 CANDIDATES",
     "head": "Hong Kong elects its Election Committee",
     "deck": "856 candidates, 723 seats; turnout 93.55%.",
     "source": "(SCMP)"},
    {"num": 6, "place": "WELLINGTON", "topic": "CRICKET", "tag": "REPORTED",
     "scene": "cricket", "kicker": "720/9 DECLARED",
     "head": "India post 720/9, a record in NZ",
     "deck": "Rahul 136, Pant 128; a 352-run lead on Day 4.",
     "source": "(ESPNcricinfo)"},
    {"num": 7, "place": "LAS VEGAS", "topic": "FORMULA 1", "tag": "REPORTED",
     "scene": "race", "kicker": "VERSTAPPEN WINS",
     "head": "Verstappen wins the Las Vegas GP",
     "deck": "From pole in 1:37.99; Norris +0.639, Piastri third.",
     "source": "(FIA)"},
    {"num": 8, "place": "TEHRAN, IRAN", "topic": "ENERGY", "tag": "REPORTED",
     "scene": "power", "kicker": "POWER CUTS",
     "head": "Iran begins rationing electricity",
     "deck": "Rolling cuts up to two hours a day.",
     "source": "(Wires)"},
    {"num": 9, "place": "NEW YORK", "topic": "MARKETS", "tag": "REPORTED",
     "scene": "chart", "kicker": "WORST SINCE 2008",
     "head": "Nvidia sheds $811bn in a week",
     "deck": "A week to Friday, tallied in Sunday reports.",
     "source": "(Clearview Politics)"},
    {"num": 10, "place": "NEW YORK", "topic": "TECH", "tag": "REPORTED",
     "scene": "ipo", "kicker": "PROJECT LANTERN",
     "head": "Anthropic slides 8.5% after debut",
     "deck": "22 underwriters; six-month non-competes.",
     "source": "(Reuters)"},
    {"num": 11, "place": "BRAS\u00cdLIA, BRAZIL", "topic": "POLITICS",
     "tag": "REPORTED", "scene": "hospital", "kicker": "IN INTENSIVE CARE",
     "head": "Bolsonaro in intensive care in Bras\u00edlia",
     "deck": "Acute bowel obstruction; stable, surgery possible.",
     "source": "(Reuters)"},
    {"num": 12, "place": "GAZA", "topic": "CEASEFIRE", "tag": "REPORTED",
     "scene": "gaza", "kicker": "CEASEFIRE FRAYS",
     "head": "Two die of wounds in Gaza; ceasefire frays",
     "deck": "Two die of wounds; talks open; UN warns.",
     "source": "(WAFA, Reuters)"},
    {"num": 13, "place": "WASHINGTON", "topic": "POLITICS", "tag": "REPORTED",
     "scene": "capitol", "kicker": "LEADERSHIP RACE",
     "head": "Van Hollen to challenge Schumer",
     "deck": "Secret vote on 1 Dec; first contested race since 1994.",
     "source": "(Reuters)"},
]

BRIEFS = [
    ("TURIN", "Zverev v Alcaraz in tonight's ATP final, 18:00 CET.", "ATP"),
    ("LONDON", "Will Jacks out of England's T20 tour with a broken hand.", "Reuters"),
    ("MANILA", "Transport group Manibela to strike on 23\u201324 Nov.", "GMA"),
    ("CEBU", "Fire on an Ormoc-bound vessel; no casualties.", "GMA"),
    ("MANILA", "Gatchalian confident the 2027 budget will be ratified.", "GMA"),
    ("MANILA", "Guterres cites Ifugao terraces in fossil-fuel call.", "GMA"),
    ("NEW DELHI", "BJP MP Ramrao Wadkute dies at 72.", "EIN"),
    ("NEW DELHI", "Cricketer Chahal joins the BJP's OBC Morcha.", "EIN"),
    ("NEW DELHI", "Nepal PM Shah begins a state visit.", "dainikjagran"),
    ("APIA", "Cyclone Xavier weakens north of Samoa.", "Wires"),
    ("ABU DHABI", "UAE shuttles oil past Iran as Hormuz tensions bite.", "Wires"),
    ("DUBAI", "British swimmer braves the Strait of Hormuz.", "Wires"),
    ("BRUSSELS", "EU floats a digital-tax plan amid budget rows.", "Wires"),
    ("SAN FRANCISCO", "OpenRouter drops three providers after a probe.", "Wires"),
    ("LONDON", "Antidepressants work in 115 trials, 30,000+ patients.", "Lancet"),
    ("SYDNEY", "Australia, NZ and US navies in Exercise Dugong.", "Wires"),
    ("WASHINGTON", "Watchdog finds a \u201ccascade of problems\u201d at ICE.", "Wires"),
    ("MANILA", "Comelec projects 4 million new voters for 2028.", "GMA"),
    ("WASHINGTON", "CBO: Navy shipbuilding to cost $54bn a year.", "CBO"),
    ("BOUGAINVILLE", "Australia and NZ rush aid as El Ni\u00f1o looms.", "Wires"),
    ("MANILA", "Marcos clarifies Trump trade claim; ICC rebuffs Duterte.", "GMA"),
    ("NEW DELHI", "India and China conclude border commander talks.", "Wires"),
    ("MASTUNG", "China renews UN bid on BLA; Pakistan kills 15.", "Wires"),
    ("WORLD", "Ghostscript flaw escapes its -dSAFER sandbox.", "CVE-2026-125396"),
]

EXCLUSIONS = (
    "Peru M6.7 quake (Fri 20 Nov) \u00b7 Russia's 400-drone barrage (Thu\u2013Fri 19\u201320 Nov) \u00b7 "
    "\u2018El Chapo Isidro\u2019 captured (Fri 20 Nov) \u00b7 ICJ Myanmar genocide ruling (Thu 19 Nov) \u00b7 "
    "Shenzhen summit (Thu 19 Nov) \u00b7 GTA VI launch (Thu 19 Nov) \u00b7 BepiColombo Mercury orbit "
    "(Sat 21 Nov) \u00b7 Nigeria boat capsized, Bayelsa (Fri 20 Nov) \u00b7 FBI NCIC hack confirmed "
    "(Sat 21 Nov) \u00b7 EU\u2013Indonesia CEPA signed (Sat 21 Nov) \u00b7 UK\u2013EU reset deal "
    "(Fri 20 Nov) \u00b7 Kryvyi Rih strike (Sat 21 Nov) \u00b7 Sparta II drone hit (Sat 21 Nov \u2014 fire "
    "continued Sunday, story 4) \u00b7 Bahrain strikes (late Sat 21 Nov \u2014 claims and denials Sunday, "
    "story 2) \u00b7 Kursk nuclear-plant drone attack (24 Aug 2025, recycled by aggregators)."
)

# ---------------------------------------------------------------- scenes


def scene(d, kind, x, y, w, h):
    if kind == "cop31":
        d.rectangle([x, y, x + w, y + h], fill=(168, 205, 222))
        d.ellipse([x + 14, y + 12, x + 78, y + 76], fill=(58, 122, 158))
        for bx, by, br in [(30, 34, 7), (48, 28, 5), (58, 48, 6), (36, 56, 5)]:
            d.ellipse([x + bx - br, y + by - br, x + bx + br, y + by + br],
                      fill=(94, 168, 96))
        d.ellipse([x + w - 52, y + 8, x + w - 12, y + 48], fill=(248, 244, 233),
                  outline=(90, 90, 90))
        d.line([x + w - 32, y + 28, x + w - 32, y + 16], fill=INK, width=2)
        d.line([x + w - 32, y + 28, x + w - 20, y + 32], fill=INK, width=2)
        d.rectangle([x, y + h - 30, x + w, y + h], fill=(122, 82, 48))
        for i, cx in enumerate(range(int(x + 18), int(x + w - 18), 34)):
            d.ellipse([cx, y + h - 62, cx + 16, y + h - 46], fill=(232, 198, 160))
            d.polygon([(cx - 4, y + h - 46), (cx + 20, y + h - 46),
                       (cx + 14, y + h - 30), (cx + 2, y + h - 30)],
                      fill=[(179, 39, 46), (31, 78, 121), (14, 107, 107),
                            (176, 132, 16), (91, 42, 134)][i % 5])
    elif kind == "bahrain":
        d.rectangle([x, y, x + w, y + h], fill=(13, 22, 48))
        for sx, sy in [(20, 14), (70, 26), (120, 10), (200, 20), (260, 12), (300, 30)]:
            d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=CREAM)
        d.ellipse([x + w - 46, y + 10, x + w - 18, y + 38], fill=(232, 228, 205))
        for bx in (x + 30, x + 130, x + 230):
            d.rectangle([bx, y + h - 34, bx + 46, y + h - 12], fill=(96, 104, 120))
            d.pieslice([bx + 6, y + h - 62, bx + 40, y + h - 28], 180, 360,
                       fill=(150, 158, 172))
            d.line([bx + 23, y + h - 62, bx + 44, y + h - 78], fill=(200, 206, 216),
                   width=2)
        for fx, fy in [(x + 52, y + h - 40), (x + 152, y + h - 40),
                       (x + 252, y + h - 40)]:
            d.polygon([(fx - 8, y + h - 12), (fx, fy), (fx + 8, y + h - 12)],
                      fill=(232, 120, 30))
            d.polygon([(fx - 4, y + h - 12), (fx, fy + 8), (fx + 4, y + h - 12)],
                      fill=(244, 196, 60))
        for i in range(8):
            t = i / 7.0
            px = x + 60 + t * 200
            py = y + 22 + (1 - t) * 46 - 18 * t * (1 - t) * 4
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(244, 170, 60))
    elif kind == "ukraine":
        d.rectangle([x, y, x + w, y + h], fill=(13, 22, 48))
        for sx, sy in [(16, 12), (60, 22), (110, 10), (180, 18), (250, 12),
                       (300, 24), (90, 34)]:
            d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=CREAM)
        d.rectangle([x + 30, y + 34, x + 150, y + h], fill=(38, 42, 58))
        for r in range(6):
            for c in range(5):
                wx = x + 42 + c * 22
                wy = y + 44 + r * 13
                lit = (r + c) % 3 != 0
                d.rectangle([wx, wy, wx + 12, wy + 8],
                            fill=(244, 196, 60) if lit else (20, 24, 40))
        d.rectangle([x + 150, y + 60, x + 210, y + h], fill=(52, 56, 74))
        for r in range(4):
            for c in range(2):
                wx = x + 160 + c * 22
                wy = y + 70 + r * 13
                d.rectangle([wx, wy, wx + 12, wy + 8],
                            fill=(244, 196, 60) if (r + c) % 2 else (20, 24, 40))
        d.polygon([(x + 200, y + 30), (x + 214, y + 46), (x + 228, y + 30),
                   (x + 214, y + 58), (x + 206, y + 34), (x + 222, y + 54)],
                  fill=(232, 120, 30))
        for dx, dy in [(250, 30), (280, 52), (225, 18)]:
            d.line([x + dx - 7, y + dy - 7, x + dx + 7, y + dy + 7],
                   fill=(200, 206, 216), width=2)
            d.line([x + dx - 7, y + dy + 7, x + dx + 7, y + dy - 7],
                   fill=(200, 206, 216), width=2)
            d.ellipse([x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2],
                      fill=(244, 170, 60))
    elif kind == "ship":
        d.rectangle([x, y, x + w, y + h], fill=(232, 150, 70))
        d.rectangle([x, y + h - 18, x + w, y + h], fill=(24, 52, 92))
        d.polygon([(x + 20, y + h - 18), (x + w - 14, y + h - 18),
                   (x + w - 34, y + h - 6), (x + 36, y + h - 6)], fill=(30, 34, 44))
        for cx, cc in [(52, (179, 39, 46)), (78, (31, 78, 121)), (104, (14, 107, 107)),
                       (130, (176, 132, 16))]:
            d.rectangle([x + cx, y + h - 40, x + cx + 22, y + h - 20], fill=cc)
        for fx in (x + 60, x + 110, x + 160):
            d.polygon([(fx - 7, y + h - 18), (fx, y + h - 44), (fx + 7, y + h - 18)],
                      fill=(232, 120, 30))
        for sx, sy, sr in [(150, 18, 9), (168, 12, 7), (140, 30, 6)]:
            d.ellipse([x + sx - sr, y + sy - sr, x + sx + sr, y + sy + sr],
                      fill=(120, 120, 120))
        d.ellipse([x + w - 34, y + 8, x + w - 6, y + 36], fill=(244, 220, 160))
    elif kind == "ballot":
        d.rectangle([x, y, x + w, y + h], fill=(238, 238, 226))
        d.rectangle([x + 58, y + 8, x + 128, y + h - 8], fill=(179, 39, 46))
        d.rectangle([x + 72, y + 8, x + 114, y + 13], fill=(90, 20, 24))
        d.polygon([(x + 78, y - 6), (x + 108, y - 6), (x + 96, y + 8), (x + 84, y + 8)],
                  fill=(248, 244, 233))
        d.line([x + 140, y + 26, x + 152, y + 38], fill=(46, 125, 50), width=4)
        d.line([x + 152, y + 38, x + 178, y + 10], fill=(46, 125, 50), width=4)
        d.rectangle([x + 12, y + h - 14, x + 52, y + h - 6], fill=(31, 78, 121))
    elif kind == "cricket":
        d.rectangle([x, y, x + w, y + h], fill=(94, 168, 96))
        d.rectangle([x + 70, y + 4, x + 122, y + h - 4], fill=(214, 186, 140))
        d.ellipse([x + 140, y + 10, x + 152, y + 22], fill=(232, 198, 160))
        d.line([x + 146, y + 22, x + 146, y + 34], fill=INK, width=3)
        d.line([x + 146, y + 26, x + 128, y + 38], fill=INK, width=3)
        d.line([x + 146, y + 26, x + 162, y + 30], fill=INK, width=3)
        d.line([x + 128, y + 38, x + 118, y + h - 8], fill=(122, 82, 48), width=3)
        d.ellipse([x + 168, y + h - 16, x + 176, y + h - 8], fill=(179, 39, 46))
    elif kind == "race":
        d.rectangle([x, y, x + w, y + h], fill=(32, 34, 44))
        for lx in (x + 10, x + 60, x + 120):
            d.line([lx, y + h - 10, lx + 30, y + h - 10], fill=(200, 200, 200),
                   width=2)
        d.polygon([(x + 30, y + h - 26), (x + 130, y + h - 26),
                   (x + 148, y + h - 12), (x + 22, y + h - 12)], fill=(179, 39, 46))
        d.polygon([(x + 62, y + h - 40), (x + 104, y + h - 40),
                   (x + 112, y + h - 26), (x + 56, y + h - 26)], fill=(200, 60, 60))
        for wx in (x + 44, x + 122):
            d.ellipse([wx, y + h - 14, wx + 14, y + h], fill=(10, 10, 10),
                      outline=(160, 160, 160))
        for r in range(2):
            for c in range(3):
                d.rectangle([x + 160 + c * 9, y + 6 + r * 9,
                             x + 169 + c * 9, y + 15 + r * 9],
                            fill=INK if (r + c) % 2 == 0 else CREAM)
        d.line([x + 164, y + 24, x + 164, y + h - 26], fill=(150, 150, 150), width=2)
    elif kind == "power":
        d.rectangle([x, y, x + w, y + h], fill=(232, 170, 90))
        d.polygon([(x + 20, y + h), (x + 44, y + 8), (x + 68, y + h)], fill=(60, 60, 60))
        d.line([x + 44, y + 8, x + 24, y + 30], fill=(60, 60, 60), width=2)
        d.line([x + 44, y + 8, x + 64, y + 30], fill=(60, 60, 60), width=2)
        d.polygon([(x + 150, y + 10), (x + 132, y + 30), (x + 146, y + 30),
                   (x + 132, y + h - 8), (x + 158, y + 26), (x + 144, y + 26)],
                  fill=(244, 196, 60))
        for bx in (x + 100, x + 130, x + 165):
            d.rectangle([bx, y + h - 16, bx + 22, y + h], fill=(40, 40, 52))
            d.rectangle([bx + 5, y + h - 12, bx + 9, y + h - 8],
                        fill=(244, 196, 60))
    elif kind == "chart":
        d.rectangle([x, y, x + w, y + h], fill=(248, 244, 233))
        d.line([x + 12, y + h - 10, x + w - 8, y + h - 10], fill=GREY, width=1)
        d.line([x + 12, y + 8, x + 12, y + h - 10], fill=GREY, width=1)
        pts = [(x + 16, y + 10), (x + 52, y + 14), (x + 88, y + 12),
               (x + 124, y + 22), (x + 160, y + 32), (x + 184, y + h - 14)]
        d.line(pts, fill=(179, 39, 46), width=3)
        for px, py in pts:
            d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(179, 39, 46))
        d.polygon([(x + 184, y + h - 14), (x + 172, y + h - 16), (x + 184, y + h - 26)],
                  fill=(179, 39, 46))
        d.text((x + 120, y + 4), "-14%", font=F(11, bold=True), fill=RED)
    elif kind == "ipo":
        d.rectangle([x, y, x + w, y + h], fill=(238, 244, 238))
        bars = [14, 22, 18, 30, 26, 38]
        for i, bh in enumerate(bars):
            bx = x + 14 + i * 26
            d.rectangle([bx, y + h - 8 - bh, bx + 18, y + h - 8],
                        fill=(46, 125, 50) if i < 5 else (31, 78, 121))
        d.polygon([(x + 168, y + 6), (x + 176, y + 18), (x + 184, y + 6)],
                  fill=(176, 132, 16))
        d.text((x + 160, y + 22), "IPO", font=F(10, bold=True), fill=GOLD)
    elif kind == "hospital":
        d.rectangle([x, y, x + w, y + h], fill=(238, 244, 244))
        d.rectangle([x + 14, y + 8, x + 46, y + 40], fill=(248, 244, 233),
                    outline=(179, 39, 46), width=2)
        d.rectangle([x + 26, y + 14, x + 34, y + 34], fill=(179, 39, 46))
        d.rectangle([x + 20, y + 20, x + 40, y + 28], fill=(179, 39, 46))
        d.line([(x + 56, y + 24), (x + 76, y + 24), (x + 84, y + 12),
                (x + 94, y + 34), (x + 102, y + 24), (x + 120, y + 24),
                (x + 130, y + 16), (x + 140, y + 24), (x + 170, y + 24)],
               fill=(46, 125, 50), width=2)
        d.line([(x + 56, y + h - 8), (x + 176, y + h - 8)], fill=GREY, width=1)
    elif kind == "gaza":
        d.rectangle([x, y, x + w, y + h], fill=(222, 200, 160))
        d.ellipse([x + w - 40, y + 6, x + w - 12, y + 34], fill=(244, 220, 160))
        for bx, bh in [(x + 10, 26), (x + 40, 34), (x + 76, 22), (x + 108, 30),
                       (x + 140, 24), (x + 168, 18)]:
            d.rectangle([bx, y + h - bh, bx + 26, y + h], fill=(90, 80, 66))
        d.line([x + 60, y + 8, x + 60, y + 26], fill=INK, width=2)
        d.polygon([(x + 60, y + 8), (x + 78, y + 13), (x + 60, y + 18)],
                  fill=(248, 244, 233))
    elif kind == "capitol":
        d.rectangle([x, y, x + w, y + h], fill=(214, 226, 232))
        d.rectangle([x + 66, y + 26, x + 126, y + h - 6], fill=(248, 244, 233))
        d.pieslice([x + 66, y + 4, x + 126, y + 34], 180, 360,
                   fill=(248, 244, 233))
        d.line([x + 96, y + 2, x + 96, y - 6], fill=INK, width=2)
        d.polygon([(x + 96, y - 6), (x + 110, y - 2), (x + 96, y + 2)],
                  fill=(179, 39, 46))
        for cx in (x + 76, x + 92, x + 108):
            d.rectangle([cx, y + 30, cx + 5, y + h - 6], fill=(180, 180, 180))
        d.rectangle([x + 20, y + h - 6, x + w - 20, y + h], fill=(160, 160, 160))


# ---------------------------------------------------------------- map

CONTINENTS = [
    [(15, 58), (45, 40), (85, 38), (108, 52), (100, 68), (88, 80), (72, 96),
     (48, 108), (28, 95), (12, 72)],
    [(110, 26), (126, 24), (130, 34), (114, 40)],
    [(60, 122), (86, 118), (100, 138), (90, 172), (74, 192), (62, 162)],
    [(138, 56), (162, 46), (182, 56), (176, 72), (154, 78), (136, 68)],
    [(138, 86), (172, 80), (196, 94), (188, 128), (168, 146), (148, 122)],
    [(182, 44), (248, 36), (286, 52), (278, 84), (242, 100), (206, 94),
     (188, 68)],
    [(242, 152), (272, 148), (284, 164), (258, 174), (240, 162)],
    [(282, 186), (290, 184), (292, 196), (284, 198)],
]

PINS = {
    1: (174, 66), 2: (200, 96), 3: (158, 52), 4: (176, 38), 5: (260, 90),
    6: (288, 192), 7: (36, 80), 8: (210, 74), 9: (24, 64), 10: (82, 62),
    11: (80, 146), 12: (180, 80), 13: (68, 74),
}


def tag_chip(d, x, y, tag):
    fill = RED if tag in ("CLAIM",) else NAVY
    f = F(8, bold=True)
    w = d.textlength(tag, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], radius=2, fill=fill)
    d.text((x + 5, y + 2), tag, font=f, fill=CREAM)
    return w


# ---------------------------------------------------------------- build


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 10
    CW = W - 2 * M

    # 1. top bar
    d.rectangle([0, 0, W, 22], fill=NAVY)
    d.text((M, 5), "THE WORLD IN ONE DAY", font=F(11, bold=True), fill=CREAM)
    rt = "37 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - M - d.textlength(rt, font=F(11, bold=True)), 5), rt,
           font=F(11, bold=True), fill=CREAM)

    # 2. masthead
    mast = "Sunday 22 November 2026"
    mf = F(54, bold=True, serif=True)
    mw = d.textlength(mast, font=mf)
    d.text(((W - mw) / 2, 26), mast, font=mf, fill=INK)
    print("masthead width:", round(mw))

    # 3. red deck line
    deck = ("COP31's final text names no fossil fuels \u00b7 Iran's radar claim meets "
            "Bahrain's denial \u00b7 186 drones over Ukraine in the night")
    df = F(15, italic=True, serif=True)
    dw = d.textlength(deck, font=df)
    d.text(((W - dw) / 2, 86), deck, font=df, fill=RED)
    print("deck width:", round(dw))
    d.line([M, 106, W - M, 106], fill=INK, width=2)

    # 4. stats strip
    y = 110
    cell = CW / 6.0
    for i, (num, cap) in enumerate(STATS):
        cx = M + i * cell
        if i:
            d.line([cx, y + 2, cx, y + 42], fill=LINE, width=1)
        nf = F(23, bold=True, serif=True)
        d.text((cx + 8, y), num, font=nf, fill=RED)
        lines = wrap(d, cap, F(8), cell - 16, max_lines=2)
        para(d, cx + 8, y + 28, lines, F(8), INK, 10)
        print("stat", num, "lines:", len(lines))

    # 5. region bar
    y = 160
    total = sum(c for _, c, _ in REGIONS)
    rx = M
    for name, count, color in REGIONS:
        seg = CW * count / total
        d.rectangle([rx, y, rx + seg, y + 20], fill=color)
        label = "%s %d" % (name, count)
        lf = F(9, bold=True)
        lw = d.textlength(label, font=lf)
        d.text((rx + (seg - lw) / 2, y + 5), label, font=lf, fill=CREAM)
        rx += seg

    # 6. UTC timeline
    y = 184
    d.rectangle([M, y, W - M, y + 18], fill=NAVY)
    d.rectangle([M, y, M + 108, y + 18], fill=RED)
    d.text((M + 6, y + 4), "THE DAY IN UTC", font=F(9, bold=True), fill=CREAM)
    tf = F(9, bold=True)
    avail = CW - 108 - 8
    beats = ["%s %s" % (t, s) for t, s in TIMELINE]
    bw = [d.textlength(b, font=tf) for b in beats]
    gap = (avail - sum(bw)) / (len(beats) - 1)
    bx = M + 108 + 4
    for b, wdt in zip(beats, bw):
        d.text((bx, y + 4), b, font=tf, fill=CREAM)
        bx += wdt + gap
    print("timeline gap:", round(gap))

    # 7. heroes
    y = 206
    hcol = (CW - 20) / 3.0
    for i, hero in enumerate(HEROES):
        hx = M + i * (hcol + 10)
        scene(d, hero["scene"], hx, y, hcol, 116)
        d.rectangle([hx, y, hx + 150, y + 15], fill=RED)
        d.text((hx + 5, y + 3), hero["kicker"], font=F(8, bold=True), fill=CREAM)
        d.rectangle([hx, y + 116, hx + hcol, y + 117], fill=INK)
        ty = y + 122
        d.text((hx, ty), "%d %s \u00b7 %s" % (hero["num"], hero["place"],
                                              hero["topic"]),
               font=F(8, bold=True), fill=INK)
        tag_chip(d, hx + hcol - 62, ty - 1, hero["tag"])
        hy = ty + 12
        hl = wrap(d, hero["head"], F(15, bold=True, serif=True), hcol, 2)
        hy = para(d, hx, hy, hl, F(15, bold=True, serif=True), INK, 19)
        dl = wrap(d, hero["deck"], F(10), hcol, 3)
        hy = para(d, hx, hy + 2, dl, F(10), INK, 13)
        d.text((hx, hy + 2), hero["source"], font=F(8, italic=True), fill=GREY)
        print("hero", hero["num"], "head lines:", len(hl), "deck lines:", len(dl))

    # 8. mids, two rows of five
    y = 436
    mcol = (CW - 40) / 5.0
    for row in range(2):
        for col in range(5):
            mid = MIDS[row * 5 + col]
            mx = M + col * (mcol + 10)
            my = y + row * 104
            scene(d, mid["scene"], mx, my, mcol, 38)
            d.rectangle([mx, my, mx + 108, my + 12], fill=RED)
            d.text((mx + 4, my + 2), mid["kicker"], font=F(7, bold=True),
                   fill=CREAM)
            ty = my + 42
            d.text((mx, ty), "%d %s \u00b7 %s" % (mid["num"], mid["place"],
                                                  mid["topic"]),
                   font=F(7, bold=True), fill=INK)
            tag_chip(d, mx + mcol - 56, ty - 1, mid["tag"])
            hl = wrap(d, mid["head"], F(11, bold=True, serif=True), mcol, 2)
            hy = para(d, mx, ty + 11, hl, F(11, bold=True, serif=True), INK, 13)
            dl = wrap(d, mid["deck"], F(8), mcol, 2)
            hy = para(d, mx, hy + 1, dl, F(8), INK, 10)
            d.text((mx, hy + 1), mid["source"], font=F(7, italic=True),
                   fill=GREY)
            print("mid", mid["num"], "head lines:", len(hl),
                  "deck lines:", len(dl))

    # 9. map + briefs
    y = 648
    d.text((M, y), "WHERE IT HAPPENED", font=F(10, bold=True), fill=INK)
    d.text((M + 132, y + 1), "pins match story numbers",
           font=F(8, italic=True), fill=GREY)
    map_x, map_y, map_w, map_h = M, y + 18, 300, 210
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=OCEAN,
                outline=(150, 150, 150))
    for poly in CONTINENTS:
        pts = [(map_x + px, map_y + py) for px, py in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    for num, (px, py) in PINS.items():
        cx, cy = map_x + px, map_y + py
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                  outline=CREAM, width=1)
        nf = F(8, bold=True)
        t = str(num)
        d.text((cx - d.textlength(t, font=nf) / 2, cy - 5), t, font=nf,
               fill=CREAM)
    d.text((map_x, map_y + map_h + 4), "Red numbers mark stories 1\u201313.",
           font=F(8, italic=True), fill=GREY)

    bx = M + 310
    bw = W - M - bx
    d.rectangle([bx, y, bx + bw, y + 18], fill=NAVY)
    d.text((bx + 6, y + 4), "ALSO ON SUNDAY 22 NOVEMBER \u2014 24 MORE STORIES",
           font=F(10, bold=True), fill=CREAM)
    col_w = (bw - 10) / 2.0
    bf = F(9)
    bfb = F(9, bold=True)
    by = y + 24
    for i, (city, text, src) in enumerate(BRIEFS):
        col = i // 12
        row = i % 12
        cx = bx + col * (col_w + 10)
        cy = by + row * 17
        d.text((cx, cy), "%d." % (i + 14), font=bfb, fill=RED)
        line = "%s \u2014 %s (%s)" % (city, text, src)
        lines = wrap(d, line, bf, col_w - 18, max_lines=1)
        d.text((cx + 18, cy), lines[0], font=bf, fill=INK)
        if len(lines[0]) < len(line):
            print("BRIEF TRUNCATED:", i + 14, line)

    # 10. DATE CHECK
    y = 882
    d.rectangle([M, y, W - M, y + 64], outline=RED, width=2)
    dc = ("DATE CHECK \u2014 Wires read up to %s, Sunday 22 November 2026. Left out "
          "as other days' news: %s" % (PRESS_TIME, EXCLUSIONS))
    lines = wrap(d, dc, F(9), CW - 20)
    para(d, M + 10, y + 6, lines, F(9), INK, 12)
    print("date check lines:", len(lines))

    # 11. footer
    y = 952
    d.text((M, y), "Sources: Reuters, AP, AFP, BBC, Al Jazeera, The Guardian, SCMP, "
                   "ESPNcricinfo, Cricbuzz, GMA, EIN Presswire, Wires \u2014 and the "
                   "outlets named with each story. Pictures and map: original, drawn in code.",
           font=F(8), fill=GREY)
    d.text((M, y + 12), "CERTAINTY: REPORTED = confirmed by named sources \u00b7 CLAIM = one "
                        "side's account, labelled as such \u00b7 ONGOING = still developing as "
                        "we print \u00b7 FORECAST = still to happen when drawn.",
           font=F(8), fill=GREY)

    # 12. bottom bar
    d.rectangle([0, 998, W, H], fill=NAVY)
    d.text((M, 1006), "THE WORLD IN ONE DAY", font=F(9, bold=True), fill=CREAM)
    bb = "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE"
    d.text((W - M - d.textlength(bb, font=F(9, bold=True)), 1006), bb,
           font=F(9, bold=True), fill=CREAM)

    out = os.path.join(HERE, "entry.png")
    img.save(out, optimize=True)
    print("saved", out, os.path.getsize(out), "bytes")
    return out


if __name__ == "__main__":
    build()
