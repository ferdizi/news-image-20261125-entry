#!/usr/bin/env python3
"""THE WEDNESDAY WORLD - 25 November 2026 in one image.

Draws entry.png (1024x1024, deterministic) with Pillow + system fonts.
No network, no system time, no randomness: two runs are byte-identical.
Run:  python3 render.py   -> writes entry.png next to this file.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 241, 227)
INK = (25, 23, 19)
MUTED = (90, 84, 72)
RULE = (25, 23, 19)
RED = (163, 22, 33)
TAG_BG = (255, 214, 90)
TAG_INK = (60, 40, 0)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def ctext(d, cx, y, text, fnt, fill=INK):
    d.text((cx - d.textlength(text, font=fnt) / 2, y), text, font=fnt, fill=fill)


def rtext(d, x, y, text, fnt, fill=INK):
    d.text((x, y), text, font=fnt, fill=fill)


def tag(d, x, y, label, fnt):
    """Small yellow claim tag; returns width used."""
    tw = d.textlength(label, font=fnt)
    pad = 4
    d.rounded_rectangle([x, y, x + tw + pad * 2, y + 13], radius=3,
                        fill=TAG_BG, outline=(180, 140, 20), width=1)
    d.text((x + pad, y + 1), label, font=fnt, fill=TAG_INK)
    return tw + pad * 2 + 3


# ---------------------------------------------------------------- stories
# tag: CONFIRMED = verified by a named outlet; REPORTED = as claimed.
HEROES = [
    dict(num="1", kicker="STRAIT OF HORMUZ",
         head="TWO TANKERS HIT MINES, BURN IN HORMUZ",
         deck="IRGC: tankers hit mines on an unauthorised route; engine rooms on fire.",
         scene="tanker", bar=(163, 22, 33), tag="REPORTED", src="Reuters"),
    dict(num="2", kicker="CANBERRA",
         head="SOLOMONS SIGN TREATY WITH AUSTRALIA",
         deck="No foreign base, ever; $740m over a decade. China pact dropped.",
         scene="treaty", bar=(15, 118, 110), tag="CONFIRMED", src="PM of Australia"),
    dict(num="3", kicker="SEOUL",
         head="KOSPI PLUNGES 6.16% IN AI ROUT",
         deck="Index closes at 4,697.51, lowest since January. Samsung -9.9%, SK Hynix -11.1%.",
         scene="chart", bar=(11, 93, 138), tag="CONFIRMED", src="Korea Exchange"),
]

# (number, name, colour, icon-scene, [ (line, tag, source), ... ])
REGIONS = [
    (1, "MIDDLE EAST", (140, 29, 24), "tower", [
        ("Houthi drone hits Riyadh tower; 11 hurt", "CONFIRMED", "Saudi Civil Defense"),
        ("Houthis say they hit Ras Tanura refinery", "REPORTED", "Houthi spokesman"),
        ("Israel kills Hamas colonel Abuelouf + family", "REPORTED", "Gaza medics"),
        ("Iran warns ships: coordinate Hormuz passage", "REPORTED", "IRGC Navy"),
    ]),
    (2, "EASTERN EUROPE", (11, 93, 138), "refinery", [
        ("Ukraine drones hit two Rosneft refineries; 1 killed", "REPORTED", "Kyiv"),
        ("Russian strike on Odesa kills 2, injures 3 incl. child", "CONFIRMED", "Odesa governor"),
        ("Zelensky: Ukraine needs \u20ac115bn foreign aid for 2027", "CONFIRMED", "Kyiv"),
    ]),
    (3, "EAST ASIA", (91, 45, 142), "rocket", [
        ("Shenzhou-24 docks; Pakistani Ali first foreigner aboard", "CONFIRMED", "Xinhua"),
        ("Nikkei -2.78% as SoftBank sinks 14.8%", "CONFIRMED", "AP"),
        ("Taiex -5% as TSMC slides", "CONFIRMED", "AP"),
        ("Qianfan: China's answer to Starlink", "REPORTED", "The Diplomat"),
    ]),
    (4, "SOUTH & SE ASIA", (29, 122, 61), "cricket", [
        ("Sooryavanshi, 15, smashes 204 off 53 balls, 28 sixes", "CONFIRMED", "Reuters"),
        ("Bogor mine flood toll rises to 6; ~20 miners trapped", "CONFIRMED", "AP"),
        ("SE Asia on US tariff list: Vietnam, Indonesia, Thailand", "CONFIRMED", "USTR"),
    ]),
    (5, "AFRICA", (176, 111, 0), "cross", [
        ("WHO evacuates Ebola teams from Akwe hospital after 3 days", "CONFIRMED", "WHO"),
        ("RSF drone strikes kill 19 civilians in Sudan", "REPORTED", "Emergency Lawyers"),
        ("CAS restores Senegal's AFCON title; Morocco to appeal", "CONFIRMED", "CAS"),
        ("UN: AIDS funding cuts threaten decades of progress", "CONFIRMED", "UN"),
    ]),
    (6, "NORTH AMERICA", (20, 70, 160), "gavel", [
        ("US jury convicts Huawei on 10 of 12 counts", "CONFIRMED", "Reuters"),
        ("Trump proposes tariffs on 14 partners; China 20%, EU 15%", "CONFIRMED", "USTR"),
        ("Dow closes above 50,000 for the first time", "CONFIRMED", "NYSE"),
        ("Abrego Garcia leaves US for Spain after 20-month fight", "CONFIRMED", "AP"),
    ]),
    (7, "MARKETS & TECH", (15, 118, 110), "chip", [
        ("Dell record Q3: revenue $54.9bn, +103% on AI servers", "CONFIRMED", "Dell"),
        ("Nvidia slides 8.5% as Nasdaq drops 3.8% on Wednesday", "CONFIRMED", "CNN"),
        ("Anthropic sinks 7%, shares below IPO price", "CONFIRMED", "CNN"),
    ]),
    (8, "DEFENCE", (74, 74, 74), "ship", [
        ("Ukraine claims sea-drone hit on corvette off Benghazi", "REPORTED", "Kyiv"),
        ("490,334 Russian soldiers dead since 2022", "REPORTED", "BBC"),
        ("Poland seeks permanent US military presence", "CONFIRMED", "Warsaw"),
    ]),
    (9, "WESTERN EUROPE", (124, 45, 18), "euro", [
        ("Eurozone inflation rises to 4.0%", "CONFIRMED", "Eurostat"),
        ("EasyJet profit falls 89% as fuel costs soar", "CONFIRMED", "EasyJet"),
        ("Roche breast-cancer drug wins 2nd FDA approval", "CONFIRMED", "Roche"),
    ]),
    (10, "LATIN AMERICA", (157, 23, 77), "shop", [
        ("Colombia frees all hostages in Cartagena supermarket siege", "CONFIRMED", "AP"),
        ("Car bomb hits governor's office in Villavicencio", "CONFIRMED", "Al Jazeera"),
        ("Brazil seeks WTO panel over US Section 301 duties", "CONFIRMED", "WTO"),
        ("Mexico to try 'El Chapo Isidro' despite US request", "CONFIRMED", "Al Jazeera"),
    ]),
]

STATS = ["KOSPI -6.16%", "DOW 50,018.70", "2 TANKERS BURN",
         "$740M PACT", "11,762 EBOLA CASES", "204 OFF 53"]

TIMELINE = [
    ("TUE 24 NOV", "Sooryavanshi 204 off 53"),
    ("TUE 24 NOV", "CAS restores Senegal title"),
    ("TUE 24 NOV", "Huawei convicted"),
    ("00:18 UTC", "Shenzhou-24 launches"),
    ("03:56 UTC", "Shenzhou-24 docks"),
    ("06:30 UTC", "Kospi closes down 6.16%"),
]

ALSO_TODAY = ("ALSO TODAY \u2014 COP31 talks collapse as oil states block fossil-fuel phaseout"
               " \u00b7 Pope Leo XIV laments the failure \u00b7 Amazon buys Decart to chase Nvidia")

DATE_CHECK = ("DATE CHECK \u2014 LEFT OUT (OTHER DAYS): ICJ finds Myanmar guilty of genocide, "
              "Thu 19 Nov \u00b7 Nvidia's Huang returns as CEO, Mon 23 Nov \u00b7 "
              "Tanker strikes off Khasab, Fri 20\u2013Sat 21 Nov.")

FOOTER = ("Every story above happened or was first reported on 24\u201325 November 2026. "
          "REPORTED = as claimed, not independently confirmed. "
          "All scenes are drawn illustrations, not photographs.")

# ---------------------------------------------------------------- scenes
# Every scene is a small flat illustration drawn with primitives only.

def scene_tanker(d, x, y, w, h):
    sky = (214, 232, 240)
    d.rectangle([x, y, x + w, y + h], fill=sky)
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(38, 90, 130))
    for i in range(5):  # waves
        wx = x + 8 + i * (w - 16) / 5
        d.arc([wx, y + h * 0.66, wx + 26, y + h * 0.80], 0, 180,
              fill=(220, 240, 248), width=3)
    d.polygon([(x + w * 0.12, y + h * 0.58), (x + w * 0.88, y + h * 0.58),
               (x + w * 0.80, y + h * 0.42), (x + w * 0.20, y + h * 0.42)],
              fill=(30, 30, 34))
    for i, c in enumerate(((200, 60, 40), (40, 120, 90), (220, 150, 40))):
        cx = x + w * (0.28 + i * 0.22)
        d.rectangle([cx, y + h * 0.28, cx + w * 0.16, y + h * 0.42], fill=c)
    for fx, fs in ((0.30, 1.0), (0.72, 0.8)):  # flames
        fx0 = x + w * fx
        fy0 = y + h * 0.30
        s = h * 0.16 * fs
        d.polygon([(fx0 - s, fy0), (fx0, fy0 - s * 1.6), (fx0 + s, fy0)],
                  fill=(240, 120, 20))
        d.polygon([(fx0 - s * 0.55, fy0), (fx0, fy0 - s), (fx0 + s * 0.55, fy0)],
                  fill=(255, 210, 60))
    for sx, sy, sr in ((0.22, 0.12, 9), (0.30, 0.07, 12), (0.80, 0.10, 10)):
        d.ellipse([x + w * sx - sr, y + h * sy - sr, x + w * sx + sr,
                   y + h * sy + sr], fill=(120, 120, 120))


def scene_treaty(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 238, 226))
    d.rectangle([x + w * 0.08, y + h * 0.12, x + w * 0.46, y + h * 0.62],
                fill=(0, 40, 90), outline=(255, 255, 255), width=2)
    for sx, sy in ((0.16, 0.24), (0.30, 0.20), (0.38, 0.42), (0.20, 0.50)):
        d.ellipse([x + w * sx - 3, y + h * sy - 3, x + w * sx + 3,
                   y + h * sy + 3], fill=(255, 255, 255))
    d.polygon([(x + w * 0.54, y + h * 0.12), (x + w * 0.92, y + h * 0.12),
               (x + w * 0.92, y + h * 0.62), (x + w * 0.54, y + h * 0.62)],
              fill=(0, 90, 60))
    d.polygon([(x + w * 0.54, y + h * 0.12), (x + w * 0.92, y + h * 0.62),
               (x + w * 0.92, y + h * 0.12), (x + w * 0.54, y + h * 0.62)],
              fill=(255, 210, 0))
    for sx, sy in ((0.66, 0.26), (0.80, 0.34), (0.70, 0.48)):
        d.ellipse([x + w * sx - 3, y + h * sy - 3, x + w * sx + 3,
                   y + h * sy + 3], fill=(255, 255, 255))
    d.rectangle([x + w * 0.18, y + h * 0.70, x + w * 0.82, y + h * 0.92],
                fill=(255, 255, 255), outline=(120, 110, 90), width=2)
    d.line([x + w * 0.24, y + h * 0.78, x + w * 0.76, y + h * 0.78],
           fill=(150, 140, 120), width=2)
    d.line([x + w * 0.24, y + h * 0.86, x + w * 0.60, y + h * 0.86],
           fill=(150, 140, 120), width=2)
    d.line([x + w * 0.60, y + h * 0.72, x + w * 0.72, y + h * 0.90],
           fill=(163, 22, 33), width=3)


def scene_chart(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 244, 240))
    gx, gy, gw, gh = x + w * 0.10, y + h * 0.12, w * 0.80, h * 0.66
    for i in range(4):
        ly = gy + gh * i / 3
        d.line([gx, ly, gx + gw, ly], fill=(220, 210, 200), width=1)
    pts = [(gx + gw * i / 6, gy + gh * (0.10 + f * 0.75))
           for i, f in enumerate((0.0, 0.15, 0.10, 0.45, 0.60, 0.85, 1.0))]
    d.line(pts, fill=(200, 30, 30), width=4, joint="curve")
    d.ellipse([pts[-1][0] - 5, pts[-1][1] - 5, pts[-1][0] + 5, pts[-1][1] + 5],
              fill=(200, 30, 30))
    d.text((x + w * 0.52, y + h * 0.80), "-6.16%",
           font=font(SANS_B, int(h * 0.16)), fill=(200, 30, 30))


def scene_tower(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 240))
    d.rectangle([x + w * 0.38, y + h * 0.22, x + w * 0.58, y + h * 0.92],
                fill=(70, 90, 120))
    for i in range(5):
        wy = y + h * (0.30 + i * 0.12)
        d.rectangle([x + w * 0.42, wy, x + w * 0.54, wy + h * 0.06],
                    fill=(255, 220, 120))
    d.polygon([(x + w * 0.36, y + h * 0.22), (x + w * 0.48, y + h * 0.08),
               (x + w * 0.60, y + h * 0.22)], fill=(50, 70, 100))
    d.ellipse([x + w * 0.66, y + h * 0.10, x + w * 0.86, y + h * 0.26],
              fill=(60, 60, 60))
    d.line([x + w * 0.70, y + h * 0.18, x + w * 0.82, y + h * 0.18],
           fill=(200, 200, 200), width=2)
    d.line([x + w * 0.76, y + h * 0.12, x + w * 0.76, y + h * 0.24],
           fill=(200, 200, 200), width=2)
    for ang in range(0, 360, 45):
        import math
        a = math.radians(ang)
        d.line([x + w * 0.76 + 10 * math.cos(a), y + h * 0.18 + 10 * math.sin(a),
                x + w * 0.76 + 16 * math.cos(a), y + h * 0.18 + 16 * math.sin(a)],
               fill=(240, 120, 20), width=3)


def scene_refinery(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 228, 210))
    d.rectangle([x + w * 0.10, y + h * 0.55, x + w * 0.90, y + h * 0.92],
                fill=(90, 80, 70))
    for tx in (0.18, 0.48, 0.76):
        d.rectangle([x + w * tx, y + h * 0.30, x + w * (tx + 0.10),
                     y + h * 0.55], fill=(120, 110, 100))
        d.polygon([(x + w * tx, y + h * 0.30), (x + w * (tx + 0.05),
                    y + h * 0.20), (x + w * (tx + 0.10), y + h * 0.30)],
                  fill=(150, 60, 40))
    for fx in (0.30, 0.66):
        fx0 = x + w * fx
        d.polygon([(fx0 - 10, y + h * 0.42), (fx0, y + h * 0.16),
                   (fx0 + 10, y + h * 0.42)], fill=(240, 120, 20))
        d.polygon([(fx0 - 5, y + h * 0.42), (fx0, y + h * 0.26),
                   (fx0 + 5, y + h * 0.42)], fill=(255, 210, 60))


def scene_rocket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 24, 48))
    for sx, sy in ((0.15, 0.15), (0.85, 0.20), (0.70, 0.10), (0.30, 0.30),
                   (0.90, 0.45), (0.12, 0.55)):
        d.ellipse([x + w * sx - 2, y + h * sy - 2, x + w * sx + 2,
                   y + h * sy + 2], fill=(255, 255, 255))
    cx = x + w * 0.5
    d.polygon([(cx - w * 0.10, y + h * 0.42), (cx, y + h * 0.10),
               (cx + w * 0.10, y + h * 0.42)], fill=(200, 30, 30))
    d.rectangle([cx - w * 0.10, y + h * 0.42, cx + w * 0.10, y + h * 0.68],
                fill=(235, 235, 235))
    d.ellipse([cx - w * 0.05, y + h * 0.30, cx + w * 0.05, y + h * 0.42],
              fill=(80, 160, 220), outline=(200, 30, 30), width=2)
    d.polygon([(cx - w * 0.10, y + h * 0.60), (cx - w * 0.20, y + h * 0.74),
               (cx - w * 0.10, y + h * 0.70)], fill=(200, 30, 30))
    d.polygon([(cx + w * 0.10, y + h * 0.60), (cx + w * 0.20, y + h * 0.74),
               (cx + w * 0.10, y + h * 0.70)], fill=(200, 30, 30))
    d.polygon([(cx - w * 0.07, y + h * 0.68), (cx, y + h * 0.92),
               (cx + w * 0.07, y + h * 0.68)], fill=(255, 160, 40))
    d.arc([x + w * 0.05, y + h * 0.78, x + w * 0.95, y + h * 1.25], 180, 360,
          fill=(90, 140, 200), width=6)


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(220, 240, 210))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(90, 160, 80))
    d.line([x + w * 0.5, y + h * 0.10, x + w * 0.62, y + h * 0.55],
           fill=(140, 100, 60), width=7)
    d.ellipse([x + w * 0.42, y + h * 0.06, x + w * 0.58, y + h * 0.20],
              fill=(220, 180, 140))
    d.line([x + w * 0.46, y + h * 0.20, x + w * 0.48, y + h * 0.55],
           fill=(40, 60, 120), width=8)
    d.line([x + w * 0.48, y + h * 0.55, x + w * 0.38, y + h * 0.78],
           fill=(40, 60, 120), width=7)
    d.line([x + w * 0.48, y + h * 0.55, x + w * 0.60, y + h * 0.76],
           fill=(40, 60, 120), width=7)
    d.ellipse([x + w * 0.78, y + h * 0.30, x + w * 0.86, y + h * 0.38],
              fill=(200, 30, 30))
    d.text((x + w * 0.06, y + h * 0.80), "204",
           font=font(SANS_B, int(h * 0.17)), fill=(25, 23, 19))


def scene_cross(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 242, 245))
    d.rectangle([x + w * 0.10, y + h * 0.45, x + w * 0.90, y + h * 0.92],
                fill=(255, 255, 255), outline=(120, 130, 140), width=2)
    d.polygon([(x + w * 0.10, y + h * 0.45), (x + w * 0.50, y + h * 0.28),
               (x + w * 0.90, y + h * 0.45)], fill=(200, 60, 50))
    d.rectangle([x + w * 0.44, y + h * 0.52, x + w * 0.56, y + h * 0.82],
                fill=(200, 40, 40))
    d.rectangle([x + w * 0.34, y + h * 0.62, x + w * 0.66, y + h * 0.72],
                fill=(200, 40, 40))
    d.ellipse([x + w * 0.70, y + h * 0.10, x + w * 0.86, y + h * 0.26],
              fill=(240, 200, 60))


def scene_gavel(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(236, 230, 214))
    d.rectangle([x + w * 0.14, y + h * 0.30, x + w * 0.62, y + h * 0.46],
                fill=(120, 80, 40))
    d.rectangle([x + w * 0.10, y + h * 0.24, x + w * 0.18, y + h * 0.52],
                fill=(90, 60, 30))
    d.rectangle([x + w * 0.58, y + h * 0.24, x + w * 0.66, y + h * 0.52],
                fill=(90, 60, 30))
    d.line([x + w * 0.62, y + h * 0.38, x + w * 0.88, y + h * 0.66],
           fill=(140, 100, 60), width=6)
    d.ellipse([x + w * 0.20, y + h * 0.68, x + w * 0.80, y + h * 0.86],
              fill=(90, 60, 30))


def scene_chip(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 236, 240))
    d.rectangle([x + w * 0.28, y + h * 0.28, x + w * 0.72, y + h * 0.72],
                fill=(30, 40, 60), outline=(180, 200, 210), width=2)
    d.rectangle([x + w * 0.42, y + h * 0.42, x + w * 0.58, y + h * 0.58],
                fill=(120, 200, 220))
    for i in range(4):
        px = x + w * (0.34 + i * 0.11)
        d.line([px, y + h * 0.16, px, y + h * 0.28], fill=(120, 130, 140),
               width=3)
        d.line([px, y + h * 0.72, px, y + h * 0.84], fill=(120, 130, 140),
               width=3)
        py = y + h * (0.34 + i * 0.11)
        d.line([x + w * 0.16, py, x + w * 0.28, py], fill=(120, 130, 140),
               width=3)
        d.line([x + w * 0.72, py, x + w * 0.84, py], fill=(120, 130, 140),
               width=3)
    d.line([x + w * 0.10, y + h * 0.88, x + w * 0.42, y + h * 0.88],
           fill=(200, 30, 30), width=3)
    d.polygon([(x + w * 0.42, y + h * 0.82), (x + w * 0.42, y + h * 0.94),
               (x + w * 0.52, y + h * 0.88)], fill=(200, 30, 30))


def scene_ship(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 236))
    d.rectangle([x, y + h * 0.66, x + w, y + h], fill=(40, 90, 130))
    d.polygon([(x + w * 0.18, y + h * 0.66), (x + w * 0.82, y + h * 0.66),
               (x + w * 0.72, y + h * 0.48), (x + w * 0.28, y + h * 0.48)],
              fill=(60, 60, 66))
    d.rectangle([x + w * 0.30, y + h * 0.34, x + w * 0.70, y + h * 0.48],
                fill=(160, 50, 40))
    d.line([x + w * 0.58, y + h * 0.34, x + w * 0.58, y + h * 0.14],
           fill=(60, 60, 66), width=3)
    d.polygon([(x + w * 0.58, y + h * 0.14), (x + w * 0.78, y + h * 0.22),
               (x + w * 0.58, y + h * 0.26)], fill=(200, 30, 30))
    for i in range(3):
        wx = x + w * (0.16 + i * 0.30)
        d.arc([wx, y + h * 0.70, wx + 24, y + h * 0.82], 0, 180,
              fill=(220, 240, 248), width=3)


def scene_euro(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 236, 244))
    d.ellipse([x + w * 0.18, y + h * 0.12, x + w * 0.82, y + h * 0.88],
              outline=(0, 40, 90), width=4)
    for i in range(8):
        import math
        a = math.radians(i * 45)
        sx = x + w * 0.50 + w * 0.26 * math.cos(a)
        sy = y + h * 0.50 + h * 0.30 * math.sin(a)
        d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 210, 0))
    d.text((x + w * 0.38, y + h * 0.36), "4.0%",
           font=font(SANS_B, int(h * 0.20)), fill=(0, 40, 90))


def scene_shop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 232, 220))
    d.rectangle([x + w * 0.10, y + h * 0.30, x + w * 0.90, y + h * 0.92],
                fill=(255, 255, 255), outline=(120, 110, 90), width=2)
    for i in range(4):
        ax = x + w * (0.10 + i * 0.20)
        d.polygon([(ax, y + h * 0.30), (ax + w * 0.10, y + h * 0.14),
                   (ax + w * 0.20, y + h * 0.30)],
                  fill=(200, 40, 40) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x + w * 0.40, y + h * 0.60, x + w * 0.60, y + h * 0.92],
                fill=(90, 130, 90))
    d.ellipse([x + w * 0.66, y + h * 0.08, x + w * 0.92, y + h * 0.34],
              fill=(40, 140, 80), outline=(255, 255, 255), width=2)
    d.line([x + w * 0.72, y + h * 0.21, x + w * 0.78, y + h * 0.27],
           fill=(255, 255, 255), width=3)
    d.line([x + w * 0.78, y + h * 0.27, x + w * 0.86, y + h * 0.15],
           fill=(255, 255, 255), width=3)


SCENES = dict(tanker=scene_tanker, treaty=scene_treaty, chart=scene_chart,
              tower=scene_tower, refinery=scene_refinery, rocket=scene_rocket,
              cricket=scene_cricket, cross=scene_cross, gavel=scene_gavel,
              chip=scene_chip, ship=scene_ship, euro=scene_euro,
              shop=scene_shop)

# ---------------------------------------------------------------- map
# Dotted world map: land spans per row on a 64 x 18 grid.
LAND = [
    (1, 4, 13), (2, 2, 15), (2, 29, 35), (2, 37, 55),
    (3, 2, 14), (3, 28, 35), (3, 36, 57),
    (4, 3, 12), (4, 28, 35), (4, 36, 57),
    (5, 4, 11), (5, 28, 35), (5, 35, 56),
    (6, 7, 10), (6, 28, 34), (6, 39, 45), (6, 46, 50),
    (7, 10, 14), (7, 28, 33), (7, 46, 51),
    (8, 10, 15), (8, 28, 32), (8, 47, 53),
    (9, 11, 14), (9, 29, 32),
    (10, 11, 14), (10, 49, 56),
    (11, 12, 13), (11, 49, 55),
    (12, 12, 12),
]
# region number -> (grid x, grid y) pin position
PINS = {1: (34, 5), 2: (32, 3), 3: (50, 4), 4: (44, 6), 5: (30, 8),
        6: (6, 4), 7: (12, 3), 8: (33, 4), 9: (29, 2), 10: (12, 9)}
REGION_COLORS = {n: c for n, _, c, _, _ in
                 [(r[0], r[1], r[2], r[3], r[4]) for r in REGIONS]}


def draw_map(d, x, y, w, h):
    cols, rows = 64, 18
    cw, ch = w / cols, h / rows
    for (r, x0, x1) in LAND:
        for gx in range(x0, x1 + 1):
            cx = x + (gx + 0.5) * cw
            cy = y + (r + 0.5) * ch
            d.ellipse([cx - 2.2, cy - 2.2, cx + 2.2, cy + 2.2],
                      fill=(120, 112, 96))
    for num, (gx, gy) in PINS.items():
        cx = x + (gx + 0.5) * cw
        cy = y + (gy + 0.5) * ch
        col = REGION_COLORS[num]
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=col,
                  outline=(255, 255, 255), width=2)
        t = str(num)
        d.text((cx - d.textlength(t, font=font(SANS_B, 11)) / 2, cy - 6),
               t, font=font(SANS_B, 11), fill=(255, 255, 255))


# ---------------------------------------------------------------- layout

def draw_masthead(d):
    ctext(d, W // 2, 4, "THE WEDNESDAY WORLD", font(SERIF, 54))
    ctext(d, W // 2, 64, "WEDNESDAY 25 NOVEMBER 2026", font(SERIF, 32))
    d.line([10, 102, W - 10, 102], fill=RULE, width=2)
    ctext(d, W // 2, 108,
          "THE WORLD IN ONE DAY \u2014 38 STORIES, 10 REGIONS, 13 SCENES",
          font(SANS_B, 14))


def draw_stats(d):
    y0, y1 = 126, 150
    d.line([10, y0, W - 10, y0], fill=RULE, width=1)
    d.line([10, y1, W - 10, y1], fill=RULE, width=1)
    colw = (W - 20) / len(STATS)
    for i, s in enumerate(STATS):
        cx = 10 + colw * (i + 0.5)
        ctext(d, cx, y0 + 5, s, font(SANS_B, 14))
        if i:
            d.line([10 + colw * i, y0 + 3, 10 + colw * i, y1 - 3],
                   fill=(180, 172, 156), width=1)


def draw_timeline(d):
    y0 = 154
    colw = (W - 20) / len(TIMELINE)
    for i, (t, txt) in enumerate(TIMELINE):
        x = 10 + colw * i + 4
        d.text((x, y0), t, font=font(SANS_B, 11), fill=RED)
        d.text((x, y0 + 13), txt, font=font(SANS, 11), fill=INK)
    d.line([10, 186, W - 10, 186], fill=RULE, width=1)


def draw_heroes(d):
    y0, ph, pw = 190, 200, 328
    for i, h in enumerate(HEROES):
        x = 10 + i * (pw + 10)
        d.rectangle([x, y0, x + pw, y0 + ph], fill=(255, 253, 247),
                    outline=INK, width=2)
        d.rectangle([x, y0, x + pw, y0 + 5], fill=h["bar"])
        SCENES[h["scene"]](d, x + 8, y0 + 11, pw - 16, 84)
        d.text((x + 10, y0 + 98), h["kicker"], font=font(SANS_B, 11),
               fill=h["bar"])
        lines = wrap(d, h["head"], font(SERIF, 19), pw - 20)
        ly = y0 + 112
        for ln in lines[:2]:
            d.text((x + 10, ly), ln, font=font(SERIF, 19), fill=INK)
            ly += 22
        dlines = wrap(d, h["deck"], font(SANS, 12), pw - 20)
        ly = y0 + 158
        for ln in dlines[:2]:
            d.text((x + 10, ly), ln, font=font(SANS, 12), fill=MUTED)
            ly += 14
        ty = y0 + ph - 15
        tw = tag(d, x + 10, ty, h["tag"], font(SANS_B, 9))
        src = "Source: " + h["src"]
        d.text((x + pw - 10 - d.textlength(src, font=font(SANS, 10)), ty + 1),
               src, font=font(SANS, 10), fill=MUTED)


def draw_regions(d):
    y0, rh, cw = 464, 88, 497
    for idx, (num, name, col, scene, lines) in enumerate(REGIONS):
        x = 10 + (idx % 2) * (cw + 10)
        y = y0 + (idx // 2) * rh
        d.ellipse([x + 2, y + 2, x + 24, y + 24], fill=col)
        t = str(num)
        d.text((x + 13 - d.textlength(t, font=font(SANS_B, 13)) / 2, y + 5),
               t, font=font(SANS_B, 13), fill=(255, 255, 255))
        d.text((x + 30, y + 4), name, font=font(SANS_B, 15), fill=col)
        d.line([x + 30, y + 22, x + cw - 4, y + 22], fill=col, width=1)
        SCENES[scene](d, x + 2, y + 26, 58, 58)
        lx = x + 66
        ly = y + 26
        for (text, tg, src) in lines:
            src_txt = " (" + src + ")"
            src_w = d.textlength(src_txt, font=font(SANS, 10))
            tag_w = 0
            if tg == "REPORTED":
                tag_w = d.textlength("REPORTED", font=font(SANS_B, 8)) + 11
            avail = cw - 66 - 6 - src_w - tag_w
            fnt = font(SANS, 12)
            wrapped = wrap(d, text, fnt, avail)
            line_txt = wrapped[0]
            d.text((lx, ly), line_txt, font=fnt, fill=INK)
            tx = lx + d.textlength(line_txt, font=fnt) + 3
            if tg == "REPORTED":
                tx += tag(d, tx, ly + 1, "REPORTED", font(SANS_B, 8))
            d.text((tx + 1, ly + 1), src_txt, font=font(SANS, 10),
                   fill=MUTED)
            ly += 15


def draw_bottom(d):
    y = 908
    d.line([10, y, W - 10, y], fill=RULE, width=1)
    d.text((10, y + 5), ALSO_TODAY, font=font(SANS, 12), fill=INK)
    d.rectangle([10, 932, W - 10, 972], outline=RED, width=2)
    dlines = wrap(d, DATE_CHECK, font(SANS_B, 11), W - 40)
    ly = 938
    for ln in dlines[:2]:
        d.text((16, ly), ln, font=font(SANS_B, 11), fill=RED)
        ly += 15
    ctext(d, W // 2, 980, FOOTER, font(SANS, 11), fill=MUTED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_stats(d)
    draw_timeline(d)
    draw_heroes(d)
    d.text((W - 10 - d.textlength("THE WORLD", font=font(SANS_B, 11)), 392),
           "THE WORLD", font=font(SANS_B, 11), fill=MUTED)
    draw_map(d, 10, 398, W - 20, 60)
    draw_regions(d)
    draw_bottom(d)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG")
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
