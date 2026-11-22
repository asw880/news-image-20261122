#!/usr/bin/env python3
"""Draw the v3 front page for make.fun news-image-20261122.

One day's world news, Sunday 22 November 2026, as a single 1024x1024
front page. All content comes from the revised v3 brief: COP31 ends with
NO DEAL, Bahrain, 186 drones over Ukraine, and 34 further stories.
Every illustration is drawn in code (shapes only, no photos).
System fonts only (Liberation).
"""
import hashlib
import math
import os
from datetime import datetime, timezone

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 18  # outer margin
FONT_DIR = "/usr/share/fonts/truetype/liberation"

# ---------------------------------------------------------------- colours
PAPER = (247, 243, 232)
NAVY = (26, 43, 74)
NAVY_DK = (18, 30, 54)
RED = (179, 35, 42)
RED_DK = (140, 25, 32)
INK = (26, 26, 26)
MUTED = (90, 90, 90)
RULE = (26, 43, 74)
CARD_BG = (255, 255, 255)
CARD_LINE = (210, 205, 190)
DATE_BG = (253, 238, 238)
DATE_LINE = (179, 35, 42)

REGION_COLOURS = {
    "AP": (217, 119, 6),    # Asia-Pacific, amber
    "EU": (15, 118, 110),   # Europe, teal
    "AM": (29, 78, 216),    # Americas, blue
    "ME": (179, 35, 42),    # Middle East, red
    "OC": (124, 58, 237),   # Oceania, purple
    "AF": (21, 128, 61),    # Africa, green
}
REGION_LABELS = [
    ("AP", "ASIA-PACIFIC", 11),
    ("EU", "EUROPE", 9),
    ("AM", "AMERICAS", 9),
    ("ME", "MIDDLE EAST", 4),
    ("OC", "OCEANIA", 3),
    ("AF", "AFRICA", 1),
]  # dateline counts; total 37

# ---------------------------------------------------------------- fonts
def F(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)

SERIF_B = "LiberationSerif-Bold.ttf"
SERIF = "LiberationSerif-Regular.ttf"
SERIF_I = "LiberationSerif-Italic.ttf"
SANS_B = "LiberationSans-Bold.ttf"
SANS = "LiberationSans-Regular.ttf"

# ---------------------------------------------------------------- text helpers
def wrap(text, font, max_w):
    """Greedy word wrap; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if font.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, font, fill, max_w, leading, max_lines=None):
    """Draw wrapped text; returns (lines_used, y_after)."""
    lines = wrap(text, font, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return len(lines), y


def centre(d, cx, y, text, font, fill):
    d.text((cx, y), text, font=font, fill=fill, anchor="ma")


def tag_chip(d, x, y, text, font, bg=RED, fg=(255, 255, 255)):
    """Small filled tag, top-left at (x, y); returns its width."""
    tw = font.getlength(text) + 12
    th = font.getbbox("Ag")[3] - font.getbbox("Ag")[1] + 8
    d.rectangle([x, y, x + tw, y + th], fill=bg)
    d.text((x + 6, y + 4), text, font=font, fill=fg)
    return tw, th

# ---------------------------------------------------------------- content
HEROES = [
    dict(num=1, city="ANTALYA, TÜRKIYE", cat="CLIMATE", tag="NO DEAL",
         cert="REPORTED", art="cop31",
         head="COP31 ends with no deal",
         body="The summit collapsed on Sunday after the EU and others refused "
              "to adopt the text; President Kurum told the closing session the "
              "decisions were not adopted. The draft named no fossil fuels, "
              "dropped the $120bn target and conceded 1.5°C will be overshot. "
              "(Reuters)"),
    dict(num=2, city="MANAMA, BAHRAIN", cat="IRAN", tag="2 RADARS?",
         cert="CLAIM", art="bahrain",
         head="Iran claims two US radars hit; Bahrain denies it",
         body="The IRGC says it hit Patriot radars at Al-Riffa and Awali "
              "Sakhir in 'Ya Umm al-Banin', after two US drones entered "
              "Iranian airspace. Bahrain says defences intercepted the "
              "attacks; debris, minor damage, no casualties. "
              "(Ynet; Sepah News)"),
    dict(num=3, city="KYIV, UKRAINE", cat="WAR", tag="186 DRONES",
         cert="REPORTED", art="ukraine",
         head="186 drones in a night; Kyiv block hit, 8 feared buried",
         body="Russia fired 186 drones overnight; Ukraine downed or jammed "
              "161 by 08:00, including 56 of 72 jet-powered Shaheds. A "
              "five-storey block in Dymer was destroyed; 8 feared buried, "
              "14 unreachable; 30 injured. (Kyiv Independent)"),
]

MIDS = [
    dict(num=4, city="NEW YORK", cat="MARKETS", tag="~$900BN",
         head="Nvidia sheds ~$900bn; SEC opens probe",
         body="Shares -23% in the week, -14% Friday. SEC opens an "
              "accounting probe. (Reuters)", art="chart"),
    dict(num=5, city="NEW YORK", cat="AI", tag="-8.5%",
         head="Anthropic slides 8.5% after record debut",
         body="IPO total $93.5bn tops SpaceX's record. 'Project Lantern': "
              "22 underwriters. (Reuters)", art="ipo"),
    dict(num=6, city="WASHINGTON", cat="POLITICS", tag="1 DEC VOTE",
         head="Van Hollen to challenge Schumer",
         body="First contested race since 1994; vote 1 Dec. 16 back "
              "Schumer, 6 Van Hollen. (Reuters)", art="capitol"),
    dict(num=7, city="WELLINGTON", cat="CRICKET", tag="720/9",
         head="India declare 720/9, a record in NZ",
         body="Rahul 136, Pant 128; Pant's 108 sixes pass McCullum's 107. "
              "(ESPNcricinfo)", art="cricket"),
    dict(num=8, city="LAS VEGAS", cat="FORMULA 1", tag="75TH WIN",
         head="Verstappen wins the Las Vegas GP",
         body="75th win, from pole after Antonelli's penalty. Antonelli "
              "already champion. (FIA)", art="race"),
    dict(num=9, city="TEHRAN", cat="ENERGY", tag="CUTS FROM SUNDAY",
         head="Iran begins rolling blackouts",
         body="Up to 2 hrs a day, says Tavanir chief Allahdad; no national "
              "schedule. (Straits Times)", art="power"),
    dict(num=10, city="GULF OF FINLAND", cat="SEA", tag="STILL BURNING",
         head="Sparta II still burning off Finland",
         body="121-m sanctioned vessel off Loviisa; 16 crew safe. Finland "
              "blames Ukraine. (Reuters)", art="ship"),
    dict(num=11, city="HONG KONG", cat="ELECTION", tag="98.79%",
         head="Hong Kong vote sets record turnout",
         body="98.79% (5,640 of 5,709) pick 723 seats — beats 89.77% in "
              "2021. (China Daily)", art="ballot"),
    dict(num=12, city="BRASÍLIA", cat="HEALTH", tag="STILL IN ICU",
         head="Bolsonaro still in intensive care",
         body="Admitted Friday, ICU Saturday; bowel obstruction, stable, "
              "no discharge date. (Reuters)", art="hospital"),
    dict(num=13, city="GAZA", cat="CEASEFIRE", tag="TALKS SOUGHT",
         head="Hamas seeks urgent talks",
         body="Two died of wounds in Al-Mawasi; Health Ministry warns on "
              "blocked supplies. (Anadolu)", art="talks"),
]

BRIEFS = [
    (14, "TURIN", "Zverev meets Alcaraz in tonight's ATP final, 18:00 CET; "
     "$5.17m. (tennis365)", 45.07, 7.69),
    (15, "LONDON", "Will Jacks out of England's T20 tour of Australia, "
     "broken hand. (Reuters)", 51.5, -0.13),
    (16, "MANILA", "Transport group Manibela to strike 23–24 Nov. (GMA)",
     14.6, 121.0),
    (17, "LIVERPOOL", "United visit Anfield tonight, 16:30 GMT. No result "
     "yet. (Sky Sports)", 53.4, -3.0),
    (18, "MANILA", "Senate chief Gatchalian confident the 2027 budget will "
     "pass. (GMA)", 14.6, 121.0),
    (19, "MANILA", "UN chief Guterres cites Ifugao terraces in a call to "
     "end fossil fuels. (GMA)", 14.6, 121.0),
    (20, "NEW DELHI", "BJP MP Ramrao Wadkute dies at 72 after a cardiac "
     "arrest. (EIN)", 28.6, 77.2),
    (21, "APIA", "Tropical Cyclone Xavier weakens north of Samoa. (NWS)",
     -13.85, -171.75),
    (22, "NEW DELHI", "Nepal PM Shah begins a two-day state visit; meets "
     "Modi. (dainikjagran)", 28.6, 77.2),
    (23, "BOUGAINVILLE", "Australia and NZ rush aid as an El Niño threat "
     "looms. (EIN)", -6.2, 155.4),
    (24, "CEBU", "Fire on an Ormoc-bound vessel from Cebu; no casualties. "
     "(GMA)", 10.3, 123.9),
    (25, "NAIROBI", "Kenya floods kill six, hit 1,141 households. "
     "(Daily Nation)", -1.29, 36.82),
    (26, "SAN FRANCISCO", "OpenRouter drops three providers after a "
     "canary-token probe. (The Hacker News)", 37.77, -122.42),
    (27, "MANILA", "Marcos clarifies Trump trade claim; ICC rebuffs "
     "Duterte evidence bid. (GMA)", 14.6, 121.0),
    (28, "NEW DELHI", "Cricketer Chahal joins the BJP's OBC Morcha. (EIN)",
     28.6, 77.2),
    (29, "NEW DELHI", "India and China conclude Corps Commander talks on "
     "the Arunachal frontier. (Indian Express)", 28.2, 94.7),
    (30, "BERLIN", "IG Metall calls 23,000 workers to a 24-hour strike on "
     "Monday. (Reuters)", 52.52, 13.4),
    (31, "MANILA", "Comelec projects 4 million new voters for 2028. (GMA)",
     14.6, 121.0),
    (32, "WASHINGTON", "S&P 500 in correction as AI shares falter. "
     "(Clearview)", 38.9, -77.04),
    (33, "WASHINGTON", "Navy deployments stretch beyond 300 days, CBO "
     "says. (Clearview)", 38.9, -77.04),
    (34, "NEW YORK", "Anthropic shares close down 8.5% after a 17% debut; "
     "IPO $93.5bn. (Reuters)", 40.71, -74.0),
    (35, "KYIV", "Six Ukrainian drones headed for Moscow downed, mayor "
     "says. (Kyiv Independent)", 50.45, 30.52),
    (36, "GAZA", "Hamas seeks urgent mediator talks; UN warns ceasefire "
     "could collapse. (Anadolu)", 31.5, 34.47),
    (37, "ANTALYA", "COP31 ends with no deal, two days past its scheduled "
     "close. (Reuters)", 36.9, 30.7),
]

# (num, lat, lon) for heroes + mids, for the map pins
PIN_POINTS = [
    (1, 36.9, 30.7), (2, 26.23, 50.59), (3, 50.45, 30.52),
    (4, 40.71, -74.0), (5, 40.71, -74.0), (6, 38.9, -77.04),
    (7, -41.29, 174.78), (8, 36.17, -115.14), (9, 35.69, 51.39),
    (10, 59.9, 26.0), (11, 22.32, 114.17), (12, -15.79, -47.88),
    (13, 31.5, 34.47),
] + [(n, la, lo) for (n, _c, _t, la, lo) in BRIEFS]

STATS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or jammed by 08:00 Kyiv"),
    ("~$900bn", "Nvidia lost in a week — worst since 2008"),
    ("98.79%", "Hong Kong turnout — a record"),
    ("720/9", "India's record Test total in NZ"),
    ("2", "US Patriot radars Iran claims hit"),
]

TIMELINE = ("THE DAY IN UTC    03:00 GMT COP31 objections close  ·  "
            "06:00 GMT COP31 approval due  ·  08:00 Kyiv: 161 drones downed  ·  "
            "09:00 HK polls open  ·  16:30 GMT Liverpool–United  ·  "
            "17:00 GMT ATP final")

DATE_CHECK = ("DATE CHECK — LEFT OUT ON PURPOSE · NOT SUNDAY 22 NOVEMBER "
    "NEWS:  Gaza food-aid van strike (Sat) · Bahrain/Hormuz strikes (late "
    "Sat) · Sparta II hit (Sat) · FBI NCIC hack (Sat) · Peru M6.7 quake "
    "(Fri) · Nigeria boat capsized (Fri, toll 24 Sat) · Mass Russian strike, "
    "500+ drones & 100+ missiles (Fri) · Kryvyi Rih (Sat) · Bolsonaro ICU "
    "admission (Sat) · Denmark expels Russian attaché (Fri) · El Chapo "
    "Isidro captured (Fri) · ICJ Myanmar ruling (Thu) · Shenzhen summit "
    "(Thu) · GTA VI launch (Thu) · BepiColombo Mercury orbit (Sat) · "
    "EU–Indonesia CEPA (Sat) · UK–EU reset deal (Fri) · Mlambo-Ngcuka died "
    "(Fri) · Finland helicopter incursion (Sat) · EU budget €1.78tn (Sat) · "
    "Turkey Sözcü TV takeover (Sat)")

SOURCES = ("Sources: Reuters, Kyiv Independent, AP, AFP, BBC, The Straits "
    "Times, China Daily, ESPNcricinfo, FIA, Anadolu, WAFA, Ynet, Sepah News, "
    "GMA, EIN Presswire, Daily Nation, The Hacker News, NWS, Indian Express, "
    "Clearview, tennis365, Sky Sports.")
LEGEND = ("Every story names its outlet. Pictures and map: original, drawn "
    "in code.  CERTAINTY:  REPORTED = carried by the day's wires  ·  "
    "CLAIM = one side's account, labelled as such  ·  FORECAST = still to "
    "happen when drawn.")

# ---------------------------------------------------------------- dotted map
# Simplified continent outlines as (lon, lat) polygons.
CONTINENTS = [
    [(-168, 66), (-160, 70), (-150, 70), (-140, 70), (-130, 69), (-120, 69),
     (-110, 68), (-100, 68), (-95, 69), (-90, 68), (-85, 66), (-82, 66),
     (-80, 70), (-75, 68), (-70, 65), (-65, 60), (-60, 55), (-55, 52),
     (-55, 47), (-60, 45), (-65, 44), (-70, 42), (-74, 39), (-76, 35),
     (-80, 32), (-81, 26), (-84, 30), (-88, 30), (-90, 29), (-94, 29),
     (-97, 26), (-97, 22), (-96, 19), (-94, 18), (-91, 19), (-88, 18),
     (-86, 16), (-84, 14), (-82, 12), (-80, 10), (-79, 9), (-81, 8),
     (-83, 9), (-85, 11), (-88, 13), (-90, 14), (-92, 15), (-94, 16),
     (-97, 16), (-100, 17), (-105, 20), (-108, 23), (-111, 25), (-114, 29),
     (-117, 33), (-120, 35), (-122, 38), (-124, 42), (-125, 48), (-128, 50),
     (-132, 55), (-136, 58), (-142, 60), (-148, 61), (-154, 59), (-160, 58),
     (-164, 58), (-168, 60), (-168, 66)],
    [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-79, -10), (-77, -12),
     (-75, -15), (-72, -18), (-70, -20), (-70, -25), (-70, -30), (-72, -35),
     (-73, -40), (-74, -45), (-74, -50), (-70, -54), (-66, -55), (-65, -50),
     (-65, -45), (-62, -40), (-58, -35), (-55, -33), (-52, -32), (-48, -28),
     (-44, -23), (-40, -20), (-38, -15), (-35, -9), (-35, -6), (-38, -4),
     (-42, -3), (-45, -2), (-50, 0), (-53, 4), (-57, 6), (-60, 8),
     (-64, 10), (-68, 11), (-72, 12), (-76, 10), (-79, 9)],
    [(-10, 36), (-9, 38), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 49),
     (1, 51), (3, 53), (5, 53), (8, 55), (8, 57), (10, 59), (7, 58),
     (5, 60), (6, 62), (10, 64), (12, 66), (15, 68), (18, 69), (22, 70),
     (25, 71), (30, 70), (32, 68), (35, 67), (40, 68), (44, 68), (48, 69),
     (52, 69), (56, 69), (60, 69), (65, 70), (68, 72), (72, 72), (75, 73),
     (80, 73), (85, 74), (90, 75), (95, 76), (100, 77), (105, 77),
     (110, 74), (115, 73), (120, 73), (125, 72), (130, 72), (135, 71),
     (140, 72), (145, 72), (150, 70), (155, 69), (160, 69), (165, 67),
     (170, 67), (175, 65), (178, 65), (178, 62), (175, 60), (170, 60),
     (165, 60), (162, 56), (160, 53), (158, 52), (156, 51), (152, 59),
     (150, 60), (145, 59), (142, 55), (141, 50), (140, 45), (138, 42),
     (135, 42), (132, 43), (130, 42), (128, 38), (127, 35), (126, 36),
     (124, 38), (122, 39), (120, 35), (119, 32), (117, 28), (115, 23),
     (113, 22), (110, 20), (109, 18), (107, 15), (105, 10), (103, 8),
     (101, 7), (99, 8), (98, 10), (97, 15), (95, 16), (93, 20), (91, 22),
     (89, 22), (87, 21), (85, 19), (83, 17), (80, 15), (79, 10), (77, 8),
     (75, 12), (74, 15), (72, 20), (70, 21), (68, 23), (66, 25), (64, 25),
     (62, 25), (60, 25), (58, 25), (56, 27), (54, 27), (52, 27), (50, 29),
     (49, 30), (48, 30), (47, 30), (45, 29), (43, 28), (41, 27), (39, 24),
     (37, 22), (35, 23), (34, 27), (33, 29), (32, 31), (30, 36), (28, 36),
     (27, 37), (26, 38), (24, 37), (23, 36), (22, 37), (20, 40), (19, 41),
     (17, 40), (15, 44), (13, 45), (12, 44), (10, 44), (8, 44), (6, 43),
     (3, 43), (1, 41), (0, 39), (-2, 37), (-5, 36), (-8, 37), (-10, 36)],
    [(-6, 35), (-2, 35), (2, 36), (6, 37), (10, 37), (11, 34), (15, 32),
     (20, 32), (25, 31), (30, 31), (32, 31), (34, 29), (35, 28), (36, 25),
     (37, 22), (38, 20), (39, 18), (40, 15), (41, 13), (43, 11), (46, 11),
     (48, 11), (51, 11), (51, 10), (48, 6), (46, 3), (44, 0), (42, -2),
     (41, -4), (40, -7), (40, -10), (39, -13), (38, -16), (36, -18),
     (35, -20), (34, -23), (33, -26), (31, -29), (29, -31), (27, -33),
     (25, -34), (22, -35), (20, -35), (18, -34), (17, -32), (16, -29),
     (15, -26), (14, -22), (13, -18), (12, -14), (12, -10), (13, -6),
     (10, -3), (9, 0), (8, 4), (6, 5), (4, 6), (1, 6), (-3, 5), (-7, 4),
     (-10, 6), (-13, 8), (-15, 10), (-17, 13), (-17, 15), (-16, 18),
     (-16, 21), (-15, 24), (-14, 27), (-12, 29), (-10, 31), (-8, 33),
     (-6, 35)],
    [(113, -22), (114, -26), (115, -30), (115, -34), (118, -35), (122, -34),
     (126, -32), (129, -32), (132, -32), (134, -33), (136, -35), (138, -35),
     (140, -38), (143, -39), (146, -39), (149, -37), (150, -37), (152, -34),
     (153, -31), (153, -28), (152, -25), (150, -22), (148, -20), (146, -19),
     (144, -15), (142, -11), (142, -14), (141, -17), (140, -18), (138, -17),
     (136, -15), (135, -12), (133, -12), (131, -12), (129, -14), (127, -14),
     (125, -15), (122, -17), (120, -19), (117, -20), (114, -21), (113, -22)],
    [(-5, 50), (-4, 52), (-5, 54), (-5, 56), (-3, 58), (-2, 57), (-1, 56),
     (0, 54), (1, 52), (1, 51), (0, 50), (-2, 50), (-4, 50), (-5, 50)],
    [(130, 31), (131, 33), (133, 34), (135, 34), (137, 35), (138, 36),
     (139, 37), (140, 39), (141, 41), (141, 43), (142, 44), (144, 44),
     (145, 43), (143, 41), (142, 40), (141, 38), (140, 36), (139, 35),
     (137, 34), (135, 33), (133, 33), (131, 32), (130, 31)],
    [(95, 5), (97, 4), (99, 2), (101, 0), (103, -2), (105, -4), (107, -6),
     (110, -7), (112, -7), (114, -8), (116, -8), (119, -9), (121, -10),
     (123, -10), (125, -9), (127, -8), (129, -7), (131, -4), (133, -3),
     (135, -2), (137, -2), (139, -3), (141, -3), (141, -6), (140, -8),
     (138, -8), (136, -6), (134, -4), (132, -3), (130, -2), (128, -3),
     (126, -1), (124, 0), (122, 1), (120, 1), (118, 0), (116, 1), (114, 3),
     (112, 1), (110, 0), (108, 1), (106, 2), (104, 3), (102, 4), (100, 5),
     (98, 5), (95, 5)],
    [(167, -45), (168, -44), (170, -42), (172, -41), (174, -40), (175, -38),
     (177, -38), (178, -37), (177, -39), (175, -40), (174, -41), (173, -42),
     (171, -43), (170, -44), (168, -46), (167, -45)],
    [(44, -16), (46, -15), (48, -15), (50, -16), (50, -18), (49, -21),
     (48, -24), (46, -25), (44, -25), (43, -23), (43, -20), (43, -17),
     (44, -16)],
    [(-22, 64), (-20, 63), (-17, 63), (-14, 64), (-14, 66), (-17, 66),
     (-20, 66), (-22, 65), (-22, 64)],
    [(80, 6), (81, 7), (82, 8), (81, 9), (80, 9), (79, 8), (80, 6)],
    [(120, 22), (121, 23), (122, 25), (121, 25), (120, 23), (120, 22)],
    [(120, 14), (121, 15), (122, 16), (122, 18), (121, 18), (120, 16),
     (120, 14)],
    [(-85, 22), (-82, 23), (-80, 23), (-77, 21), (-74, 20), (-77, 20),
     (-80, 22), (-83, 22), (-85, 22)],
    [(-74, 19), (-72, 19), (-70, 18), (-68, 18), (-70, 19), (-73, 19),
     (-74, 19)],
]


def point_in_polygon(x, y, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > y) != (yj > y):
            xinters = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < xinters:
                inside = not inside
        j = i
    return inside


def draw_map(d, x0, y0, mw, mh):
    """Dotted world map, equirectangular lon -180..180, lat -58..84."""
    lon0, lon1, lat0, lat1 = -180, 180, -58, 84

    def px(lon, lat):
        return (x0 + (lon - lon0) / (lon1 - lon0) * mw,
                y0 + (lat1 - lat) / (lat1 - lat0) * mh)

    step = 4
    dot = (150, 140, 110)
    for gy in range(y0 + 2, y0 + mh, step):
        for gx in range(x0 + 2, x0 + mw, step):
            lon = lon0 + (gx - x0) / mw * (lon1 - lon0)
            lat = lat1 - (gy - y0) / mh * (lat1 - lat0)
            for poly in CONTINENTS:
                if point_in_polygon(lon, lat, poly):
                    d.ellipse([gx - 1.2, gy - 1.2, gx + 1.2, gy + 1.2], fill=dot)
                    break
    # pins, jittering clusters that share a spot
    groups = {}
    for num, la, lo in PIN_POINTS:
        key = (round(la * 2) / 2, round(lo * 2) / 2)
        groups.setdefault(key, []).append((num, la, lo))
    fnum = F(SANS_B, 7)
    for key, items in groups.items():
        n = len(items)
        for i, (num, la, lo) in enumerate(items):
            cx, cy = px(lo, la)
            if n > 1:
                ang = -math.pi / 2 + i * 2 * math.pi / n
                r = 16 if n >= 4 else 13
                cx += r * math.cos(ang)
                cy += r * math.sin(ang)
            d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED,
                      outline=(255, 255, 255), width=1)
            d.text((cx, cy), str(num), font=fnum, fill=(255, 255, 255),
                   anchor="mm")
    return px


# ---------------------------------------------------------------- art panels
def art_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(178, 205, 222))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(120, 90, 60))
    # table
    d.rectangle([x + 18, y + h - 52, x + w - 18, y + h - 26], fill=(96, 68, 44))
    # delegates: coloured flags + heads along the table
    cols = [(179, 35, 42), (29, 78, 216), (21, 128, 61), (217, 119, 6),
            (124, 58, 237)]
    for i, c in enumerate(cols):
        cx = x + 64 + i * 40
        d.rectangle([cx - 9, y + h - 74, cx + 9, y + h - 52], fill=c)
        d.ellipse([cx - 8, y + h - 88, cx + 8, y + h - 74], fill=(232, 200, 170))
    # document with a red cross (the unadopted text)
    dx, dy = x + w - 92, y + 16
    d.rectangle([dx, dy, dx + 72, dy + 52], fill=(255, 255, 255),
                outline=(120, 120, 120))
    for ly in range(dy + 10, dy + 40, 7):
        d.line([dx + 8, ly, dx + 64, ly], fill=(170, 170, 170), width=2)
    d.line([dx + 8, dy + 8, dx + 64, dy + 44], fill=RED, width=5)
    d.line([dx + 64, dy + 8, dx + 8, dy + 44], fill=RED, width=5)
    # clock (03:00 objections)
    ccx, ccy = x + 28, y + 38
    d.ellipse([ccx - 12, ccy - 12, ccx + 12, ccy + 12], fill=(255, 255, 255),
              outline=NAVY, width=2)
    d.line([ccx, ccy, ccx, ccy - 8], fill=NAVY, width=2)
    d.line([ccx, ccy, ccx + 6, ccy], fill=NAVY, width=2)


def art_bahrain(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 48))
    for sx, sy in [(30, 18), (90, 10), (150, 22), (210, 12), (260, 20), (300, 14)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
    # sea
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(24, 52, 90))
    # radar dishes
    for bx in (x + 60, x + 210):
        d.line([bx, y + h - 22, bx + 26, y + h - 62], fill=(200, 200, 200), width=3)
        d.arc([bx + 2, y + h - 78, bx + 50, y + h - 40], 180, 360,
              fill=(220, 220, 220), width=4)
    # missile arcs (dashed orange)
    for (ax, ay, bx, by) in [(x + 20, y + 30, x + 90, y + h - 50),
                             (x + 130, y + 22, x + 230, y + h - 56)]:
        steps = 14
        for i in range(steps):
            t0, t1 = i / steps, (i + 0.55) / steps
            x0 = ax + (bx - ax) * t0
            y0 = ay + (by - ay) * t0 - 26 * math.sin(math.pi * t0)
            x1 = ax + (bx - ax) * t1
            y1 = ay + (by - ay) * t1 - 26 * math.sin(math.pi * t1)
            d.line([x0, y0, x1, y1], fill=(255, 150, 40), width=2)
    # explosion bursts at the dishes
    for bx, by in [(x + 88, y + h - 58), (x + 238, y + h - 62)]:
        for ang in range(0, 360, 45):
            ex = bx + 12 * math.cos(math.radians(ang))
            ey = by + 12 * math.sin(math.radians(ang))
            d.line([bx, by, ex, ey], fill=(255, 180, 60), width=2)
        d.ellipse([bx - 5, by - 5, bx + 5, by + 5], fill=(255, 200, 80))


def art_ukraine(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 48))
    for sx, sy in [(24, 14), (80, 24), (140, 10), (200, 20), (260, 12), (300, 26)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(255, 255, 255))
    # drones (small X silhouettes)
    for dx, dy in [(x + 60, y + 26), (x + 170, y + 18), (x + 260, y + 34),
                   (x + 120, y + 44)]:
        d.line([dx - 6, dy - 6, dx + 6, dy + 6], fill=(255, 200, 90), width=2)
        d.line([dx - 6, dy + 6, dx + 6, dy - 6], fill=(255, 200, 90), width=2)
    # apartment block, damaged, with lit windows
    bx, by, bw, bh = x + 30, y + h - 78, 120, 78
    d.rectangle([bx, by, bx + bw, by + bh], fill=(90, 95, 105))
    d.polygon([(bx + bw, by), (bx + bw + 26, by + 14), (bx + bw, by + 30)],
              fill=(60, 64, 72))
    for r in range(4):
        for c in range(5):
            wx = bx + 10 + c * 22
            wy = by + 10 + r * 18
            lit = (r + c) % 3 != 0
            d.rectangle([wx, wy, wx + 12, wy + 10],
                        fill=(255, 210, 110) if lit else (50, 54, 62))
    # searchlight beam
    d.polygon([(x + w - 40, y + h), (x + w - 90, y + 20), (x + w - 60, y + 20)],
              fill=(255, 240, 180))
    # ground
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(40, 44, 54))


def art_mid(d, kind, x, y, w, h):
    """Small art strip for a mid card."""
    if kind == "chart":  # Nvidia: falling red chart
        d.rectangle([x, y, x + w, y + h], fill=(24, 24, 34))
        pts = [(x + 8, y + 10), (x + 40, y + 14), (x + 70, y + 12),
               (x + 100, y + 22), (x + 130, y + 20), (x + 160, y + 32),
               (x + w - 8, y + h - 6)]
        d.line(pts, fill=(255, 80, 80), width=3, joint="curve")
        d.text((x + 8, y + h - 16), "$", font=F(SANS_B, 14), fill=(255, 120, 120))
    elif kind == "ipo":  # Anthropic: bell + bars
        d.rectangle([x, y, x + w, y + h], fill=(20, 32, 54))
        d.polygon([(x + 30, y + 8), (x + 58, y + 8), (x + 62, y + 26),
                   (x + 26, y + 26)], fill=(212, 175, 55))
        d.rectangle([x + 24, y + 26, x + 64, y + 30], fill=(212, 175, 55))
        d.ellipse([x + 40, y + 30, x + 48, y + 36], fill=(212, 175, 55))
        for i, bh in enumerate([10, 18, 8, 22]):
            d.rectangle([x + 90 + i * 22, y + h - 6 - bh,
                         x + 104 + i * 22, y + h - 6],
                        fill=(120, 200, 120) if i % 2 == 0 else (220, 90, 90))
    elif kind == "capitol":  # Van Hollen: dome
        d.rectangle([x, y, x + w, y + h], fill=(26, 43, 74))
        d.rectangle([x + 20, y + h - 10, x + w - 20, y + h - 6], fill=(220, 220, 220))
        d.rectangle([x + 40, y + h - 20, x + w - 40, y + h - 10], fill=(220, 220, 220))
        d.pieslice([x + 70, y + 2, x + w - 70, y + 34], 180, 360, fill=(235, 235, 235))
        d.rectangle([x + 60, y + h - 30, x + w - 60, y + h - 20], fill=(200, 200, 200))
    elif kind == "cricket":  # India: bat, ball, stumps on green
        d.rectangle([x, y, x + w, y + h], fill=(34, 110, 60))
        d.rectangle([x, y + h - 12, x + w, y + h], fill=(210, 190, 140))
        for sx in (x + 60, x + 66, x + 72):
            d.line([sx, y + h - 12, sx, y + h - 26], fill=(240, 230, 180), width=2)
        d.line([x + 120, y + 6, x + 150, y + 30], fill=(220, 190, 140), width=7)
        d.ellipse([x + 160, y + 30, x + 172, y + 42], fill=(255, 255, 255),
                  outline=(180, 40, 40), width=1)
    elif kind == "race":  # Verstappen: red car on track
        d.rectangle([x, y, x + w, y + h], fill=(30, 30, 40))
        d.rectangle([x, y + h - 12, x + w, y + h], fill=(60, 60, 70))
        for cx in range(x + 6, x + w - 6, 18):
            d.rectangle([cx, y + h - 12, cx + 9, y + h - 9],
                        fill=(255, 255, 255) if (cx // 18) % 2 == 0 else (20, 20, 20))
        d.polygon([(x + 40, y + h - 14), (x + 60, y + 14), (x + 120, y + 12),
                   (x + 150, y + h - 14)], fill=(200, 30, 30))
        d.ellipse([x + 58, y + h - 20, x + 74, y + h - 6], fill=(15, 15, 15))
        d.ellipse([x + 118, y + h - 20, x + 134, y + h - 6], fill=(15, 15, 15))
    elif kind == "power":  # Iran: pylon + dark city
        d.rectangle([x, y, x + w, y + h], fill=(28, 28, 40))
        d.polygon([(x + 90, y + 4), (x + 80, y + h - 6), (x + 100, y + h - 6)],
                  fill=(120, 120, 130))
        d.line([x + 78, y + 12, x + 102, y + 12], fill=(120, 120, 130), width=2)
        d.line([x, y + 16, x + 78, y + 10], fill=(150, 150, 150), width=1)
        d.line([x + 102, y + 10, x + w, y + 18], fill=(150, 150, 150), width=1)
        for bx in (x + 14, x + 34, x + 150, x + 168):
            d.rectangle([bx, y + h - 18, bx + 12, y + h - 6], fill=(50, 50, 64))
            d.rectangle([bx + 3, y + h - 15, bx + 6, y + h - 12], fill=(90, 90, 90))
    elif kind == "ship":  # Sparta II: ship + flames
        d.rectangle([x, y, x + w, y + h], fill=(24, 52, 90))
        d.rectangle([x, y + h - 14, x + w, y + h], fill=(18, 38, 66))
        d.polygon([(x + 30, y + h - 14), (x + 160, y + h - 14), (x + 150, y + h - 24),
                   (x + 42, y + h - 24)], fill=(60, 64, 72))
        d.rectangle([x + 110, y + h - 38, x + 140, y + h - 24], fill=(90, 94, 104))
        for fx, fh in [(x + 60, 16), (x + 80, 22), (x + 100, 14), (x + 125, 18)]:
            d.polygon([(fx - 6, y + h - 24), (fx, y + h - 24 - fh),
                       (fx + 6, y + h - 24)], fill=(255, 140, 30))
        d.ellipse([x + 150, y + 6, x + 185, y + 22], fill=(180, 180, 180))
    elif kind == "ballot":  # Hong Kong: ballot box + tick
        d.rectangle([x, y, x + w, y + h], fill=(140, 30, 36))
        d.rectangle([x + 60, y + 12, x + 130, y + h - 8], fill=(240, 235, 220))
        d.rectangle([x + 80, y + 8, x + 110, y + 14], fill=(255, 255, 255),
                    outline=(120, 120, 120))
        d.line([x + 70, y + 26, x + 82, y + 34, x + 100, y + 16],
               fill=(21, 128, 61), width=4, joint="curve")
    elif kind == "hospital":  # Bolsonaro: cross + ECG
        d.rectangle([x, y, x + w, y + h], fill=(235, 240, 245))
        d.rectangle([x + 24, y + 8, x + 40, y + 34], fill=(179, 35, 42))
        d.rectangle([x + 16, y + 16, x + 48, y + 26], fill=(179, 35, 42))
        d.line([(x + 70, y + 22), (x + 90, y + 22), (x + 98, y + 12),
                (x + 106, y + 32), (x + 114, y + 22), (x + 150, y + 22),
                (x + 158, y + 14), (x + 166, y + 22), (x + 182, y + 22)],
               fill=(26, 43, 74), width=2, joint="curve")
    elif kind == "talks":  # Gaza: table with two flags
        d.rectangle([x, y, x + w, y + h], fill=(178, 205, 222))
        d.rectangle([x + 30, y + h - 16, x + w - 30, y + h - 10], fill=(96, 68, 44))
        for fx, col in [(x + 60, (21, 128, 61)), (x + 120, (240, 240, 240))]:
            d.line([fx, y + 8, fx, y + h - 16], fill=(90, 90, 90), width=2)
            d.polygon([(fx, y + 8), (fx + 22, y + 13), (fx, y + 18)], fill=col)
        d.ellipse([x + 88, y + h - 26, x + 104, y + h - 14], fill=(255, 255, 255))
        d.ellipse([x + 92, y + h - 24, x + 100, y + h - 16], fill=(21, 128, 61))

ART = {"cop31": art_cop31, "bahrain": art_bahrain, "ukraine": art_ukraine}

# ---------------------------------------------------------------- build page
def build():
    press = datetime.now(timezone.utc).strftime("%H:%M")
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- top bar
    d.rectangle([0, 0, W, 24], fill=NAVY)
    d.text((M, 6), "THE WORLD IN ONE DAY", font=F(SANS_B, 11), fill=(255, 255, 255))
    right = "37 STORIES  ·  6 REGIONS  ·  EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    d.text((W - M, 6), right, font=F(SANS_B, 11), fill=(255, 255, 255), anchor="ra")

    # ---- masthead
    centre(d, W // 2, 28, "Sunday 22 November 2026", F(SERIF_B, 56), NAVY)
    centre(d, W // 2, 88,
           "COP31 ends with no deal  ·  Iran claims radar hits in Bahrain  ·  "
           "Russia sends 186 drones at Ukraine",
           F(SERIF_I, 15), RED)
    d.line([M, 108, W - M, 108], fill=RULE, width=2)

    # ---- stats strip
    col_w = (W - 2 * M) / 6
    for i, (num, lab) in enumerate(STATS):
        cx = M + col_w * i
        centre(d, cx + col_w / 2, 114, num, F(SERIF_B, 27), RED)
        draw_wrapped(d, cx + 8, 142, lab, F(SANS, 9), MUTED, col_w - 16, 11,
                     max_lines=2)
    d.line([M, 166, W - M, 166], fill=CARD_LINE, width=1)

    # ---- region bar
    total = sum(c for _k, _l, c in REGION_LABELS)
    bx = M
    bar_w = W - 2 * M
    for key, label, count in REGION_LABELS:
        seg = bar_w * count / total
        d.rectangle([bx, 172, bx + seg - 1, 186], fill=REGION_COLOURS[key])
        txt = f"{label} {count}" if seg > 60 else f"{key} {count}"
        centre(d, bx + seg / 2, 175, txt, F(SANS_B, 8), (255, 255, 255))
        bx += seg

    # ---- UTC timeline
    d.rectangle([M, 192, W - M, 210], fill=NAVY)
    d.text((M + 8, 196), TIMELINE, font=F(SANS_B, 10), fill=(255, 255, 255))

    # ---- heroes
    hero_w = 322
    hero_x = [M, M + hero_w + 10, M + 2 * (hero_w + 10)]
    hy = 216
    art_h = 104
    for h, x in zip(HEROES, hero_x):
        ART[h["art"]](d, x, hy, hero_w, art_h)
        tag_chip(d, x + 6, hy + 6, h["tag"], F(SANS_B, 10))
        y = hy + art_h + 6
        d.text((x, y), f"{h['num']}  {h['city']} · {h['cat']}",
               font=F(SANS_B, 10), fill=RED)
        cert_w = F(SANS_B, 9).getlength(h["cert"]) + 10
        d.rectangle([x + hero_w - cert_w, y - 1, x + hero_w, y + 12],
                    outline=MUTED, width=1)
        d.text((x + hero_w - cert_w / 2, y + 1), h["cert"],
               font=F(SANS_B, 9), fill=MUTED, anchor="ma")
        y += 16
        _n, y = draw_wrapped(d, x, y, h["head"], F(SERIF_B, 17), INK,
                             hero_w, 20, max_lines=2)
        y += 2
        _n, y = draw_wrapped(d, x, y, h["body"], F(SERIF, 11), INK,
                             hero_w, 13, max_lines=5)

    # ---- mids (5 x 2)
    mid_w = 191
    mid_x = [M + i * (mid_w + 8) for i in range(5)]
    my = 448
    row_h = 106
    for r in range(2):
        for c in range(5):
            m = MIDS[r * 5 + c]
            x = mid_x[c]
            y = my + r * row_h
            art_mid(d, m["art"], x, y, mid_w, 40)
            tag_chip(d, x + 5, y + 5, m["tag"], F(SANS_B, 8))
            yy = y + 44
            d.text((x, yy), f"{m['num']}  {m['city']} · {m['cat']}",
                   font=F(SANS_B, 8), fill=RED)
            yy += 12
            _n, yy = draw_wrapped(d, x, yy, m["head"], F(SERIF_B, 12), INK,
                                  mid_w, 14, max_lines=2)
            _n, yy = draw_wrapped(d, x, yy, m["body"], F(SANS, 9), INK,
                                  mid_w, 11, max_lines=2)

    # ---- bottom: map + briefs
    by = 668
    d.text((M, by), "WHERE IT HAPPENED", font=F(SANS_B, 11), fill=NAVY)
    d.text((M + 150, by), "pins match story numbers",
           font=F(SANS_I, 10) if False else F(SERIF_I, 10), fill=MUTED)
    d.text((472, by), "ALSO ON SUNDAY 22 NOVEMBER — 24 MORE STORIES",
           font=F(SANS_B, 11), fill=NAVY)
    map_x, map_y, map_w, map_h = M, by + 18, 440, 240
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h],
                fill=(250, 247, 240), outline=CARD_LINE, width=1)
    draw_map(d, map_x + 4, map_y + 4, map_w - 8, map_h - 8)

    # briefs in two columns
    bx0, bw = 472, 268
    fnum = F(SANS_B, 9)
    fbr = F(SANS, 9)
    for i, (num, city, text, _la, _lo) in enumerate(BRIEFS):
        col = i // 12
        row = i % 12
        x = bx0 + col * (bw + 6)
        y = map_y + row * 20
        d.text((x, y), str(num), font=fnum, fill=RED)
        lines, _ = draw_wrapped(d, x + 20, y, f"{city} — {text}", fbr, INK,
                                bw - 20, 10, max_lines=2)

    # ---- DATE CHECK
    dy = 928
    d.rectangle([M, dy, W - M, dy + 62], fill=DATE_BG, outline=DATE_LINE, width=2)
    _n, _y = draw_wrapped(d, M + 8, dy + 5, DATE_CHECK, F(SANS, 9), INK,
                          W - 2 * M - 16, 11, max_lines=5)

    # ---- sources footer
    fy = 996
    d.text((M, fy), SOURCES, font=F(SANS, 8), fill=MUTED)
    d.text((M, fy + 10), LEGEND, font=F(SANS, 8), fill=MUTED)

    # ---- bottom bar
    d.rectangle([0, H - 22, W, H], fill=NAVY)
    d.text((M, H - 17), "THE WORLD IN ONE DAY", font=F(SANS_B, 9),
           fill=(255, 255, 255))
    d.text((W - M, H - 17),
           f"SUNDAY 22 NOVEMBER 2026  ·  ONE PAGE  ·  PRESS {press} UTC",
           font=F(SANS_B, 9), fill=(255, 255, 255), anchor="ra")
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = build()
    img.save(out, optimize=True)
    data = open(out, "rb").read()
    print(f"wrote {out}: {img.size[0]}x{img.size[1]}, {len(data)} bytes, "
          f"sha256 {hashlib.sha256(data).hexdigest()}")


if __name__ == "__main__":
    main()
