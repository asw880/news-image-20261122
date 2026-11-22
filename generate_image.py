#!/usr/bin/env python3
"""Draw the v2 front page for news-image-20261122: 37 dated stories.

One-page newspaper front page, 1024x1024, drawn entirely in code with
Pillow and system fonts. No photos, no network, no external images.
Run: python3 generate_image.py  (writes entry.png next to this file)
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (179, 35, 27)
NAVY = (22, 35, 63)
GREY = (110, 108, 100)
LIGHT = (232, 226, 210)
SKY = (168, 205, 225)
NIGHT = (16, 22, 48)
NIGHT2 = (28, 38, 78)

FDIR = "/usr/share/fonts/truetype/liberation"


def F(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


SERIF = lambda s: F("LiberationSerif-Bold.ttf", s)
SERIF_R = lambda s: F("LiberationSerif-Regular.ttf", s)
SERIF_I = lambda s: F("LiberationSerif-Italic.ttf", s)
SERIF_BI = lambda s: F("LiberationSerif-BoldItalic.ttf", s)
SANS = lambda s: F("LiberationSans-Regular.ttf", s)
SANS_B = lambda s: F("LiberationSans-Bold.ttf", s)
SANS_I = lambda s: F("LiberationSans-Italic.ttf", s)


def wrap(text, font, max_w, draw):
    """Greedy word wrap; returns list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, font, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def center(d, cx, y, text, font, fill):
    d.text((cx - d.textlength(text, font=font) / 2, y), text, font=font, fill=fill)


def tag(d, x, y, label, fg, bg):
    """Certainty tag chip; returns width used."""
    f = SANS_B(8)
    w = d.textlength(label, font=f) + 10
    d.rounded_rectangle([x, y, x + w, y + 13], radius=2, fill=bg)
    d.text((x + 5, y + 2), label, font=f, fill=fg)
    return w


# ---------------------------------------------------------------- layout
M = 20                      # side margin
CW = W - 2 * M              # content width = 984
COL = 320                   # hero column width
GAP = 12
HERO_X = [M, M + COL + GAP, M + 2 * (COL + GAP)]

# region counts (counted from the story datelines; sums to 37)
REGIONS = [
    ("EUROPE", 7, (31, 78, 121)),
    ("MIDDLE EAST", 5, (179, 35, 27)),
    ("ASIA-PACIFIC", 12, (197, 90, 17)),
    ("AMERICAS", 8, (46, 125, 107)),
    ("OCEANIA", 4, (106, 74, 158)),
    ("WORLD", 1, (102, 102, 102)),
]

STATS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed by air defence"),
    ("723", "seats voted in Hong Kong"),
    ("720/9", "India's record Test total in NZ"),
    ("$811bn", "Nvidia's lost week, worst since 2008"),
    ("$120bn", "adaptation target dropped at COP31"),
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

PRESS_TIME = "13:20 UTC"   # set to the real UTC time when this page was drawn

DATE_CHECK = (
    "DATE CHECK \u2014 Wires read up to " + PRESS_TIME +
    ", Sunday 22 November 2026. Left out as other days' news: Peru M6.7 quake (Fri 20 Nov) \u00b7 "
    "Russia's 400-drone barrage (Thu\u2013Fri 19\u201320 Nov) \u00b7 \u2018El Chapo Isidro\u2019 captured "
    "(Fri 20 Nov) \u00b7 ICJ Myanmar genocide ruling (Thu 19 Nov) \u00b7 Shenzhen summit (Thu 19 Nov) \u00b7 "
    "GTA VI launch (Thu 19 Nov) \u00b7 BepiColombo Mercury orbit (Sat 21 Nov) \u00b7 Nigeria boat capsized, "
    "Bayelsa (Fri 20 Nov) \u00b7 FBI NCIC hack confirmed (Sat 21 Nov) \u00b7 EU\u2013Indonesia CEPA signed "
    "(Sat 21 Nov) \u00b7 UK\u2013EU reset deal (Fri 20 Nov) \u00b7 Kryvyi Rih strike (Sat 21 Nov) \u00b7 "
    "Sparta II drone hit (Sat 21 Nov \u2014 fire continued Sunday, story 4) \u00b7 Bahrain strikes "
    "(late Sat 21 Nov \u2014 claims and denials Sunday, story 2) \u00b7 Kursk nuclear-plant drone attack "
    "(24 Aug 2025, recycled by aggregators)."
)

FOOTER_SOURCES = (
    "Sources: Reuters, AP, AFP, BBC, Al Jazeera, The Guardian, SCMP, ESPNcricinfo, Cricbuzz, GMA, "
    "EIN Presswire, Wires \u2014 and the outlets named with each story. Pictures and map: original, drawn in code."
)
FOOTER_LEGEND = (
    "CERTAINTY: REPORTED = confirmed by named sources \u00b7 CLAIM = one side's account, labelled as such "
    "\u00b7 ONGOING = still developing as we print \u00b7 FORECAST = still to happen when drawn."
)


# ---------------------------------------------------------------- art
def kicker(d, x, y, w, text, bg=RED):
    f = SANS_B(10)
    tw = d.textlength(text, font=f) + 14
    d.rectangle([x, y, x + tw, y + 18], fill=bg)
    d.text((x + 7, y + 3), text, font=f, fill=(255, 255, 255))


def sun_glow(d, cx, cy, r, col):
    for i in range(5, 0, -1):
        d.ellipse([cx - r * i // 5, cy - r * i // 5, cx + r * i // 5, cy + r * i // 5],
                  fill=tuple(min(255, c + 18 * (5 - i)) for c in col))


def art_cop31(d, x, y, w, h):
    """Antalya conference hall at dawn: sky, sun, globe, delegate flags, table, clock."""
    # dawn sky gradient
    for i in range(h):
        t = i / h
        d.line([x, y + i, x + w, y + i],
               fill=(int(250 - 60 * t), int(214 - 40 * t), int(170 - 20 * t)))
    # sun
    sun_glow(d, x + w - 52, y + 34, 26, (245, 180, 60))
    d.ellipse([x + w - 68, y + 18, x + w - 36, y + 50], fill=(250, 200, 80))
    # skyline silhouettes
    for bx, bw, bh in [(0, 46, 26), (52, 38, 34), (96, 52, 22), (154, 40, 30), (200, 44, 24),
                       (250, 36, 32), (292, 28, 20)]:
        d.rectangle([x + bx, y + h - 58 - bh, x + bx + bw, y + h - 58], fill=(120, 90, 110))
        for wx in range(bx + 6, bx + bw - 4, 10):
            d.rectangle([x + wx, y + h - 54 - bh, x + wx + 4, y + h - 48 - bh],
                        fill=(250, 220, 130))
    # globe
    gx, gy, gr = x + 44, y + 52, 26
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 180))
    d.ellipse([gx - gr + 5, gy - gr + 8, gx - gr + 22, gy - gr + 24], fill=(90, 170, 110))
    d.ellipse([gx + 2, gy + 6, gx + 20, gy + 22], fill=(90, 170, 110))
    d.ellipse([gx - gr + 12, gy + gr - 18, gx + gr - 4, gy + gr - 2], fill=(90, 170, 110))
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 200, 340, fill=(255, 255, 255), width=1)
    # clock
    cx, cy, cr = x + w - 46, y + 88, 17
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255),
              outline=INK, width=2)
    d.line([cx, cy, cx, cy - 11], fill=INK, width=2)
    d.line([cx, cy, cx + 8, cy + 3], fill=INK, width=2)
    # delegate flags row
    flag_cols = [(179, 35, 27), (31, 78, 121), (46, 125, 107), (197, 90, 17),
                 (106, 74, 158), (0, 120, 120), (200, 60, 60), (60, 60, 160)]
    for i, c in enumerate(flag_cols):
        fx = x + 14 + i * 36
        d.rectangle([fx, y + h - 46, fx + 26, y + h - 30], fill=c)
        d.rectangle([fx, y + h - 30, fx + 26, y + h - 28], fill=(255, 255, 255))
    # table
    d.rectangle([x, y + h - 28, x + w, y + h], fill=(96, 62, 40))
    d.rectangle([x, y + h - 28, x + w, y + h - 24], fill=(120, 80, 52))
    for i in range(8):
        px = x + 20 + i * 36
        d.ellipse([px, y + h - 44, px + 14, y + h - 30], fill=(232, 190, 150))
    kicker(d, x, y + 6, w, "COP31: FINAL TEXT")


def art_bahrain(d, x, y, w, h):
    """Night over Manama: missile arcs, Patriot radars, fires, moon, sea."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    for sx, sy in [(30, 18), (90, 30), (150, 12), (210, 26), (270, 16), (300, 34),
                   (60, 44), (180, 40), (240, 48)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
    # moon
    d.ellipse([x + w - 46, y + 14, x + w - 16, y + 44], fill=(235, 230, 200))
    d.ellipse([x + w - 40, y + 22, x + w - 32, y + 30], fill=(210, 205, 175))
    # missile arcs (dashed orange trails)
    for (ax, ay, bx, by) in [(40, 96, 130, 30), (90, 100, 190, 26), (150, 98, 250, 34)]:
        for t in range(0, 11):
            tt = t / 10
            px = x + ax + (bx - ax) * tt
            py = y + ay + (by - ay) * tt - 34 * 4 * tt * (1 - tt)
            if t % 2 == 0:
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 170, 60))
        d.polygon([(x + bx, y + by - 6), (x + bx + 8, y + by), (x + bx, y + by + 6)],
                  fill=(255, 210, 120))
    # radar dishes
    for rx in (36, 132, 228):
        d.rectangle([x + rx + 12, y + h - 46, x + rx + 18, y + h - 20], fill=(90, 95, 110))
        d.pieslice([x + rx - 6, y + h - 78, x + rx + 36, y + h - 38], 200, 340,
                   fill=(200, 205, 215))
        d.line([x + rx + 15, y + h - 58, x + rx + 30, y + h - 70], fill=(220, 225, 235), width=2)
        # fire at base
        d.polygon([(x + rx + 4, y + h - 20), (x + rx + 12, y + h - 38),
                   (x + rx + 20, y + h - 20)], fill=(255, 140, 40))
        d.polygon([(x + rx + 8, y + h - 20), (x + rx + 12, y + h - 30),
                   (x + rx + 16, y + h - 20)], fill=(255, 220, 90))
    # sea
    d.rectangle([x, y + h - 20, x + w, y + h], fill=(20, 40, 70))
    for wx in range(8, w - 8, 26):
        d.line([x + wx, y + h - 10, x + wx + 14, y + h - 10], fill=(90, 130, 180), width=2)
    kicker(d, x, y + 6, w, "CLAIM VS DENIAL")


def art_kyiv(d, x, y, w, h):
    """Kyiv at night: skyline, lit windows, searchlights, drone crosses, blast."""
    d.rectangle([x, y, x + w, y + h], fill=NIGHT)
    for sx, sy in [(20, 14), (70, 26), (120, 10), (170, 22), (230, 14), (280, 28),
                   (45, 40), (150, 36), (260, 42)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
    # moon
    d.ellipse([x + w - 44, y + 12, x + w - 18, y + 38], fill=(235, 230, 200))
    # searchlight beams
    d.polygon([(x + 60, y + h), (x + 130, y + 18), (x + 150, y + 18), (x + 90, y + h)],
              fill=(60, 70, 120))
    d.polygon([(x + 240, y + h), (x + 190, y + 22), (x + 206, y + 22), (x + 268, y + h)],
              fill=(50, 60, 105))
    # buildings with lit windows
    for bx, bw, bh in [(0, 52, 52), (56, 44, 70), (104, 60, 46), (168, 48, 62),
                       (220, 56, 50), (280, 40, 66)]:
        d.rectangle([x + bx, y + h - 26 - bh, x + bx + bw, y + h - 26], fill=(10, 14, 32))
        for wy in range(y + h - 20 - bh, y + h - 30, 12):
            for wx in range(bx + 6, bx + bw - 6, 12):
                if (wx * 7 + wy * 3) % 5:
                    d.rectangle([x + wx, wy, x + wx + 5, wy + 6], fill=(250, 210, 110))
    # damaged block with blast
    d.rectangle([x + 168, y + h - 26 - 62, x + 216, y + h - 26 - 44], fill=(40, 30, 26))
    for i in range(8):
        ang = i * 3.14159 / 4
        ex = x + 192 + int(20 * __import__("math").cos(ang))
        ey = y + h - 96 + int(14 * __import__("math").sin(ang))
        d.line([x + 192, y + h - 96, ex, ey], fill=(255, 170, 60), width=3)
    d.ellipse([x + 182, y + h - 106, x + 202, y + h - 86], fill=(255, 200, 80))
    # drone crosses
    for dx, dy in [(120, 52), (250, 46), (300, 60)]:
        d.line([x + dx - 7, y + dy, x + dx + 7, y + dy], fill=(255, 255, 255), width=2)
        d.line([x + dx, y + dy - 7, x + dx, y + dy + 7], fill=(255, 255, 255), width=2)
    # ground
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(8, 10, 22))
    kicker(d, x, y + 6, w, "186 DRONES OVERNIGHT")


# ---------------------------------------------------------------- mid art
def art_sparta(d, x, y, w, h):
    """Cargo ship ablaze at dusk: sea, hull, containers, smoke, flames."""
    for i in range(h):
        t = i / h
        d.line([x, y + i, x + w, y + i],
               fill=(int(240 - 90 * t), int(150 - 30 * t), int(90 - 10 * t)))
    d.ellipse([x + w - 30, y + 4, x + w - 8, y + 26], fill=(250, 210, 120))
    # sea
    d.rectangle([x, y + h - 14, x + w, y + h], fill=(30, 70, 110))
    for wx in range(4, w - 4, 18):
        d.line([x + wx, y + h - 7, x + wx + 10, y + h - 7], fill=(120, 170, 220), width=2)
    # hull
    d.polygon([(x + 8, y + h - 22), (x + w - 8, y + h - 22), (x + w - 20, y + h - 12),
               (x + 20, y + h - 12)], fill=(40, 40, 48))
    # containers
    for i, c in enumerate([(179, 35, 27), (31, 78, 121), (197, 120, 20), (46, 125, 107)]):
        d.rectangle([x + 16 + i * 34, y + h - 40, x + 44 + i * 34, y + h - 23], fill=c)
    # smoke + flames
    d.ellipse([x + 96, y + 2, x + 118, y + 18], fill=(60, 60, 60))
    d.ellipse([x + 108, y + 0, x + 126, y + 12], fill=(80, 80, 80))
    d.polygon([(x + 60, y + h - 40), (x + 66, y + h - 52), (x + 72, y + h - 40)],
              fill=(255, 140, 40))
    d.polygon([(x + 130, y + h - 40), (x + 136, y + h - 50), (x + 142, y + h - 40)],
              fill=(255, 200, 80))


def art_hk(d, x, y, w, h):
    """Ballot box, checkmark, flag stripes, ballot papers."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 30, 40))
    d.rectangle([x, y, x + w, y + 10], fill=(255, 255, 255))
    d.rectangle([x, y + h - 10, x + w, y + h], fill=(255, 255, 255))
    # ballot box
    d.rectangle([x + 52, y + 14, x + 108, y + h - 8], fill=(255, 255, 255),
                outline=INK, width=2)
    d.rectangle([x + 66, y + 10, x + 94, y + 16], fill=INK)
    d.line([x + 62, y + 26, x + 72, y + 36], fill=(0, 140, 60), width=4)
    d.line([x + 72, y + 36, x + 96, y + 16], fill=(0, 140, 60), width=4)
    # ballot papers
    for px, py, rot in [(18, 12, 0), (122, 10, 0), (128, 26, 0)]:
        d.rectangle([x + px, y + py, x + px + 18, y + py + 12], fill=(255, 255, 255),
                    outline=(150, 150, 150))
        d.line([x + px + 3, y + py + 4, x + px + 15, y + py + 4], fill=GREY, width=1)
        d.line([x + px + 3, y + py + 8, x + px + 12, y + py + 8], fill=GREY, width=1)
    # stars
    for sx, sy in [(24, 30), (140, 32), (30, 40), (134, 42)]:
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(255, 220, 90))


def art_cricket(d, x, y, w, h):
    """Green pitch, stumps, bat, red ball, scoreboard strip."""
    d.rectangle([x, y, x + w, y + h], fill=(90, 160, 90))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(60, 120, 60))
    # pitch
    d.rectangle([x + 56, y + 6, x + 104, y + h - 6], fill=(220, 200, 150))
    # stumps
    for sx in (118, 124, 130):
        d.line([x + sx, y + 12, x + sx, y + 26], fill=(250, 220, 120), width=3)
    d.line([x + 118, y + 11, x + 132, y + 11], fill=(250, 220, 120), width=2)
    # bat + ball
    d.polygon([(x + 70, y + 14), (x + 78, y + 12), (x + 88, y + 30), (x + 80, y + 32)],
              fill=(200, 160, 100))
    d.ellipse([x + 138, y + 30, x + 148, y + 40], fill=(179, 35, 27))
    # boundary rope + crowd dots
    for cx in range(8, w - 8, 14):
        d.ellipse([x + cx, y + h - 13, x + cx + 6, y + h - 7],
                  fill=[(255, 255, 255), (250, 200, 80), (200, 60, 60)][cx % 3])


def art_f1(d, x, y, w, h):
    """Red F1 car, checkered flag, track, speed lines."""
    d.rectangle([x, y, x + w, y + h], fill=(40, 44, 60))
    d.rectangle([x, y + h - 12, x + w, y + h], fill=(60, 60, 66))
    for i in range(6):
        d.line([x + 8 + i * 24, y + h - 6, x + 20 + i * 24, y + h - 6],
               fill=(255, 220, 90), width=2)
    # speed lines
    for sy in (10, 18, 26):
        d.line([x + 10, y + sy, x + 44, y + sy], fill=(140, 150, 180), width=2)
    # car body
    d.polygon([(x + 46, y + 30), (x + 66, y + 22), (x + 118, y + 22), (x + 138, y + 30),
               (x + 138, y + 36), (x + 46, y + 36)], fill=(200, 30, 30))
    d.polygon([(x + 66, y + 22), (x + 76, y + 12), (x + 104, y + 12), (x + 112, y + 22)],
              fill=(160, 20, 20))
    d.ellipse([x + 62, y + 32, x + 78, y + 46], fill=INK)
    d.ellipse([x + 112, y + 32, x + 128, y + 46], fill=INK)
    d.ellipse([x + 66, y + 35, x + 74, y + 43], fill=(180, 180, 180))
    d.ellipse([x + 116, y + 35, x + 124, y + 43], fill=(180, 180, 180))
    # checkered flag
    d.line([x + 146, y + 6, x + 146, y + 34], fill=(255, 255, 255), width=2)
    for r in range(2):
        for c in range(2):
            if (r + c) % 2 == 0:
                d.rectangle([x + 146 + c * 6, y + 6 + r * 6, x + 152 + c * 6, y + 12 + r * 6],
                            fill=INK)
    d.rectangle([x + 146, y + 6, x + 158, y + 18], outline=(255, 255, 255), width=1)


def art_power(d, x, y, w, h):
    """Dark city blocks, pylon, dim windows, one lit window."""
    d.rectangle([x, y, x + w, y + h], fill=(52, 44, 60))
    # buildings
    for bx, bw, bh in [(6, 34, 30), (46, 28, 38), (80, 36, 26), (122, 30, 34)]:
        d.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(24, 22, 34))
        for wy in range(y + h - bh + 5, y + h - 5, 9):
            for wx in range(bx + 4, bx + bw - 4, 9):
                d.rectangle([x + wx, wy, x + wx + 4, wy + 5], fill=(60, 58, 70))
    # one lit window
    d.rectangle([x + 88, y + h - 20, x + 94, y + h - 13], fill=(250, 210, 110))
    # pylon
    d.line([x + 128, y + 6, x + 122, y + h - 10], fill=INK, width=3)
    d.line([x + 128, y + 6, x + 134, y + h - 10], fill=INK, width=3)
    d.line([x + 118, y + 16, x + 138, y + 16], fill=INK, width=2)
    d.line([x + 122, y + 26, x + 134, y + 26], fill=INK, width=2)
    # wires
    d.line([x, y + 8, x + 122, y + 16], fill=(120, 118, 130), width=1)
    d.line([x + 134, y + 16, x + w, y + 8], fill=(120, 118, 130), width=1)


def art_nvidia(d, x, y, w, h):
    """Falling red chart line over bars, chip square."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 244, 230))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(230, 220, 200))
    # bars
    bars = [30, 26, 34, 24, 18, 12]
    for i, bh in enumerate(bars):
        d.rectangle([x + 12 + i * 16, y + h - 8 - bh, x + 24 + i * 16, y + h - 8],
                    fill=(120, 160, 90) if i < 3 else (179, 35, 27))
    # falling line
    pts = [(x + 12, y + 8), (x + 44, y + 14), (x + 76, y + 12), (x + 108, y + 24),
           (x + 140, y + 34)]
    d.line(pts, fill=(179, 35, 27), width=3)
    d.polygon([(x + 140, y + 34), (x + 148, y + 30), (x + 144, y + 40)], fill=(179, 35, 27))
    # chip
    d.rectangle([x + 118, y + 6, x + 142, y + 26], fill=(31, 78, 121))
    d.rectangle([x + 124, y + 12, x + 136, y + 20], fill=(255, 255, 255))
    for px in (122, 130, 138):
        d.line([x + px, y + 2, x + px, y + 6], fill=(31, 78, 121), width=2)
        d.line([x + px, y + 26, x + px, y + 30], fill=(31, 78, 121), width=2)


def art_anthropic(d, x, y, w, h):
    """Rising-then-falling bars, IPO bell, starburst."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 60, 90))
    # bars
    bars = [10, 16, 26, 34, 22, 16]
    for i, bh in enumerate(bars):
        d.rectangle([x + 10 + i * 15, y + h - 8 - bh, x + 21 + i * 15, y + h - 8],
                    fill=(90, 180, 120) if i < 4 else (255, 120, 90))
    # bell
    d.pieslice([x + 108, y + 8, x + 138, y + 34], 180, 360, fill=(250, 200, 80))
    d.rectangle([x + 106, y + 32, x + 140, y + 36], fill=(250, 200, 80))
    d.ellipse([x + 120, y + 36, x + 126, y + 42], fill=(250, 200, 80))
    # starburst
    for i in range(6):
        ang = i * 3.14159 / 3
        ex = x + 146 + int(8 * __import__("math").cos(ang))
        ey = y + 10 + int(8 * __import__("math").sin(ang))
        d.line([x + 146, y + 10, ex, ey], fill=(255, 220, 120), width=2)


def art_bolsonaro(d, x, y, w, h):
    """Hospital: cross, monitor line, bed, flag stripe."""
    d.rectangle([x, y, x + w, y + h], fill=(235, 245, 240))
    # flag stripe (Brazil green/yellow)
    d.rectangle([x, y, x + w, y + 6], fill=(0, 140, 60))
    d.rectangle([x, y + 6, x + w, y + 10], fill=(250, 200, 60))
    # cross
    d.rectangle([x + 14, y + 16, x + 22, y + 36], fill=(179, 35, 27))
    d.rectangle([x + 8, y + 22, x + 28, y + 30], fill=(179, 35, 27))
    # monitor
    d.rectangle([x + 44, y + 12, x + 108, y + 32], fill=(20, 30, 40))
    d.line([(x + 48, y + 24), (x + 60, y + 24), (x + 66, y + 16), (x + 72, y + 30),
            (x + 78, y + 24), (x + 104, y + 24)], fill=(90, 220, 120), width=2)
    # bed
    d.rectangle([x + 44, y + 36, x + 118, y + 42], fill=(120, 140, 160))
    d.line([x + 48, y + 42, x + 48, y + h - 4], fill=(120, 140, 160), width=2)
    d.line([x + 114, y + 42, x + 114, y + h - 4], fill=(120, 140, 160), width=2)
    d.ellipse([x + 122, y + 16, x + 140, y + 34], fill=(232, 190, 150))
    d.rectangle([x + 120, y + 34, x + 142, y + 42], fill=(255, 255, 255))


def art_gaza(d, x, y, w, h):
    """Gaza skyline at dusk, aid van, smoke column."""
    for i in range(h):
        t = i / h
        d.line([x, y + i, x + w, y + i],
               fill=(int(240 - 60 * t), int(200 - 40 * t), int(150 - 20 * t)))
    # buildings
    for bx, bw, bh in [(4, 30, 26), (38, 26, 34), (68, 32, 22), (104, 28, 30), (136, 22, 24)]:
        d.rectangle([x + bx, y + h - 12 - bh, x + bx + bw, y + h - 12], fill=(110, 90, 80))
        for wy in range(y + h - 8 - bh, y + h - 14, 8):
            for wx in range(bx + 4, bx + bw - 4, 8):
                d.rectangle([x + wx, wy, x + wx + 3, wy + 4], fill=(250, 220, 140))
    # smoke column
    d.ellipse([x + 76, y + 2, x + 92, y + 14], fill=(90, 85, 80))
    d.ellipse([x + 82, y + 0, x + 96, y + 10], fill=(110, 105, 100))
    # aid van
    d.rectangle([x + 8, y + h - 12, x + 52, y + h - 2], fill=(255, 255, 255),
                outline=INK, width=1)
    d.rectangle([x + 52, y + h - 10, x + 64, y + h - 2], fill=(220, 220, 220),
                outline=INK, width=1)
    d.ellipse([x + 16, y + h - 4, x + 24, y + h + 2], fill=INK)
    d.ellipse([x + 52, y + h - 4, x + 60, y + h + 2], fill=INK)
    d.text((x + 18, y + h - 11), "AID", font=SANS_B(7), fill=RED)


def art_schumer(d, x, y, w, h):
    """Capitol dome, ballot slip, two arrows."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 215, 230))
    # dome
    d.pieslice([x + 56, y + 4, x + 104, y + 36], 180, 360, fill=(240, 240, 235))
    d.rectangle([x + 56, y + 34, x + 104, y + h - 6], fill=(240, 240, 235))
    d.rectangle([x + 48, y + h - 10, x + 112, y + h - 6], fill=(200, 200, 195))
    d.line([x + 80, y + 2, x + 80, y + 8], fill=INK, width=2)
    for cx in range(60, 104, 10):
        d.rectangle([x + cx, y + 40, x + cx + 4, y + 46], fill=(120, 130, 140))
    # ballot slip
    d.rectangle([x + 116, y + 12, x + 146, y + 34], fill=(255, 255, 255),
                outline=INK, width=1)
    d.line([x + 120, y + 18, x + 126, y + 24], fill=(0, 140, 60), width=2)
    d.line([x + 126, y + 24, x + 140, y + 14], fill=(0, 140, 60), width=2)
    # arrows (two candidates)
    d.line([x + 12, y + 14, x + 40, y + 14], fill=RED, width=3)
    d.polygon([(x + 40, y + 10), (x + 48, y + 14), (x + 40, y + 18)], fill=RED)
    d.line([x + 12, y + 26, x + 40, y + 26], fill=(31, 78, 121), width=3)
    d.polygon([(x + 40, y + 22), (x + 48, y + 26), (x + 40, y + 30)], fill=(31, 78, 121))


# ---------------------------------------------------------------- world map
# Continent polygons as (lon, lat) lists, equirectangular.
CONTINENTS = {
    "NA": [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-110, 68), (-95, 69),
           (-85, 66), (-82, 70), (-75, 72), (-65, 60), (-55, 52), (-60, 47),
           (-70, 42), (-75, 35), (-80, 32), (-84, 30), (-90, 21), (-97, 16),
           (-105, 20), (-114, 28), (-122, 37), (-124, 48), (-135, 58), (-152, 58),
           (-162, 58), (-168, 66)],
    "GL": [(-45, 60), (-32, 68), (-22, 70), (-30, 76), (-55, 76), (-58, 70)],
    "SA": [(-78, 7), (-72, 11), (-62, 9), (-52, 5), (-44, -3), (-35, -8),
           (-38, -15), (-41, -22), (-48, -28), (-55, -35), (-62, -41), (-68, -50),
           (-70, -54), (-73, -50), (-73, -40), (-71, -30), (-70, -18), (-77, -12),
           (-80, -4), (-78, 7)],
    "AF": [(-17, 15), (-12, 27), (-6, 35), (10, 37), (20, 32), (30, 31),
           (35, 28), (43, 12), (51, 11), (48, 2), (40, -5), (40, -15),
           (35, -26), (28, -33), (19, -35), (15, -27), (12, -18), (13, -10),
           (9, 4), (-8, 5), (-15, 11)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (4, 53), (8, 57),
           (6, 60), (10, 62), (14, 66), (20, 70), (28, 71), (35, 68),
           (42, 66), (45, 60), (40, 55), (35, 50), (30, 46), (28, 44),
           (23, 40), (22, 37), (19, 41), (12, 44), (8, 44), (3, 42),
           (-1, 37), (-9, 37)],
    "AS": [(30, 68), (45, 68), (60, 69), (75, 72), (90, 75), (105, 77),
           (120, 73), (135, 72), (150, 70), (162, 66), (175, 66), (178, 64),
           (170, 60), (162, 58), (158, 52), (150, 59), (142, 54), (142, 45),
           (140, 40), (135, 35), (130, 33), (127, 35), (122, 31), (120, 28),
           (114, 22), (108, 18), (105, 9), (100, 7), (98, 12), (94, 16),
           (91, 22), (88, 21), (85, 19), (80, 13), (77, 8), (75, 12),
           (72, 20), (68, 22), (62, 25), (57, 26), (54, 26), (50, 29),
           (48, 30), (44, 29), (42, 31), (36, 36), (33, 39), (30, 41),
           (28, 45), (30, 52), (30, 60), (30, 68)],
    "OC": [(113, -22), (114, -30), (115, -35), (120, -34), (126, -32), (132, -32),
           (135, -35), (140, -38), (146, -39), (150, -37), (153, -27), (150, -22),
           (146, -19), (142, -11), (137, -12), (132, -11), (126, -14), (122, -17),
           (118, -20), (113, -22)],
}

# story pins: (number, lat, lon)
PINS = [
    (1, 36.9, 30.7), (2, 26.2, 50.6), (3, 50.4, 30.5), (4, 59.5, 24.0),
    (5, 22.3, 114.2), (6, -41.3, 174.8), (7, 36.1, -115.1), (8, 35.7, 51.4),
    (9, 40.7, -74.0), (10, 41.6, -73.0), (11, -15.8, -47.9), (12, 31.5, 34.5),
    (13, 38.9, -77.0),
]


def _in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > lat) != (y2 > lat):
            xin = x1 + (lat - y1) * (x2 - x1) / (y2 - y1)
            if lon < xin:
                inside = not inside
    return inside


def draw_map(d, x, y, w, h):
    """Dotted world map with numbered pins."""
    d.rectangle([x, y, x + w, y + h], fill=(214, 230, 238))
    lon0, lon1, lat0, lat1 = -170.0, 190.0, 80.0, -60.0
    step = 6
    for gy in range(y + 3, y + h - 2, step):
        lat = lat0 + (gy - y) / h * (lat1 - lat0)
        for gx in range(x + 3, x + w - 2, step):
            lon = lon0 + (gx - x) / w * (lon1 - lon0)
            if any(_in_poly(lon, lat, poly) for poly in CONTINENTS.values()):
                d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=(178, 152, 110))
    # graticule ticks
    for gx in range(x, x + w + 1, 62):
        d.line([gx, y + h - 4, gx, y + h], fill=(150, 170, 185), width=1)
    # pins
    for num, lat, lon in PINS:
        px = x + (lon - lon0) / (lon1 - lon0) * w
        py = y + (lat0 - lat) / (lat0 - lat1) * h
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        f = SANS_B(8)
        t = str(num)
        d.text((px - d.textlength(t, font=f) / 2, py - 5), t, font=f, fill=(255, 255, 255))
    d.text((x + 4, y + h - 12), "Pins match story numbers.",
           font=SANS_I(8), fill=(60, 80, 100))


# ---------------------------------------------------------------- stories
HEROES = [
    dict(kicker="COP31: FINAL TEXT", num=1, place="ANTALYA, TÜRKIYE", topic="CLIMATE",
         tag="REPORTED", tagbg=NAVY,
         head="Climate deal lands with no mention of fossil fuels",
         deck=("The final text keeps the 35% electricity-by-2035 goal, drops the $120bn "
               "adaptation target and is the first to admit 1.5\u00b0C will be overshot. "
               "Approval stalled Sunday, two days overdue."),
         src="(Reuters, AP)", art="cop31"),
    dict(kicker="CLAIM VS DENIAL", num=2, place="MANAMA, BAHRAIN", topic="IRAN",
         tag="CLAIM", tagbg=RED,
         head="Iran claims two US radars hit; Bahrain denies it",
         deck=("The IRGC says it destroyed two Patriot radars on Saturday night. Bahrain "
               "answered on Sunday: a civilian industrial site was hit \u2014 a fire, "
               "no injuries."),
         src="(Al Jazeera, Reuters)", art="bahrain"),
    dict(kicker="186 DRONES OVERNIGHT", num=3, place="KYIV, UKRAINE", topic="WAR",
         tag="REPORTED", tagbg=NAVY,
         head="Russia fires 186 drones; a Kyiv block is destroyed",
         deck=("Air defences downed or jammed 161 of 186 strike drones. One destroyed a "
               "five-storey block in Dymer, near Kyiv; six Ukrainian drones bound for "
               "Moscow were downed."),
         src="(Ukrainian Air Force, Reuters)", art="kyiv"),
]

MIDS = [
    dict(kicker="SHIP ABLAZE", num=4, place="GULF OF FINLAND", topic="SEA",
         tag="ONGOING", tagbg=(150, 90, 0),
         head="Russian cargo ship still burning",
         deck="Hit Saturday, still burning at anchor Sunday; 16 crew safe.",
         src="(Reuters)", art="sparta"),
    dict(kicker="856 CANDIDATES", num=5, place="HONG KONG", topic="POLITICS",
         tag="REPORTED", tagbg=NAVY,
         head="Hong Kong elects its Election Committee",
         deck="856 candidates, 723 seats; turnout 93.55%.",
         src="(SCMP)", art="hk"),
    dict(kicker="720/9 DECLARED", num=6, place="WELLINGTON", topic="CRICKET",
         tag="REPORTED", tagbg=NAVY,
         head="India post 720/9, a record in NZ",
         deck="Rahul 136, Pant 128; a 352-run lead on Day 4.",
         src="(ESPNcricinfo)", art="cricket"),
    dict(kicker="VERSTAPPEN WINS", num=7, place="LAS VEGAS", topic="FORMULA 1",
         tag="REPORTED", tagbg=NAVY,
         head="Verstappen wins the Las Vegas GP",
         deck="Norris +0.639, Piastri third. His 75th win.",
         src="(FIA)", art="f1"),
    dict(kicker="POWER CUTS", num=8, place="TEHRAN, IRAN", topic="ENERGY",
         tag="REPORTED", tagbg=NAVY,
         head="Iran begins rationing electricity",
         deck="Rolling cuts up to two hours a day.",
         src="(Wires)", art="power"),
    dict(kicker="WORST SINCE 2008", num=9, place="NEW YORK", topic="MARKETS",
         tag="REPORTED", tagbg=NAVY,
         head="Nvidia sheds $811bn in a week",
         deck="A week of falls, tallied in Sunday reports.",
         src="(Clearview Politics)", art="nvidia"),
    dict(kicker="PROJECT LANTERN", num=10, place="NEW YORK", topic="TECH",
         tag="REPORTED", tagbg=NAVY,
         head="Anthropic slides 8.5% after debut",
         deck="22 underwriters; six-month non-competes.",
         src="(Reuters)", art="anthropic"),
    dict(kicker="IN INTENSIVE CARE", num=11, place="BRAS\u00cdLIA", topic="POLITICS",
         tag="REPORTED", tagbg=NAVY,
         head="Bolsonaro in intensive care in Bras\u00edlia",
         deck="Bowel obstruction; stable, surgery possible.",
         src="(Reuters)", art="bolsonaro"),
    dict(kicker="CEASEFIRE FRAYS", num=12, place="GAZA", topic="CEASEFIRE",
         tag="REPORTED", tagbg=NAVY,
         head="Two die of wounds in Gaza; ceasefire frays",
         deck="Two die of wounds; talks open; UN warns.",
         src="(WAFA, Reuters)", art="gaza"),
    dict(kicker="LEADERSHIP RACE", num=13, place="WASHINGTON", topic="POLITICS",
         tag="REPORTED", tagbg=NAVY,
         head="Van Hollen to challenge Schumer",
         deck="Secret vote on 1 Dec; first contested race since 1994.",
         src="(Reuters)", art="schumer"),
]

BRIEFS = [
    (14, "TURIN", "Zverev v Alcaraz in tonight's ATP final, 18:00 CET.", "ATP"),
    (15, "LONDON", "Will Jacks out of T20 tour, broken hand.", "Reuters"),
    (16, "MANILA", "Transport group Manibela to strike on 23\u201324 Nov.", "GMA"),
    (17, "CEBU", "Fire on an Ormoc-bound vessel; no casualties.", "GMA"),
    (18, "MANILA", "Gatchalian: 2027 budget will be ratified.", "GMA"),
    (19, "MANILA", "Guterres cites Ifugao terraces in fossil-fuel call.", "GMA"),
    (20, "NEW DELHI", "BJP MP Ramrao Wadkute dies at 72.", "EIN"),
    (21, "NEW DELHI", "Cricketer Chahal joins the BJP's OBC Morcha.", "EIN"),
    (22, "NEW DELHI", "Nepal PM Shah begins a state visit.", "dainikjagran"),
    (23, "APIA", "Cyclone Xavier weakens north of Samoa.", "Wires"),
    (24, "ABU DHABI", "UAE moves oil past Iran as Hormuz bites.", "Wires"),
    (25, "DUBAI", "British swimmer braves the Strait of Hormuz.", "Wires"),
    (26, "BRUSSELS", "EU floats a digital-tax plan amid budget rows.", "Wires"),
    (27, "SAN FRANCISCO", "OpenRouter drops three providers.", "Wires"),
    (28, "LONDON", "Antidepressants: 115 trials, 30,000+ patients.", "Lancet"),
    (29, "SYDNEY", "Australia, NZ, US navies in Exercise Dugong.", "Wires"),
    (30, "WASHINGTON", "Watchdog: \u201ccascade of problems\u201d at ICE.", "Wires"),
    (31, "MANILA", "Comelec projects 4 million new voters for 2028.", "GMA"),
    (32, "WASHINGTON", "CBO: Navy shipbuilding $54bn a year.", "CBO"),
    (33, "BOUGAINVILLE", "Australia, NZ rush aid as El Ni\u00f1o looms.", "Wires"),
    (34, "MANILA", "Marcos clarifies Trump claim; ICC rebuffs Duterte.", "GMA"),
    (35, "NEW DELHI", "India and China conclude commander talks.", "Wires"),
    (36, "MASTUNG", "China renews UN bid on BLA; 15 killed.", "Wires"),
    (37, "WORLD", "Ghostscript flaw escapes sandbox.", "CVE-2026-125396"),
]

ART = dict(cop31=art_cop31, bahrain=art_bahrain, kyiv=art_kyiv, sparta=art_sparta,
           hk=art_hk, cricket=art_cricket, f1=art_f1, power=art_power,
           nvidia=art_nvidia, anthropic=art_anthropic, bolsonaro=art_bolsonaro,
           gaza=art_gaza, schumer=art_schumer)


# ---------------------------------------------------------------- page
def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    warns = []

    # top bar
    d.rectangle([0, 0, W, 22], fill=NAVY)
    d.text((M, 5), "THE WORLD IN ONE DAY", font=SANS_B(11), fill=(255, 255, 255))
    rt = "37 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - M - d.textlength(rt, font=SANS_B(11)), 5), rt, font=SANS_B(11),
           fill=(255, 255, 255))

    # masthead
    center(d, W // 2, 26, "Sunday 22 November 2026", SERIF(58), INK)
    center(d, W // 2, 86,
           "COP31's final text names no fossil fuels \u00b7 Iran's radar claim meets "
           "Bahrain's denial \u00b7 186 drones over Ukraine in the night",
           SERIF_I(15), RED)
    d.rectangle([M, 102, W - M, 105], fill=INK)

    # stats strip
    sw = CW / 6
    for i, (num, cap) in enumerate(STATS):
        x0 = M + i * sw
        if i:
            d.line([x0, 110, x0, 140], fill=(190, 185, 170), width=1)
        center(d, x0 + sw / 2, 108, num, SERIF(30), RED)
        lines = wrap(cap, SANS(9), sw - 12, d)
        if len(lines) > 2:
            warns.append(f"stat {num}: {len(lines)} lines")
        draw_lines(d, x0 + 6, 140, lines, SANS(9), INK, 11)
    d.rectangle([M, 166, W - M, 167], fill=INK)

    # region bar
    total = sum(c for _, c, _ in REGIONS)
    x = M
    for name, cnt, col in REGIONS:
        seg = CW * cnt / total
        d.rectangle([x, 170, x + seg - 1, 185], fill=col)
        lab = f"{name} {cnt}"
        f = SANS_B(9)
        if d.textlength(lab, font=f) <= seg - 6:
            d.text((x + 4, 173), lab, font=f, fill=(255, 255, 255))
        x += seg

    # UTC timeline
    d.rectangle([M, 188, W - M, 204], fill=INK)
    d.text((M + 6, 191), "THE DAY IN UTC", font=SANS_B(10), fill=(255, 220, 90))
    tx = M + 108
    for tm, ev in TIMELINE:
        d.text((tx, 191), tm, font=SANS_B(10), fill=(255, 255, 255))
        tw = d.textlength(tm, font=SANS_B(10))
        d.text((tx + tw + 4, 191), ev, font=SANS(10), fill=(220, 220, 220))
        tx += tw + 4 + d.textlength(ev, font=SANS(10)) + 16
    if tx > W - M:
        warns.append(f"timeline overflows by {tx - (W - M)}px")

    # heroes
    HY, HH = 208, 100
    for i, st in enumerate(HEROES):
        x0 = HERO_X[i]
        ART[st["art"]](d, x0, HY, COL, HH)
        d.rectangle([x0, HY, x0 + COL, HY + HH], outline=INK, width=1)
        # text block
        y = HY + HH + 8
        d.text((x0, y), f"{st['num']} {st['place']} \u00b7 {st['topic']}",
               font=SANS_B(10), fill=RED)
        tag(d, x0 + COL - 78, y - 1, st["tag"], (255, 255, 255), st["tagbg"])
        y += 16
        hl = wrap(st["head"], SERIF(16), COL, d)
        if len(hl) > 2:
            warns.append(f"hero {st['num']} headline: {len(hl)} lines")
        y = draw_lines(d, x0, y, hl, SERIF(16), INK, 19)
        y += 2
        dl = wrap(st["deck"], SANS(10), COL, d)
        if len(dl) > 3:
            warns.append(f"hero {st['num']} deck: {len(dl)} lines")
        y = draw_lines(d, x0, y, dl, SANS(10), INK, 13)
        d.text((x0, y + 1), st["src"], font=SANS_I(9), fill=GREY)

    # mids: two rows of five
    MIDW = 188
    MIDX = [M + i * (MIDW + 11) for i in range(5)]
    for row in range(2):
        ay = 428 + row * 122
        ty = ay + 50
        for col in range(5):
            st = MIDS[row * 5 + col]
            x0 = MIDX[col]
            ART[st["art"]](d, x0, ay, MIDW, 44)
            d.rectangle([x0, ay, x0 + MIDW, ay + 44], outline=INK, width=1)
            kicker(d, x0, ay, MIDW, st["kicker"], bg=RED)
            y = ty
            d.text((x0, y), f"{st['num']} {st['place']} \u00b7 {st['topic']}",
                   font=SANS_B(8), fill=RED)
            tag(d, x0 + MIDW - 62, y - 1, st["tag"], (255, 255, 255), st["tagbg"])
            y += 13
            hl = wrap(st["head"], SANS_B(11), MIDW, d)
            if len(hl) > 2:
                warns.append(f"mid {st['num']} headline: {len(hl)} lines")
            y = draw_lines(d, x0, y, hl, SANS_B(11), INK, 13)
            dl = wrap(st["deck"], SANS(9), MIDW, d)
            if len(dl) > 2:
                warns.append(f"mid {st['num']} deck: {len(dl)} lines")
            y = draw_lines(d, x0, y, dl, SANS(9), INK, 11)
            d.text((x0, y + 1), st["src"], font=SANS_I(8), fill=GREY)

    # bottom section header
    d.text((M, 682), "WHERE IT HAPPENED", font=SANS_B(10), fill=INK)
    d.text((M + 118, 682), "pins match story numbers", font=SANS_I(9), fill=GREY)
    d.rectangle([344, 680, W - M, 696], fill=NAVY)
    d.text((352, 683), "ALSO ON SUNDAY 22 NOVEMBER \u2014 24 MORE STORIES",
           font=SANS_B(10), fill=(255, 255, 255))

    # map + briefs
    draw_map(d, M, 700, 310, 242)
    d.rectangle([M, 700, M + 310, 700 + 242], outline=INK, width=1)
    cols = [BRIEFS[:12], BRIEFS[12:]]
    for ci, group in enumerate(cols):
        bx = 344 + ci * 332
        y = 704
        for num, city, text, src in group:
            line = f"{num}. {city} \u2014 {text} ({src})"
            f = SANS(10)
            if d.textlength(line, font=f) > 324:
                warns.append(f"brief {num} too long ({d.textlength(line, font=f):.0f}px)")
            d.text((bx, y), line, font=f, fill=INK)
            y += 20

    # DATE CHECK
    d.rectangle([M, 946, W - M, 992], outline=RED, width=2)
    dc_lines = wrap(DATE_CHECK, SANS(9), CW - 16, d)
    if len(dc_lines) > 4:
        warns.append(f"DATE CHECK: {len(dc_lines)} lines")
    draw_lines(d, M + 8, 950, dc_lines, SANS(9), INK, 11)

    # footer
    d.text((M, 995), FOOTER_SOURCES, font=SANS(8), fill=GREY)
    d.text((M, 1004), FOOTER_LEGEND, font=SANS(8), fill=GREY)

    # bottom bar
    d.rectangle([0, 1014, W, H], fill=NAVY)
    d.text((M, 1015), "THE WORLD IN ONE DAY", font=SANS_B(8), fill=(255, 255, 255))
    rb = "SUNDAY 22 NOVEMBER 2026 \u00b7 ONE PAGE"
    d.text((W - M - d.textlength(rb, font=SANS_B(8)), 1015), rb, font=SANS_B(8),
           fill=(255, 255, 255))

    img.save(os.path.join(HERE, "entry.png"), optimize=True)
    print("saved entry.png")
    for w_ in warns:
        print("WARN:", w_)
    print("warnings:", len(warns))


if __name__ == "__main__":
    draw()
